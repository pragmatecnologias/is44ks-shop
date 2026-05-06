from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.campaign import DiscoveryCampaign
from app.models.external_research import EvidenceCandidate, ExternalResearchJob
from app.models.portfolio import PortfolioItem, ProductCollection, ShopConcept
from app.models.product import Product
from app.models.product_validation import ProductDemandResearch, ProductTrendResearch, ProductValidationSummary
from app.models.supplier import AgentReport, CompetitorListing, MarketplaceEvidence, ProductIdea, ProductSource, ProfitAnalysis
from app.schemas.portfolio_schema import (
    PortfolioItemCreate,
    PortfolioItemResponse,
    PortfolioItemUpdate,
    ProductCollectionCreate,
    ProductCollectionResponse,
    ProductCollectionUpdate,
    ShopConceptCreate,
    ShopConceptDetailResponse,
    ShopConceptResponse,
    ShopConceptUpdate,
    ShopPortfolioReportResponse,
)


def _json_load(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


def _best_source_landed_cost(source: ProductSource) -> float | None:
    if source.estimated_landed_cost is not None:
        return float(source.estimated_landed_cost)
    values = [source.unit_cost, source.domestic_shipping, source.international_shipping_estimate]
    if any(value is None for value in values):
        return None
    return round(sum(float(value) for value in values if value is not None), 2)


def _product_decision(product: Product, agent_rows: list[AgentReport]) -> dict[str, Any]:
    latest = {}
    for report in agent_rows:
        if report.agent_name == "decision_agent" and report.output_json:
            latest = _json_load(report.output_json, {})
            break
    decision = (product.final_decision or latest.get("research_verdict") or product.status or "UNKNOWN").upper()
    readiness = (latest.get("buy_readiness_status") or latest.get("buy_readiness") or product.status or "NOT_READY").upper()
    return {
        "final_decision": decision,
        "buy_readiness_status": readiness,
        "research_verdict": product.final_decision or latest.get("research_verdict") or product.status,
        "main_blocker": latest.get("main_blocker"),
        "next_action": latest.get("next_action") or getattr(product, "decision_reason", None),
    }


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def create_shop_concept(self, data: ShopConceptCreate) -> ShopConcept:
        shop = ShopConcept(
            name=data.name,
            description=data.description,
            target_customer=data.target_customer,
            category=data.category,
            price_min=data.price_min,
            price_max=data.price_max,
            avoid_list_json=data.avoid_list_json or {},
            preferred_attributes_json=data.preferred_attributes_json or {},
            brand_angle=data.brand_angle,
            status=data.status,
        )
        self.db.add(shop)
        self.db.commit()
        self.db.refresh(shop)
        return shop

    def list_shop_concepts(self) -> list[ShopConcept]:
        return self.db.query(ShopConcept).order_by(ShopConcept.updated_at.desc()).all()

    def get_shop_concept(self, shop_id: uuid.UUID) -> ShopConcept | None:
        return self.db.query(ShopConcept).filter(ShopConcept.id == shop_id).first()

    def update_shop_concept(self, shop_id: uuid.UUID, data: ShopConceptUpdate) -> ShopConcept | None:
        shop = self.get_shop_concept(shop_id)
        if not shop:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(shop, field, value)
        shop.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(shop)
        return shop

    def create_collection(self, shop_id: uuid.UUID, data: ProductCollectionCreate) -> ProductCollection:
        shop = self.get_shop_concept(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop concept not found")
        if data.shop_concept_id and data.shop_concept_id != shop_id:
            raise HTTPException(status_code=400, detail="shop_concept_id mismatch.")
        collection = ProductCollection(
            shop_concept_id=shop.id,
            name=data.name,
            theme=data.theme,
            target_problem=data.target_problem,
            description=data.description,
            status=data.status,
        )
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        return collection

    def get_collection(self, collection_id: uuid.UUID) -> ProductCollection | None:
        return self.db.query(ProductCollection).filter(ProductCollection.id == collection_id).first()

    def update_collection(self, collection_id: uuid.UUID, data: ProductCollectionUpdate) -> ProductCollection | None:
        collection = self.get_collection(collection_id)
        if not collection:
            return None
        if data.shop_concept_id and data.shop_concept_id != collection.shop_concept_id:
            raise HTTPException(status_code=400, detail="shop_concept_id mismatch.")
        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "shop_concept_id" and value is not None:
                continue
            setattr(collection, field, value)
        collection.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(collection)
        return collection

    def _resolve_shop_context(
        self,
        *,
        shop_concept_id: uuid.UUID | None,
        collection_id: uuid.UUID | None,
        idea_id: uuid.UUID | None,
        product_id: uuid.UUID | None,
    ) -> tuple[uuid.UUID | None, uuid.UUID | None]:
        if collection_id:
            collection = self.get_collection(collection_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Product collection not found")
            if shop_concept_id and collection.shop_concept_id != shop_concept_id:
                raise HTTPException(status_code=400, detail="collection does not belong to shop concept")
            shop_concept_id = shop_concept_id or collection.shop_concept_id
        if idea_id:
            idea = self.db.query(ProductIdea).filter(ProductIdea.id == idea_id).first()
            if idea:
                shop_concept_id = shop_concept_id or idea.shop_concept_id
                collection_id = collection_id or idea.collection_id
        if product_id:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if product:
                shop_concept_id = shop_concept_id or product.shop_concept_id
                collection_id = collection_id or product.collection_id
        return shop_concept_id, collection_id

    def add_portfolio_item(self, shop_id: uuid.UUID, data: PortfolioItemCreate) -> PortfolioItem:
        shop = self.get_shop_concept(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop concept not found")
        if not data.idea_id and not data.product_id:
            raise HTTPException(status_code=400, detail="Either idea_id or product_id is required.")
        if data.shop_concept_id and data.shop_concept_id != shop_id:
            raise HTTPException(status_code=400, detail="shop_concept_id mismatch.")
        if data.idea_id and data.product_id:
            raise HTTPException(status_code=400, detail="Link either an idea or a product, not both.")

        resolved_shop_id, resolved_collection_id = self._resolve_shop_context(
            shop_concept_id=data.shop_concept_id or shop_id,
            collection_id=data.collection_id,
            idea_id=data.idea_id,
            product_id=data.product_id,
        )
        if resolved_shop_id is None:
            resolved_shop_id = shop_id
        if data.collection_id and resolved_collection_id is None:
            raise HTTPException(status_code=404, detail="Product collection not found")

        item = PortfolioItem(
            shop_concept_id=resolved_shop_id,
            collection_id=resolved_collection_id,
            idea_id=data.idea_id,
            product_id=data.product_id,
            role=data.role,
            status=data.status,
            assortment_fit_score=data.assortment_fit_score,
            bundle_potential_score=data.bundle_potential_score,
            notes=data.notes,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_portfolio_item(self, item_id: uuid.UUID) -> PortfolioItem | None:
        return self.db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()

    def update_portfolio_item(self, item_id: uuid.UUID, data: PortfolioItemUpdate) -> PortfolioItem | None:
        item = self.get_portfolio_item(item_id)
        if not item:
            return None
        if data.shop_concept_id and data.shop_concept_id != item.shop_concept_id:
            raise HTTPException(status_code=400, detail="shop_concept_id mismatch.")
        if data.collection_id:
            collection = self.get_collection(data.collection_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Product collection not found")
            if collection.shop_concept_id != (data.shop_concept_id or item.shop_concept_id):
                raise HTTPException(status_code=400, detail="collection does not belong to shop concept")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def _serialize_shop(self, shop: ShopConcept) -> dict[str, Any]:
        collections = self.db.query(ProductCollection).filter(ProductCollection.shop_concept_id == shop.id).all()
        portfolio_items = self.db.query(PortfolioItem).filter(PortfolioItem.shop_concept_id == shop.id).all()
        ideas = self.db.query(ProductIdea).filter(ProductIdea.shop_concept_id == shop.id).all()
        products = self.db.query(Product).filter(Product.shop_concept_id == shop.id).all()
        campaigns = self.db.query(DiscoveryCampaign).filter(DiscoveryCampaign.shop_concept_id == shop.id).all()
        return {
            "id": str(shop.id),
            "name": shop.name,
            "description": shop.description,
            "target_customer": shop.target_customer,
            "category": shop.category,
            "price_min": float(shop.price_min) if shop.price_min is not None else None,
            "price_max": float(shop.price_max) if shop.price_max is not None else None,
            "avoid_list_json": _json_load(shop.avoid_list_json, {}),
            "preferred_attributes_json": _json_load(shop.preferred_attributes_json, {}),
            "brand_angle": shop.brand_angle,
            "status": shop.status,
            "created_at": shop.created_at,
            "updated_at": shop.updated_at,
            "campaign_count": len(campaigns),
            "collection_count": len(collections),
            "idea_count": len(ideas),
            "product_count": len(products),
            "portfolio_item_count": len(portfolio_items),
        }

    def _serialize_collection(self, collection: ProductCollection) -> dict[str, Any]:
        portfolio_items = self.db.query(PortfolioItem).filter(PortfolioItem.collection_id == collection.id).all()
        ideas = self.db.query(ProductIdea).filter(ProductIdea.collection_id == collection.id).all()
        products = self.db.query(Product).filter(Product.collection_id == collection.id).all()
        return {
            "id": str(collection.id),
            "shop_concept_id": str(collection.shop_concept_id),
            "shop_concept_name": collection.shop_concept.name if collection.shop_concept else None,
            "name": collection.name,
            "theme": collection.theme,
            "target_problem": collection.target_problem,
            "description": collection.description,
            "status": collection.status,
            "created_at": collection.created_at,
            "updated_at": collection.updated_at,
            "portfolio_item_count": len(portfolio_items),
            "idea_count": len(ideas),
            "product_count": len(products),
        }

    def _serialize_item(self, item: PortfolioItem) -> dict[str, Any]:
        return {
            "id": str(item.id),
            "shop_concept_id": str(item.shop_concept_id),
            "shop_concept_name": item.shop_concept.name if item.shop_concept else None,
            "collection_id": str(item.collection_id) if item.collection_id else None,
            "collection_name": item.collection.name if item.collection else None,
            "idea_id": str(item.idea_id) if item.idea_id else None,
            "idea_name": item.idea.idea_name if item.idea else None,
            "product_id": str(item.product_id) if item.product_id else None,
            "product_name": item.product.name if item.product else None,
            "role": item.role,
            "status": item.status,
            "assortment_fit_score": int(item.assortment_fit_score or 0),
            "bundle_potential_score": int(item.bundle_potential_score or 0),
            "notes": item.notes,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }

    def _product_summary(self, product: Product) -> dict[str, Any]:
        agent_rows = self.db.query(AgentReport).filter(AgentReport.product_id == product.id).order_by(AgentReport.created_at.desc()).all()
        decision = _product_decision(product, agent_rows)
        return {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "status": product.status,
            "research_verdict": decision["research_verdict"],
            "buy_readiness_status": decision["buy_readiness_status"],
            "final_decision": decision["final_decision"],
            "next_action": decision["next_action"],
            "main_blocker": decision["main_blocker"],
        }

    def _idea_summary(self, idea: ProductIdea) -> dict[str, Any]:
        return {
            "id": str(idea.id),
            "idea_name": idea.idea_name,
            "category": idea.category,
            "status": idea.status,
            "quick_scan_verdict": idea.quick_scan_verdict,
            "buy_readiness_status": "NOT_READY",
            "opportunity_score": 0,
            "research_completeness_score": 0,
        }

    def get_product_portfolio_context(self, product_id: uuid.UUID) -> dict[str, Any] | None:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        items = self.db.query(PortfolioItem).filter(PortfolioItem.product_id == product.id).order_by(PortfolioItem.updated_at.desc()).all()
        if not items and not product.shop_concept_id and not product.collection_id:
            return None
        return {
            "shop_concept": self._serialize_shop(product.shop_concept) if product.shop_concept else None,
            "collection": self._serialize_collection(product.collection) if product.collection else None,
            "portfolio_items": [self._serialize_item(item) for item in items],
        }

    def get_shop_report(self, shop_id: uuid.UUID) -> dict[str, Any]:
        shop = self.get_shop_concept(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop concept not found")
        collections = self.db.query(ProductCollection).filter(ProductCollection.shop_concept_id == shop.id).order_by(ProductCollection.updated_at.desc()).all()
        items = self.db.query(PortfolioItem).filter(PortfolioItem.shop_concept_id == shop.id).order_by(PortfolioItem.updated_at.desc()).all()
        products = self.db.query(Product).filter(Product.shop_concept_id == shop.id).order_by(Product.updated_at.desc()).all()
        ideas = self.db.query(ProductIdea).filter(ProductIdea.shop_concept_id == shop.id).order_by(ProductIdea.updated_at.desc()).all()

        items_by_role: dict[str, int] = {}
        items_by_status: dict[str, int] = {}
        for item in items:
            items_by_role[item.role] = items_by_role.get(item.role, 0) + 1
            items_by_status[item.status] = items_by_status.get(item.status, 0) + 1

        products_by_decision: dict[str, int] = {}
        watchlist_products: list[dict[str, Any]] = []
        skip_products: list[dict[str, Any]] = []
        ready_for_sample_products: list[dict[str, Any]] = []
        for product in products:
            summary = self._product_summary(product)
            decision = str(summary.get("final_decision") or summary.get("research_verdict") or "UNKNOWN").upper()
            products_by_decision[decision] = products_by_decision.get(decision, 0) + 1
            if decision == "WATCHLIST":
                watchlist_products.append(summary)
            elif decision in {"SKIP", "REJECT"}:
                skip_products.append(summary)
            elif decision in {"READY_FOR_SAMPLE", "BUY_SAMPLE"} or str(summary.get("buy_readiness_status") or "").upper() in {"READY", "READY_FOR_SAMPLE"}:
                ready_for_sample_products.append(summary)

        ideas_still_under_research = [self._idea_summary(idea) for idea in ideas if idea.promoted_product_id is None or (idea.quick_scan_verdict or "").upper() in {"", "NEEDS_MARKET_CHECK", "NEEDS_SUPPLIER_CHECK"}]
        hero_count = sum(1 for item in items if (item.role or "").upper() == "HERO")
        support_item_count = sum(1 for item in items if (item.role or "").upper() in {"ADD_ON", "BUNDLE_SUPPORT"})
        collection_gaps: list[str] = []
        if hero_count < 1:
            collection_gaps.append("No hero portfolio item yet.")
        if support_item_count < 2:
            collection_gaps.append("No add-on or bundle support items yet.")
        if not ready_for_sample_products:
            collection_gaps.append("No sample-ready product yet.")
        if not items:
            collection_gaps.append("No portfolio items have been added.")

        shop_readiness_blockers: list[str] = []
        if not collections:
            shop_readiness_blockers.append("No collections defined yet.")
        if hero_count < 1:
            shop_readiness_blockers.append("No hero portfolio item yet.")
        if support_item_count < 2:
            shop_readiness_blockers.append("Need at least two add-on or bundle support items.")
        if not ready_for_sample_products:
            shop_readiness_blockers.append("No sample-ready product yet.")
        if len(collections) < 2:
            shop_readiness_blockers.append("Need at least two collections.")

        if not collections or not items:
            shop_readiness_status = "NOT_READY"
        elif hero_count < 1 or support_item_count < 2 or len(collections) < 2 or not ready_for_sample_products:
            shop_readiness_status = "BUILDING_ASSORTMENT"
        else:
            shop_readiness_status = "READY_FOR_BASIC_WEBSITE"

        shop_readiness_score = 0
        if collections:
            shop_readiness_score += 25
        if len(collections) >= 2:
            shop_readiness_score += 20
        if items:
            shop_readiness_score += 15
        if hero_count >= 1:
            shop_readiness_score += 15
        if ready_for_sample_products:
            shop_readiness_score += 15
        if support_item_count >= 2:
            shop_readiness_score += 10

        next_recommended_campaign = None
        if not any((item.role or "").upper() == "HERO" for item in items):
            next_recommended_campaign = f"Run a hero-product campaign for {shop.name}."
        elif not any((item.role or "").upper() in {"ADD_ON", "BUNDLE_SUPPORT"} for item in items):
            next_recommended_campaign = f"Run add-on discovery for {shop.name}."
        else:
            next_recommended_campaign = f"Strengthen {shop.name} by filling the weakest collection gap."

        next_action = collection_gaps[0] if collection_gaps else f"Review the {shop.name} shop portfolio."

        return {
            "shop_concept_id": str(shop.id),
            "shop_concept_name": shop.name,
            "shop_readiness_status": shop_readiness_status,
            "shop_readiness_score": min(shop_readiness_score, 100),
            "shop_readiness_blockers": shop_readiness_blockers,
            "collections": [self._serialize_collection(collection) for collection in collections],
            "portfolio_items": [self._serialize_item(item) for item in items],
            "total_items": len(items),
            "items_by_role": items_by_role,
            "items_by_status": items_by_status,
            "products_by_decision": products_by_decision,
            "watchlist_products": watchlist_products,
            "skip_products": skip_products,
            "ready_for_sample_products": ready_for_sample_products,
            "ideas_still_under_research": ideas_still_under_research,
            "collection_gaps": collection_gaps,
            "next_recommended_campaign": next_recommended_campaign,
            "next_action": next_action,
        }

    def get_shop_detail(self, shop_id: uuid.UUID) -> ShopConceptDetailResponse:
        shop = self.get_shop_concept(shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop concept not found")
        collections = self.db.query(ProductCollection).filter(ProductCollection.shop_concept_id == shop.id).order_by(ProductCollection.updated_at.desc()).all()
        items = self.db.query(PortfolioItem).filter(PortfolioItem.shop_concept_id == shop.id).order_by(PortfolioItem.updated_at.desc()).all()
        report = self.get_shop_report(shop.id)
        return ShopConceptDetailResponse(
            shop_concept=ShopConceptResponse.model_validate(self._serialize_shop(shop)),
            collections=[ProductCollectionResponse.model_validate(self._serialize_collection(collection)) for collection in collections],
            portfolio_items=[PortfolioItemResponse.model_validate(self._serialize_item(item)) for item in items],
            report=ShopPortfolioReportResponse.model_validate(report),
        )
