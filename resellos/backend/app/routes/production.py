from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.production_schema import (
    MachineCandidateCreate,
    MachineCandidateUpdate,
    MachineCandidateResponse,
    MachineCockpitResponse,
    MachineDecisionResponse,
    MachineEvidenceCreate,
    MachineEvidenceResponse,
    MachineProductFamilyCreate,
    MachineProductFamilyResponse,
    MachineProductFamilyUpdate,
    ProductionCampaignCreate,
    ProductionCampaignDetailResponse,
    ProductionCampaignResponse,
    ProductionCampaignUpdate,
    ProductionCapabilityCreate,
    ProductionCapabilityResponse,
    ProductionCostScenarioCreate,
    ProductionCostScenarioResponse,
    ProductionCostScenarioUpdate,
)
from app.services.production_service import ProductionService

production_router = APIRouter(prefix="/api/production", tags=["production"])


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------


@production_router.post("/campaigns", response_model=ProductionCampaignResponse, status_code=201)
def create_campaign(data: ProductionCampaignCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    campaign = service.create_campaign(data.model_dump())
    return service._serialize_campaign(campaign)


@production_router.get("/campaigns", response_model=list[ProductionCampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    service = ProductionService(db)
    return [service._serialize_campaign(c) for c in service.list_campaigns()]


@production_router.get("/campaigns/{campaign_id}", response_model=ProductionCampaignDetailResponse)
def get_campaign(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    campaign = service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Production campaign not found")
    capabilities = service.list_capabilities(campaign_id)
    machines = service.list_machines(campaign_id)
    return {
        "campaign": service._serialize_campaign(campaign),
        "capabilities": [service._serialize_capability(c) for c in capabilities],
        "machines": [service._serialize_machine(m) for m in machines],
    }


@production_router.patch("/campaigns/{campaign_id}", response_model=ProductionCampaignResponse)
def update_campaign(
    campaign_id: uuid.UUID, data: ProductionCampaignUpdate, db: Session = Depends(get_db)
):
    service = ProductionService(db)
    campaign = service.update_campaign(campaign_id, data.model_dump(exclude_unset=True))
    if not campaign:
        raise HTTPException(status_code=404, detail="Production campaign not found")
    return service._serialize_campaign(campaign)


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------


@production_router.post("/capabilities", response_model=ProductionCapabilityResponse, status_code=201)
def create_capability(data: ProductionCapabilityCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    cap = service.create_capability(data.model_dump())
    return service._serialize_capability(cap)


@production_router.get("/capabilities", response_model=list[ProductionCapabilityResponse])
def list_capabilities(campaign_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    return [service._serialize_capability(c) for c in service.list_capabilities(campaign_id)]


# ---------------------------------------------------------------------------
# Machines
# ---------------------------------------------------------------------------


@production_router.post("/machines", response_model=MachineCandidateResponse, status_code=201)
def create_machine(data: MachineCandidateCreate, db: Session = Depends(get_db)):
    service = ProductionService(db)
    payload = data.model_dump()
    machine = service.create_machine(payload)
    return service._serialize_machine(machine)


@production_router.get("/machines", response_model=list[MachineCandidateResponse])
def list_machines(
    campaign_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    return [service._serialize_machine(m) for m in service.list_machines(campaign_id)]


@production_router.get("/machines/{machine_id}", response_model=MachineCockpitResponse)
def get_machine_cockpit(machine_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    cockpit = service.get_machine_cockpit(machine_id)
    if not cockpit:
        raise HTTPException(status_code=404, detail="Machine not found")
    return cockpit


@production_router.patch("/machines/{machine_id}", response_model=MachineCandidateResponse)
def update_machine(
    machine_id: uuid.UUID, data: MachineCandidateUpdate, db: Session = Depends(get_db)
):
    service = ProductionService(db)
    machine = service.update_machine(machine_id, data.model_dump(exclude_unset=True))
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return service._serialize_machine(machine)


@production_router.post("/machines/{machine_id}/decision", response_model=MachineDecisionResponse)
def run_decision(machine_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    decision = service.run_machine_decision(machine_id)
    return service._serialize_decision(decision)


@production_router.get("/machines/{machine_id}/next-action")
def get_next_action(machine_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    cockpit = service.get_machine_cockpit(machine_id)
    if not cockpit:
        raise HTTPException(status_code=404, detail="Machine not found")
    return cockpit["next_action"]


# ---------------------------------------------------------------------------
# Machine Evidence
# ---------------------------------------------------------------------------


@production_router.post(
    "/machines/{machine_id}/evidence",
    response_model=MachineEvidenceResponse,
    status_code=201,
)
def create_evidence(
    machine_id: uuid.UUID, data: MachineEvidenceCreate, db: Session = Depends(get_db)
):
    service = ProductionService(db)
    ev = service.create_evidence(machine_id, data.model_dump())
    return service._serialize_evidence(ev)


@production_router.get(
    "/machines/{machine_id}/evidence", response_model=list[MachineEvidenceResponse]
)
def list_evidence(machine_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    return [service._serialize_evidence(e) for e in service.list_evidence(machine_id)]


@production_router.patch(
    "/machines/{machine_id}/evidence/{evidence_id}/verify",
    response_model=MachineEvidenceResponse,
)
def verify_evidence(
    machine_id: uuid.UUID,
    evidence_id: uuid.UUID,
    data: dict[str, str],
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    ev = service.verify_evidence(evidence_id, data.get("status", "USER_VERIFIED"))
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return service._serialize_evidence(ev)


@production_router.post(
    "/machines/{machine_id}/evidence/{evidence_id}/reject",
    response_model=MachineEvidenceResponse,
)
def reject_evidence(
    machine_id: uuid.UUID,
    evidence_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    ev = service.reject_evidence(evidence_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return service._serialize_evidence(ev)


# ---------------------------------------------------------------------------
# Product Families
# ---------------------------------------------------------------------------


@production_router.post(
    "/machines/{machine_id}/product-families",
    response_model=MachineProductFamilyResponse,
    status_code=201,
)
def create_product_family(
    machine_id: uuid.UUID,
    data: MachineProductFamilyCreate,
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    fam = service.create_product_family(machine_id, data.model_dump())
    return service._serialize_product_family(fam)


@production_router.get(
    "/machines/{machine_id}/product-families",
    response_model=list[MachineProductFamilyResponse],
)
def list_product_families(machine_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    return [
        service._serialize_product_family(f)
        for f in service.list_product_families(machine_id)
    ]


@production_router.patch(
    "/machines/{machine_id}/product-families/{family_id}",
    response_model=MachineProductFamilyResponse,
)
def update_product_family(
    machine_id: uuid.UUID,
    family_id: uuid.UUID,
    data: MachineProductFamilyUpdate,
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    fam = service.update_product_family(family_id, data.model_dump(exclude_unset=True))
    if not fam:
        raise HTTPException(status_code=404, detail="Product family not found")
    return service._serialize_product_family(fam)


@production_router.post("/machines/{machine_id}/product-families/{family_id}/promote-to-product")
def promote_product_family(
    machine_id: uuid.UUID,
    family_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    return service.promote_product_family(family_id)


# ---------------------------------------------------------------------------
# Cost Scenarios
# ---------------------------------------------------------------------------


@production_router.post(
    "/product-families/{family_id}/cost-scenarios",
    response_model=ProductionCostScenarioResponse,
    status_code=201,
)
def create_cost_scenario(
    family_id: uuid.UUID,
    data: ProductionCostScenarioCreate,
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    sc = service.create_cost_scenario(family_id, data.model_dump())
    return service._serialize_cost_scenario(sc)


@production_router.get(
    "/product-families/{family_id}/cost-scenarios",
    response_model=list[ProductionCostScenarioResponse],
)
def list_cost_scenarios(family_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ProductionService(db)
    return [
        service._serialize_cost_scenario(s)
        for s in service.list_cost_scenarios(family_id)
    ]


@production_router.patch(
    "/product-families/{family_id}/cost-scenarios/{scenario_id}",
    response_model=ProductionCostScenarioResponse,
)
def update_cost_scenario(
    family_id: uuid.UUID,
    scenario_id: uuid.UUID,
    data: ProductionCostScenarioUpdate,
    db: Session = Depends(get_db),
):
    service = ProductionService(db)
    sc = service.update_cost_scenario(scenario_id, data.model_dump(exclude_unset=True))
    if not sc:
        raise HTTPException(status_code=404, detail="Cost scenario not found")
    return service._serialize_cost_scenario(sc)
