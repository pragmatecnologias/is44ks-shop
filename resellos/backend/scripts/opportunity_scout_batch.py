from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.db import SessionLocal
from app.models.campaign import DiscoveryCampaign
from app.models.research_search import ResearchSearchResult
from app.models.supplier import ProductIdea
from app.schemas.campaign_schema import DiscoveryCampaignCreate
from app.schemas.product_schema import OpportunityScoutRequest, ProductIdeaCreate
from app.schemas.research_search_schema import ResearchSearchRequest
from app.services.campaign_service import CampaignService
from app.services.discovery_service import DiscoveryService
from app.services.research_search_broker import ResearchSearchBroker


@dataclass(frozen=True)
class IdeaPlan:
    idea: str
    category: str
    why_interesting: str
    notes: str
    keywords: str
    sold: str
    active: str
    supplier: str
    competitor: str
    risk_notes: list[str]


PLANS: list[IdeaPlan] = [
    IdeaPlan(
        idea="Washing Machine Anti-Vibration Pads",
        category="Laundry room accessories",
        why_interesting="Reduce washer vibration and movement on hard floors.",
        notes="Do not claim it fixes broken suspension or severe appliance issues.",
        keywords="washing machine anti vibration pads",
        sold="washer anti vibration pads sold",
        active="washer anti vibration pads",
        supplier="washer anti vibration pads supplier",
        competitor="anti vibration rubber feet pads",
        risk_notes=["Installation and leveling matter", "Does not fix broken suspension"],
    ),
    IdeaPlan(
        idea="Moen Shower Cartridge Puller Tool",
        category="Plumbing repair",
        why_interesting="Stuck Moen shower cartridge removal tool for common cartridge families.",
        notes="Shut off water before removal and avoid forcing the valve body.",
        keywords="Moen cartridge puller tool",
        sold="Moen cartridge puller tool sold",
        active="Moen 1222 cartridge puller",
        supplier="Moen cartridge puller supplier",
        competitor="Moen cartridge extractor tool",
        risk_notes=["Shut off water before removal", "Do not force the cartridge"],
    ),
    IdeaPlan(
        idea="Bi-Fold Closet Door Hardware Repair Kit",
        category="Home repair",
        why_interesting="Repair sagging bi-fold closet doors with pivot and roller hardware.",
        notes="Compatibility matters; focus on pivot diameter and door thickness fit.",
        keywords="bi fold closet door hardware repair kit",
        sold="bifold door repair kit sold",
        active="bifold door repair kit",
        supplier="bifold door hardware repair kit supplier",
        competitor="Prime-Line N 7534",
        risk_notes=["Pivot diameter and door thickness matter", "Compatibility varies by door"],
    ),
    IdeaPlan(
        idea="Shower Door Roller Replacement Kit",
        category="Bathroom repair",
        why_interesting="Repair sliding shower doors with worn rollers and bearings.",
        notes="Compatibility matters; separate roller diameter, wheel thickness, and screw size.",
        keywords="shower door roller replacement",
        sold="shower door roller replacement sold",
        active="shower door wheel replacement kit",
        supplier="shower door roller supplier",
        competitor="shower door roller kit",
        risk_notes=["Diameter and screw size matter", "Top/bottom fit can vary"],
    ),
    IdeaPlan(
        idea="Toilet Tank Flush Lever Replacement Kit",
        category="Bathroom repair",
        why_interesting="Replace broken or loose toilet tank handles and flush levers.",
        notes="Compatibility matters; front, side, angle, and adjustable-arm variants may differ.",
        keywords="toilet tank flush lever replacement",
        sold="toilet tank flush lever sold",
        active="toilet tank handle replacement",
        supplier="toilet tank lever supplier",
        competitor="toilet tank lever replacement",
        risk_notes=["Mount type matters", "Adjustable arm fit matters"],
    ),
    IdeaPlan(
        idea="Dryer Vent Cleaning Brush Extension Rods",
        category="Laundry maintenance",
        why_interesting="Extend dryer vent cleaning reach with more rigid rod segments.",
        notes="Extension rod stiffness and connection strength matter.",
        keywords="dryer vent cleaning brush extension rods",
        sold="dryer vent cleaning brush rods sold",
        active="dryer vent cleaning brush rods",
        supplier="dryer vent brush extension rods supplier",
        competitor="dryer vent brush extension rod kit",
        risk_notes=["Rod stiffness matters", "Connection strength matters"],
    ),
    IdeaPlan(
        idea="Garbage Disposal Wrench / Jam-Buster Tool",
        category="Kitchen repair",
        why_interesting="Manual tool for clearing jammed garbage disposals safely.",
        notes="Must fit specific disposal models; jam prevention is not universal.",
        keywords="garbage disposal wrench",
        sold="garbage disposal wrench sold",
        active="garbage disposal wrench tool",
        supplier="garbage disposal wrench supplier",
        competitor="garbage disposal jam buster tool",
        risk_notes=["Model fit matters", "Do not force a seized disposal"],
    ),
    IdeaPlan(
        idea="Sink Drain Hair Catcher Replacement Basket",
        category="Drain accessories",
        why_interesting="Replace broken or missing drain baskets and hair catchers.",
        notes="Drain size and basket fit matter.",
        keywords="sink drain hair catcher replacement basket",
        sold="sink drain hair catcher sold",
        active="drain hair catcher basket",
        supplier="sink drain basket supplier",
        competitor="hair catcher replacement basket",
        risk_notes=["Drain size fit matters", "Basket style varies"],
    ),
    IdeaPlan(
        idea="Refrigerator Door Shelf Bar End Caps",
        category="Appliance repair",
        why_interesting="Replace missing end caps that hold fridge shelf bars in place.",
        notes="Model fit matters and end cap shape varies by refrigerator brand.",
        keywords="refrigerator door shelf bar end caps",
        sold="refrigerator shelf end caps sold",
        active="fridge shelf end caps",
        supplier="refrigerator shelf end caps supplier",
        competitor="fridge shelf cap replacement",
        risk_notes=["Brand/model fit matters", "End cap shapes vary"],
    ),
    IdeaPlan(
        idea="Window Blind Wand Tilt Mechanism Repair Kit",
        category="Window treatments",
        why_interesting="Repair broken blind wand tilt mechanisms instead of replacing the blinds.",
        notes="Tilt rod size and wand connector fit matter.",
        keywords="window blind wand tilt mechanism repair kit",
        sold="blind wand tilt repair kit sold",
        active="blind wand tilt repair kit",
        supplier="window blind wand supplier",
        competitor="blind tilt mechanism repair",
        risk_notes=["Tilt rod size matters", "Connector fit varies"],
    ),
    IdeaPlan(
        idea="Cabinet Shelf Support Pegs with Locking Clips",
        category="Cabinet hardware",
        why_interesting="Stop shelves from slipping with locking shelf support pegs.",
        notes="Peg diameter and clip style matter.",
        keywords="cabinet shelf support pegs with locking clips",
        sold="shelf support peg clips sold",
        active="shelf support peg clips",
        supplier="cabinet shelf support peg supplier",
        competitor="locking shelf peg kit",
        risk_notes=["Peg diameter matters", "Locking clip styles vary"],
    ),
    IdeaPlan(
        idea="Screen Door Latch Strike Plate Repair Kit",
        category="Door hardware",
        why_interesting="Repair loose or misaligned screen door latches and strike plates.",
        notes="Hole spacing and latch style matter.",
        keywords="screen door latch strike plate repair kit",
        sold="screen door strike plate sold",
        active="screen door strike plate repair",
        supplier="screen door strike plate supplier",
        competitor="screen door latch strike plate kit",
        risk_notes=["Hole spacing matters", "Latch style matters"],
    ),
]


def _top_values(rows: list[ResearchSearchResult], limit: int = 3) -> list[str]:
    values: list[str] = []
    for row in rows:
        title = (row.title or "").strip()
        if title and title not in values:
            values.append(title)
        if len(values) >= limit:
            break
    return values


def _status_rank(status: str | None) -> int:
    order = {"SHORTLIST": 0, "NEEDS_SOLD_PROOF": 1, "WATCH": 2, "REJECT": 3}
    return order.get((status or "").upper(), 99)


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = [
        "idea",
        "idea_id",
        "campaign_id",
        "scout_status",
        "scout_score",
        "scout_confidence",
        "buyer_problem_score",
        "active_market_score",
        "supplier_path_score",
        "margin_potential_score",
        "compatibility_risk_score",
        "evidence_friction_score",
        "reason",
        "next_step",
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        vals = []
        for key in headers:
            val = row.get(key)
            if isinstance(val, str):
                vals.append(val.replace("|", "\\|"))
            elif val is None:
                vals.append("—")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    run_started = datetime.now()
    db = SessionLocal()
    try:
        campaign_service = CampaignService(db)
        discovery = DiscoveryService(db)
        broker = ResearchSearchBroker(db)

        campaign = campaign_service.create_campaign(
            DiscoveryCampaignCreate(
                name=f"Opportunity Scout Batch {run_started:%Y-%m-%d}",
                goal="Pre-validation opportunity scout batch using local search only.",
                category="Home maintenance",
                budget_limit_usd=0.0,
                max_ideas=len(PLANS),
                max_products_to_promote=0,
                status="RUNNING",
                created_by="codex",
            )
        )

        results: list[dict[str, Any]] = []

        for plan in PLANS:
            idea = discovery.create_idea(
                ProductIdeaCreate(
                    idea_name=plan.idea,
                    category=plan.category,
                    campaign_id=campaign.id,
                    source_platform="Local search broker",
                    why_interesting=plan.why_interesting,
                    notes=f"{plan.notes} Pre-validation scout only.",
                    status="NEW_IDEA",
                )
            )

            search_specs = [
                ("KEYWORD_DEMAND", plan.keywords),
                ("SOLD_EVIDENCE", plan.sold),
                ("ACTIVE_LISTING", plan.active),
                ("SUPPLIER", plan.supplier),
                ("COMPETITOR", plan.competitor),
            ]

            search_summary: dict[str, Any] = {
                "keyword_signals": [plan.keywords],
                "active_listing_candidates": [],
                "competitor_candidates": [],
                "supplier_candidates": [],
                "risk_notes": plan.risk_notes,
            }
            counts_by_intent: dict[str, dict[str, int]] = {}

            for intent, query in search_specs:
                response = broker.search(
                    ResearchSearchRequest(
                        query=query,
                        intent=intent,  # type: ignore[arg-type]
                        providers=["SEARXNG", "OPENSERP"],
                        max_results=10,
                        idea_id=idea.id,
                        campaign_id=campaign.id,
                        store_results=True,
                    )
                )
                stored_rows = discovery.db.query(ResearchSearchResult).filter(
                    ResearchSearchResult.idea_id == idea.id,
                    ResearchSearchResult.campaign_id == campaign.id,
                    ResearchSearchResult.intent == intent,
                ).order_by(ResearchSearchResult.created_at.desc()).all()

                counts_by_intent[intent] = {
                    "result_count": response.result_count,
                    "stored_count": response.stored_count,
                    "deduped_count": response.deduped_count,
                }

                if intent == "ACTIVE_LISTING":
                    search_summary["active_listing_candidates"].extend(_top_values(stored_rows, 5))
                elif intent == "COMPETITOR":
                    search_summary["competitor_candidates"].extend(_top_values(stored_rows, 5))
                elif intent == "SUPPLIER":
                    search_summary["supplier_candidates"].extend(_top_values(stored_rows, 5))
                elif intent == "KEYWORD_DEMAND":
                    search_summary["keyword_signals"].extend(_top_values(stored_rows, 5))

            scout = discovery.opportunity_scout(
                idea.id,
                OpportunityScoutRequest(
                    campaign_id=campaign.id,
                    local_search_summary=search_summary,
                    keyword_signals=list(dict.fromkeys(search_summary["keyword_signals"])),
                    active_listing_candidates=[{"title": title} for title in search_summary["active_listing_candidates"]],
                    competitor_candidates=[{"title": title} for title in search_summary["competitor_candidates"]],
                    supplier_candidates=[{"title": title} for title in search_summary["supplier_candidates"]],
                    risk_notes=plan.risk_notes,
                ),
            )
            idea_row = db.query(ProductIdea).filter(ProductIdea.id == idea.id).first()
            stored_search_count = db.query(ResearchSearchResult).filter(
                ResearchSearchResult.idea_id == idea.id,
                ResearchSearchResult.campaign_id == campaign.id,
            ).count()

            results.append(
                {
                    "idea": plan.idea,
                    "idea_id": str(idea.id),
                    "campaign_id": str(campaign.id),
                    "scout_status": scout["scout_status"],
                    "scout_score": scout["scout_score"],
                    "scout_confidence": scout["confidence"],
                    "buyer_problem_score": scout["buyer_problem_score"],
                    "active_market_score": scout["active_market_score"],
                    "supplier_path_score": scout["supplier_path_score"],
                    "margin_potential_score": scout["margin_potential_score"],
                    "compatibility_risk_score": scout["compatibility_risk_score"],
                    "evidence_friction_score": scout["evidence_friction_score"],
                    "reason": scout["reason"],
                    "next_step": scout["next_step"],
                    "search_counts": counts_by_intent,
                    "stored_search_count": stored_search_count,
                    "idea_scout_status": idea_row.scout_status if idea_row else None,
                }
            )

        results.sort(key=lambda row: (_status_rank(row["scout_status"]), -(row["scout_score"] or 0), row["idea"]))

        output = {
            "campaign": {
                "id": str(campaign.id),
                "name": campaign.name,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            },
            "generated_at": datetime.now().isoformat(),
            "local_search_only": True,
            "count": len(results),
            "results": results,
        }

        reports_dir = Path("/Users/admin/CascadeProjects/is44ks-shop/resellos/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = reports_dir / "opportunity_scout_batch_report.json"
        md_path = reports_dir / "opportunity_scout_batch_report.md"
        json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(
            "\n".join(
                [
                    "# Opportunity Scout Batch",
                    "",
                    f"- campaign_id: `{campaign.id}`",
                    f"- campaign_name: `{campaign.name}`",
                    f"- generated_at: `{output['generated_at']}`",
                    f"- ideas: `{len(results)}`",
                    "",
                    _markdown_table(results),
                    "",
                    "## Notes",
                    "- Scout only. No promotion.",
                    "- Local search broker only. No DataForSEO.",
                    "- Scout status is early-stage only and does not change final decision or readiness.",
                ]
            ),
            encoding="utf-8",
        )

        print(json.dumps({"json_path": str(json_path), "md_path": str(md_path), "campaign_id": str(campaign.id), "ideas": len(results)}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
