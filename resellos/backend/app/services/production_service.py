from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.production import (
    MachineCandidate,
    MachineDecision,
    MachineEvidence,
    MachineProductFamily,
    ProductionCampaign,
    ProductionCapability,
    ProductionCostScenario,
    machine_capabilities,
)
from app.models.product import Product
from app.models.supplier import ProductIdea


class ProductionService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Campaign CRUD
    # ------------------------------------------------------------------

    def list_campaigns(self) -> list[ProductionCampaign]:
        return (
            self.db.query(ProductionCampaign)
            .order_by(ProductionCampaign.updated_at.desc())
            .all()
        )

    def get_campaign(self, campaign_id: uuid.UUID) -> Optional[ProductionCampaign]:
        return (
            self.db.query(ProductionCampaign)
            .filter(ProductionCampaign.id == campaign_id)
            .first()
        )

    def create_campaign(self, data: dict[str, Any]) -> ProductionCampaign:
        campaign = ProductionCampaign(
            id=uuid.uuid4(),
            name=data["name"],
            shop_concept_id=data.get("shop_concept_id"),
            mode="PRODUCTION",
            goal=data.get("goal"),
            workspace_type=data.get("workspace_type"),
            workspace_dimensions_json=data.get("workspace_dimensions_json"),
            power_constraints_json=data.get("power_constraints_json"),
            safety_requirements_json=data.get("safety_requirements_json"),
            budget_limit_usd=data.get("budget_limit_usd"),
            status=data.get("status", "DRAFT"),
            created_by=data.get("created_by"),
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def update_campaign(
        self, campaign_id: uuid.UUID, data: dict[str, Any]
    ) -> Optional[ProductionCampaign]:
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        for field, value in data.items():
            if value is not None:
                setattr(campaign, field, value)
        campaign.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    # ------------------------------------------------------------------
    # Capability CRUD
    # ------------------------------------------------------------------

    def list_capabilities(self, campaign_id: uuid.UUID) -> list[ProductionCapability]:
        return (
            self.db.query(ProductionCapability)
            .filter(ProductionCapability.campaign_id == campaign_id)
            .all()
        )

    def create_capability(self, data: dict[str, Any]) -> ProductionCapability:
        cap = ProductionCapability(
            id=uuid.uuid4(),
            campaign_id=data["campaign_id"],
            name=data["name"],
            category=data.get("category"),
            description=data.get("description"),
            materials=data.get("materials"),
            typical_products=data.get("typical_products"),
            entry_cost_range_json=data.get("entry_cost_range_json"),
            skill_level=data.get("skill_level"),
            workspace_footprint=data.get("workspace_footprint"),
        )
        self.db.add(cap)
        self.db.commit()
        self.db.refresh(cap)
        return cap

    # ------------------------------------------------------------------
    # Machine CRUD
    # ------------------------------------------------------------------

    def list_machines(
        self, campaign_id: Optional[uuid.UUID] = None
    ) -> list[MachineCandidate]:
        q = self.db.query(MachineCandidate)
        if campaign_id:
            q = q.filter(MachineCandidate.campaign_id == campaign_id)
        return q.order_by(MachineCandidate.updated_at.desc()).all()

    def get_machine(self, machine_id: uuid.UUID) -> Optional[MachineCandidate]:
        return (
            self.db.query(MachineCandidate)
            .filter(MachineCandidate.id == machine_id)
            .first()
        )

    def create_machine(self, data: dict[str, Any]) -> MachineCandidate:
        capability_ids = data.pop("capability_ids", None)
        campaign_id = data["campaign_id"]
        if isinstance(campaign_id, str):
            campaign_id = uuid.UUID(campaign_id)
        machine = MachineCandidate(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            name=data["name"],
            brand=data.get("brand"),
            model=data.get("model"),
            category=data.get("category"),
            description=data.get("description"),
            url=data.get("url"),
            price_new=data.get("price_new"),
            price_used_range_json=data.get("price_used_range_json"),
            condition=data.get("condition"),
            power_requirements=data.get("power_requirements"),
            workspace_needed=data.get("workspace_needed"),
            safety_notes=data.get("safety_notes"),
            status="SUGGESTED",
        )
        if capability_ids:
            caps = (
                self.db.query(ProductionCapability)
                .filter(ProductionCapability.id.in_(capability_ids))
                .all()
            )
            machine.capabilities = caps
        self.db.add(machine)
        self.db.commit()
        self.db.refresh(machine)
        return machine

    def update_machine(
        self, machine_id: uuid.UUID, data: dict[str, Any]
    ) -> Optional[MachineCandidate]:
        machine = self.get_machine(machine_id)
        if not machine:
            return None
        capability_ids = data.pop("capability_ids", None)
        for field, value in data.items():
            if value is not None:
                setattr(machine, field, value)
        if capability_ids is not None:
            caps = (
                self.db.query(ProductionCapability)
                .filter(ProductionCapability.id.in_(capability_ids))
                .all()
            )
            machine.capabilities = caps
        machine.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(machine)
        return machine

    # ------------------------------------------------------------------
    # Evidence CRUD
    # ------------------------------------------------------------------

    def list_evidence(self, machine_id: uuid.UUID) -> list[MachineEvidence]:
        return (
            self.db.query(MachineEvidence)
            .filter(MachineEvidence.machine_id == machine_id)
            .order_by(MachineEvidence.created_at.desc())
            .all()
        )

    def create_evidence(
        self, machine_id: uuid.UUID, data: dict[str, Any]
    ) -> MachineEvidence:
        ev = MachineEvidence(
            id=uuid.uuid4(),
            machine_id=machine_id,
            evidence_type=data["evidence_type"],
            title=data.get("title"),
            url=data.get("url"),
            price=data.get("price"),
            source=data.get("source"),
            seller=data.get("seller"),
            condition=data.get("condition"),
            specs_json=data.get("specs_json"),
            pros=data.get("pros"),
            cons=data.get("cons"),
            verification_status="PENDING",
            confidence=data.get("confidence", "MEDIUM"),
            raw_text=data.get("raw_text"),
            screenshot_url=data.get("screenshot_url"),
            notes=data.get("notes"),
        )
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def verify_evidence(
        self, evidence_id: uuid.UUID, status: str
    ) -> Optional[MachineEvidence]:
        ev = (
            self.db.query(MachineEvidence)
            .filter(MachineEvidence.id == evidence_id)
            .first()
        )
        if not ev:
            return None
        ev.verification_status = status
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def reject_evidence(self, evidence_id: uuid.UUID) -> Optional[MachineEvidence]:
        return self.verify_evidence(evidence_id, "REJECTED")

    # ------------------------------------------------------------------
    # Product Families CRUD
    # ------------------------------------------------------------------

    def list_product_families(
        self, machine_id: uuid.UUID
    ) -> list[MachineProductFamily]:
        return (
            self.db.query(MachineProductFamily)
            .filter(MachineProductFamily.machine_id == machine_id)
            .order_by(MachineProductFamily.updated_at.desc())
            .all()
        )

    def create_product_family(
        self, machine_id: uuid.UUID, data: dict[str, Any]
    ) -> MachineProductFamily:
        fam = MachineProductFamily(
            id=uuid.uuid4(),
            machine_id=machine_id,
            name=data["name"],
            description=data.get("description"),
            material_cost_per_unit=data.get("material_cost_per_unit"),
            estimated_sale_price=data.get("estimated_sale_price"),
            estimated_demand=data.get("estimated_demand"),
            has_market_evidence=data.get("has_market_evidence", False),
            market_evidence_summary=data.get("market_evidence_summary"),
            notes=data.get("notes"),
        )
        self.db.add(fam)
        self.db.commit()
        self.db.refresh(fam)
        return fam

    def update_product_family(
        self, family_id: uuid.UUID, data: dict[str, Any]
    ) -> Optional[MachineProductFamily]:
        fam = (
            self.db.query(MachineProductFamily)
            .filter(MachineProductFamily.id == family_id)
            .first()
        )
        if not fam:
            return None
        for field, value in data.items():
            if value is not None:
                setattr(fam, field, value)
        fam.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(fam)
        return fam

    def promote_product_family(self, family_id: uuid.UUID) -> dict[str, Any]:
        fam = (
            self.db.query(MachineProductFamily)
            .filter(MachineProductFamily.id == family_id)
            .first()
        )
        if not fam:
            raise HTTPException(status_code=404, detail="Product family not found")
        if fam.status == "PROMOTED_TO_PRODUCT":
            return {
                "idea_id": str(fam.promoted_idea_id),
                "product_id": str(fam.promoted_product_id) if fam.promoted_product_id else None,
            }
        machine = fam.machine
        idea = ProductIdea(
            id=uuid.uuid4(),
            idea_name=fam.name,
            category=machine.category if machine else None,
            rough_supplier_cost=float(fam.material_cost_per_unit) if fam.material_cost_per_unit else None,
            estimated_landed_cost=float(fam.material_cost_per_unit) if fam.material_cost_per_unit else None,
            why_interesting=f"Produced by {machine.name}: {fam.description}" if machine else fam.description,
            research_priority="HIGH",
            status="NEW_IDEA",
        )
        self.db.add(idea)
        self.db.flush()

        product_id = None
        if fam.has_market_evidence:
            product = Product(
                id=uuid.uuid4(),
                sku=f"PROD-{idea.id.hex[:8].upper()}",
                name=fam.name,
                status="NEEDS_RESEARCH",
            )
            self.db.add(product)
            self.db.flush()
            idea.promoted_product_id = product.id
            product_id = str(product.id)

        fam.promoted_idea_id = idea.id
        fam.promoted_product_id = idea.promoted_product_id
        fam.status = "PROMOTED_TO_PRODUCT"
        self.db.commit()
        return {"idea_id": str(idea.id), "product_id": product_id}

    # ------------------------------------------------------------------
    # Cost Scenarios CRUD
    # ------------------------------------------------------------------

    def list_cost_scenarios(
        self, family_id: uuid.UUID
    ) -> list[ProductionCostScenario]:
        return (
            self.db.query(ProductionCostScenario)
            .filter(ProductionCostScenario.product_family_id == family_id)
            .order_by(ProductionCostScenario.created_at.desc())
            .all()
        )

    def create_cost_scenario(
        self, family_id: uuid.UUID, data: dict[str, Any]
    ) -> ProductionCostScenario:
        fam = (
            self.db.query(MachineProductFamily)
            .filter(MachineProductFamily.id == family_id)
            .first()
        )
        if not fam:
            raise HTTPException(status_code=404, detail="Product family not found")

        # Calculate total cost per unit from components
        cost_components = ['material_cost', 'labor_cost', 'machine_time_cost', 'consumables_cost',
                           'marketplace_fee', 'shipping_cost', 'packaging_cost', 'other_costs']
        total = sum(filter(None, [data.get(c) for c in cost_components]))
        # If any component is provided, compute total
        if total > 0:
            computed_total = total
        elif data.get('total_cost_per_unit'):
            computed_total = data['total_cost_per_unit']
        else:
            computed_total = None

        sale = data.get('sale_price')

        # Net profit per unit
        if computed_total is not None and sale is not None:
            net_profit = sale - computed_total
        elif data.get('net_profit_per_unit') is not None:
            net_profit = data['net_profit_per_unit']
        else:
            net_profit = None

        # Margin percent
        if sale and sale > 0 and net_profit is not None:
            margin = round((net_profit / sale) * 100, 2)
        elif data.get('margin_percent') is not None:
            margin = data['margin_percent']
        else:
            margin = None

        # Monthly profit
        units = data.get('units_per_month')
        if units and net_profit is not None:
            monthly = round(net_profit * units, 2)
        elif data.get('monthly_profit') is not None:
            monthly = data['monthly_profit']
        else:
            monthly = None

        # Payback months
        purchase_price = data.get('machine_purchase_price')
        if purchase_price and monthly and monthly > 0:
            payback = round(purchase_price / monthly, 1)
        elif data.get('payback_months') is not None:
            payback = data['payback_months']
        else:
            payback = None

        scenario = ProductionCostScenario(
            id=uuid.uuid4(),
            machine_id=fam.machine_id,
            product_family_id=family_id,
            scenario_name=data["scenario_name"],
            material_cost=data.get("material_cost"),
            labor_cost=data.get("labor_cost"),
            machine_time_cost=data.get("machine_time_cost"),
            consumables_cost=data.get("consumables_cost"),
            marketplace_fee=data.get("marketplace_fee"),
            shipping_cost=data.get("shipping_cost"),
            packaging_cost=data.get("packaging_cost"),
            other_costs=data.get("other_costs"),
            total_cost_per_unit=computed_total,
            sale_price=sale,
            net_profit_per_unit=net_profit,
            margin_percent=margin,
            machine_purchase_price=purchase_price,
            units_per_month=units,
            monthly_profit=monthly,
            payback_months=payback,
            notes=data.get("notes"),
        )
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def update_cost_scenario(
        self, scenario_id: uuid.UUID, data: dict[str, Any]
    ) -> Optional[ProductionCostScenario]:
        sc = (
            self.db.query(ProductionCostScenario)
            .filter(ProductionCostScenario.id == scenario_id)
            .first()
        )
        if not sc:
            return None
        for field, value in data.items():
            if value is not None:
                setattr(sc, field, value)
        self.db.commit()
        self.db.refresh(sc)
        return sc

    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------

    def get_decision(self, machine_id: uuid.UUID) -> Optional[MachineDecision]:
        return (
            self.db.query(MachineDecision)
            .filter(MachineDecision.machine_id == machine_id)
            .first()
        )

    def run_machine_decision(self, machine_id: uuid.UUID) -> MachineDecision:
        machine = self.get_machine(machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")

        evidence_rows = (
            self.db.query(MachineEvidence)
            .filter(MachineEvidence.machine_id == machine_id)
            .all()
        )
        families = (
            self.db.query(MachineProductFamily)
            .filter(MachineProductFamily.machine_id == machine_id)
            .all()
        )
        scenarios = (
            self.db.query(ProductionCostScenario)
            .filter(ProductionCostScenario.machine_id == machine_id)
            .all()
        )

        evidence_count = len(evidence_rows)
        verified_evidence = sum(
            1 for e in evidence_rows if e.verification_status == "USER_VERIFIED"
        )
        family_count = len(families)
        families_with_evidence = sum(1 for f in families if f.has_market_evidence)
        has_cost_scenario = len(scenarios) > 0
        payback_calculated = any(s.payback_months is not None for s in scenarios)

        hard_blockers: list[str] = []
        warnings: list[str] = []

        # Workspace / safety / budget checks
        workspace_fit = self._assess_workspace_fit(machine)
        safety_fit = self._assess_safety_fit(machine)
        budget_fit = self._assess_budget_fit(machine, machine.campaign)

        if workspace_fit == "INSUFFICIENT":
            hard_blockers.append("Workspace requirements not met")
        if safety_fit == "FAIL":
            hard_blockers.append("Safety requirements not met")
        if budget_fit == "EXCEEDED":
            hard_blockers.append("Budget exceeded")

        if evidence_count < 2:
            hard_blockers.append(f"Only {evidence_count} evidence items (need 2+)")
        if family_count < 2:
            warnings.append(f"Only {family_count} product families (recommend 2+)")
        if families_with_evidence == 0:
            hard_blockers.append("No product family has market evidence")
        if not has_cost_scenario:
            hard_blockers.append("No cost scenario created")
        if not payback_calculated:
            warnings.append("Payback not calculated")

        # Check for realistic payback
        if payback_calculated:
            best_payback = min(
                (float(s.payback_months) for s in scenarios if s.payback_months is not None),
                default=None,
            )
            if best_payback and best_payback > 36:
                hard_blockers.append(f"Payback period too long ({best_payback:.0f} months)")
            if best_payback and best_payback < 0:
                hard_blockers.append("Payback calculation invalid")

        # Check if most evidence is unverified
        if evidence_count > 0 and verified_evidence == 0:
            hard_blockers.append("No verified evidence — at least 1 USER_VERIFIED evidence item required")

        # Determine recommendation
        if hard_blockers:
            if evidence_count < 2 or families_with_evidence == 0 or not has_cost_scenario:
                recommendation = "NEEDS_MORE_RESEARCH"
            elif budget_fit == "EXCEEDED":
                recommendation = "WAIT_FOR_USED_DEAL"
            elif safety_fit == "FAIL" or workspace_fit == "INSUFFICIENT":
                recommendation = "REJECT"
            else:
                recommendation = "NEEDS_MORE_RESEARCH"
        else:
            recommendation = "BUY_MACHINE"

        # Update machine status
        machine.status = "DECIDED"
        machine.decision_recommendation = recommendation
        machine.decision_reason = "; ".join(hard_blockers + warnings) or "All gates passed"
        machine.decided_at = datetime.utcnow()

        # Upsert decision
        existing = self.get_decision(machine_id)
        if existing:
            self.db.delete(existing)
            self.db.flush()

        decision = MachineDecision(
            id=uuid.uuid4(),
            machine_id=machine_id,
            recommendation=recommendation,
            reason=machine.decision_reason,
            confidence="HIGH" if not warnings else "MEDIUM" if not hard_blockers else "LOW",
            evidence_count=evidence_count,
            product_family_count=family_count,
            families_with_market_evidence=families_with_evidence,
            has_cost_scenario=has_cost_scenario,
            payback_calculated=payback_calculated,
            workspace_fit=workspace_fit,
            safety_fit=safety_fit,
            budget_fit=budget_fit,
            hard_blockers_json=hard_blockers,
            warnings_json=warnings,
        )
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        return decision

    # ------------------------------------------------------------------
    # Cockpit (aggregated view)
    # ------------------------------------------------------------------

    def get_machine_cockpit(self, machine_id: uuid.UUID) -> dict[str, Any]:
        machine = self.get_machine(machine_id)
        if not machine:
            return None
        capabilities = machine.capabilities
        evidence = machine.evidence
        families = machine.product_families
        all_scenarios = machine.cost_scenarios
        decision = machine.decision

        next_action = self._compute_next_action(machine, evidence, families, all_scenarios, decision)

        return {
            "machine": self._serialize_machine(machine),
            "capabilities": [self._serialize_capability(c) for c in capabilities],
            "evidence": [self._serialize_evidence(e) for e in evidence],
            "product_families": [self._serialize_product_family(f) for f in families],
            "cost_scenarios": [self._serialize_cost_scenario(s) for s in all_scenarios],
            "decision": self._serialize_decision(decision) if decision else None,
            "next_action": next_action,
        }

    # ------------------------------------------------------------------
    # Next action
    # ------------------------------------------------------------------

    def _compute_next_action(
        self,
        machine: MachineCandidate,
        evidence: list[MachineEvidence],
        families: list[MachineProductFamily],
        scenarios: list[ProductionCostScenario],
        decision: Optional[MachineDecision],
    ) -> dict[str, Any]:
        if machine.status in ("DECIDED", "REJECTED", "ARCHIVED"):
            return {"action": "none", "reason": "Machine already decided"}

        if len(evidence) < 2:
            return {
                "action": "add_evidence",
                "priority": "HIGH",
                "reason": f"Only {len(evidence)} evidence items. Need 2+ for decision.",
            }

        if len(families) == 0:
            return {
                "action": "add_product_family",
                "priority": "HIGH",
                "reason": "No product families defined.",
            }

        if not any(f.has_market_evidence for f in families):
            return {
                "action": "research_product_family",
                "priority": "HIGH",
                "reason": "No product family has market evidence.",
            }

        if len(scenarios) == 0:
            return {
                "action": "add_cost_scenario",
                "priority": "HIGH",
                "reason": "No cost scenario created.",
            }

        if not any(s.payback_months is not None for s in scenarios):
            return {
                "action": "calculate_payback",
                "priority": "MEDIUM",
                "reason": "Payback not calculated.",
            }

        return {
            "action": "run_decision",
            "priority": "MEDIUM",
            "reason": "Ready for decision — all prerequisites met.",
        }

    # ------------------------------------------------------------------
    # Fit assessments
    # ------------------------------------------------------------------

    def _assess_workspace_fit(self, machine: MachineCandidate) -> str:
        if not machine.workspace_needed:
            return "UNKNOWN"
        return "FIT"

    def _assess_safety_fit(self, machine: MachineCandidate) -> str:
        if not machine.safety_notes:
            return "UNKNOWN"
        return "PASS"

    def _assess_budget_fit(
        self, machine: MachineCandidate, campaign: Optional[ProductionCampaign]
    ) -> str:
        if not campaign or campaign.budget_limit_usd is None:
            return "UNKNOWN"
        budget = float(campaign.budget_limit_usd)
        price = float(machine.price_new) if machine.price_new else None
        if price is None:
            return "UNKNOWN"
        if price <= budget:
            return "WITHIN"
        if price <= budget * 1.2:
            return "AT_LIMIT"
        return "EXCEEDED"

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def _serialize_campaign(self, campaign: ProductionCampaign) -> dict[str, Any]:
        machines = campaign.machines or []
        return {
            "id": str(campaign.id),
            "name": campaign.name,
            "shop_concept_id": str(campaign.shop_concept_id) if campaign.shop_concept_id else None,
            "mode": campaign.mode,
            "goal": campaign.goal,
            "workspace_type": campaign.workspace_type,
            "workspace_dimensions_json": campaign.workspace_dimensions_json,
            "power_constraints_json": campaign.power_constraints_json,
            "safety_requirements_json": campaign.safety_requirements_json,
            "budget_limit_usd": float(campaign.budget_limit_usd) if campaign.budget_limit_usd else None,
            "status": campaign.status,
            "created_by": campaign.created_by,
            "machine_count": len(machines),
            "shortlisted_count": sum(1 for m in machines if m.status == "SHORTLISTED"),
            "decided_count": sum(1 for m in machines if m.status == "DECIDED"),
            "report_generated_at": campaign.report_generated_at,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
        }

    def _serialize_capability(self, cap: ProductionCapability) -> dict[str, Any]:
        return {
            "id": str(cap.id),
            "campaign_id": str(cap.campaign_id),
            "name": cap.name,
            "category": cap.category,
            "description": cap.description,
            "materials": cap.materials,
            "typical_products": cap.typical_products,
            "entry_cost_range_json": cap.entry_cost_range_json,
            "skill_level": cap.skill_level,
            "workspace_footprint": cap.workspace_footprint,
            "machine_count": len(cap.machines) if cap.machines else 0,
            "created_at": cap.created_at,
        }

    def _serialize_machine(self, machine: MachineCandidate) -> dict[str, Any]:
        return {
            "id": str(machine.id),
            "campaign_id": str(machine.campaign_id),
            "name": machine.name,
            "brand": machine.brand,
            "model": machine.model,
            "category": machine.category,
            "description": machine.description,
            "url": machine.url,
            "price_new": float(machine.price_new) if machine.price_new else None,
            "price_used_range_json": machine.price_used_range_json,
            "condition": machine.condition,
            "power_requirements": machine.power_requirements,
            "workspace_needed": machine.workspace_needed,
            "safety_notes": machine.safety_notes,
            "status": machine.status,
            "decision_recommendation": machine.decision_recommendation,
            "decision_reason": machine.decision_reason,
            "decided_at": machine.decided_at,
            "notes": machine.notes,
            "evidence_count": len(machine.evidence) if machine.evidence else 0,
            "product_family_count": len(machine.product_families) if machine.product_families else 0,
            "cost_scenario_count": len(machine.cost_scenarios) if machine.cost_scenarios else 0,
            "has_decision": machine.decision is not None,
            "created_at": machine.created_at,
            "updated_at": machine.updated_at,
        }

    def _serialize_evidence(self, ev: MachineEvidence) -> dict[str, Any]:
        return {
            "id": str(ev.id),
            "machine_id": str(ev.machine_id),
            "evidence_type": ev.evidence_type,
            "title": ev.title,
            "url": ev.url,
            "price": float(ev.price) if ev.price else None,
            "source": ev.source,
            "seller": ev.seller,
            "condition": ev.condition,
            "specs_json": ev.specs_json,
            "pros": ev.pros,
            "cons": ev.cons,
            "verification_status": ev.verification_status,
            "confidence": ev.confidence,
            "raw_text": ev.raw_text,
            "screenshot_url": ev.screenshot_url,
            "notes": ev.notes,
            "created_at": ev.created_at,
        }

    def _serialize_product_family(self, fam: MachineProductFamily) -> dict[str, Any]:
        return {
            "id": str(fam.id),
            "machine_id": str(fam.machine_id),
            "name": fam.name,
            "description": fam.description,
            "material_cost_per_unit": float(fam.material_cost_per_unit) if fam.material_cost_per_unit else None,
            "estimated_sale_price": float(fam.estimated_sale_price) if fam.estimated_sale_price else None,
            "estimated_demand": fam.estimated_demand,
            "market_evidence_summary": fam.market_evidence_summary,
            "market_evidence_count": fam.market_evidence_count or 0,
            "has_market_evidence": fam.has_market_evidence or False,
            "status": fam.status,
            "promoted_product_id": str(fam.promoted_product_id) if fam.promoted_product_id else None,
            "promoted_idea_id": str(fam.promoted_idea_id) if fam.promoted_idea_id else None,
            "notes": fam.notes,
            "cost_scenario_count": len(fam.cost_scenarios) if fam.cost_scenarios else 0,
            "created_at": fam.created_at,
            "updated_at": fam.updated_at,
        }

    def _serialize_cost_scenario(self, sc: ProductionCostScenario) -> dict[str, Any]:
        return {
            "id": str(sc.id),
            "machine_id": str(sc.machine_id),
            "product_family_id": str(sc.product_family_id) if sc.product_family_id else None,
            "scenario_name": sc.scenario_name,
            "material_cost": float(sc.material_cost) if sc.material_cost else None,
            "labor_cost": float(sc.labor_cost) if sc.labor_cost else None,
            "machine_time_cost": float(sc.machine_time_cost) if sc.machine_time_cost else None,
            "consumables_cost": float(sc.consumables_cost) if sc.consumables_cost else None,
            "marketplace_fee": float(sc.marketplace_fee) if sc.marketplace_fee else None,
            "shipping_cost": float(sc.shipping_cost) if sc.shipping_cost else None,
            "packaging_cost": float(sc.packaging_cost) if sc.packaging_cost else None,
            "other_costs": float(sc.other_costs) if sc.other_costs else None,
            "total_cost_per_unit": float(sc.total_cost_per_unit) if sc.total_cost_per_unit else None,
            "sale_price": float(sc.sale_price) if sc.sale_price else None,
            "net_profit_per_unit": float(sc.net_profit_per_unit) if sc.net_profit_per_unit else None,
            "margin_percent": float(sc.margin_percent) if sc.margin_percent else None,
            "machine_purchase_price": float(sc.machine_purchase_price) if sc.machine_purchase_price else None,
            "units_per_month": sc.units_per_month,
            "monthly_profit": float(sc.monthly_profit) if sc.monthly_profit else None,
            "payback_months": float(sc.payback_months) if sc.payback_months else None,
            "notes": sc.notes,
            "created_at": sc.created_at,
        }

    def _serialize_decision(self, decision: MachineDecision) -> dict[str, Any]:
        return {
            "id": str(decision.id),
            "machine_id": str(decision.machine_id),
            "recommendation": decision.recommendation,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "evidence_count": decision.evidence_count or 0,
            "product_family_count": decision.product_family_count or 0,
            "families_with_market_evidence": decision.families_with_market_evidence or 0,
            "has_cost_scenario": decision.has_cost_scenario or False,
            "payback_calculated": decision.payback_calculated or False,
            "workspace_fit": decision.workspace_fit,
            "safety_fit": decision.safety_fit,
            "budget_fit": decision.budget_fit,
            "hard_blockers": decision.hard_blockers_json or [],
            "warnings": decision.warnings_json or [],
            "created_at": decision.created_at,
        }
