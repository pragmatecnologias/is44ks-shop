from fastapi import APIRouter

from app.routes.products import router as products_router, supplier_router
from app.routes.dashboard import router as dashboard_router
from app.routes.marketplace import router as marketplace_router
from app.routes.profit import router as profit_router
from app.routes.agents import router as agents_router
from app.routes.discovery import router as discovery_router
from app.routes.campaigns import router as campaigns_router
from app.routes.portfolio import router as portfolio_router
from app.routes.validation import router as validation_router
from app.routes.research import router as research_router
from app.routes.vision import router as vision_router
from app.routes.external_research import router as external_research_router
from app.routes.evidence_candidates import router as evidence_candidates_router
from app.routes.capture import router as capture_router
from app.routes.listings import router as listings_router
from app.routes.inventory import router as inventory_router
from app.routes.sales import router as sales_router
from app.routes.research_search import router as research_search_router
from app.routes.production import production_router

__all__ = [
    "products_router",
    "supplier_router",
    "dashboard_router",
    "marketplace_router",
    "profit_router",
    "agents_router",
    "discovery_router",
    "campaigns_router",
    "portfolio_router",
    "validation_router",
    "research_router",
    "vision_router",
    "external_research_router",
    "evidence_candidates_router",
    "capture_router",
    "listings_router",
    "inventory_router",
    "sales_router",
    "research_search_router",
    "production_router",
]
