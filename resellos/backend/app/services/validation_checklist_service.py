from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.product import Product
from app.models.product_validation import ProductDemandResearch, ProductTrendResearch, ProductValidationSummary
from app.models.supplier import AgentReport, ProductSource
from app.services.agent_utils import agent_data
from app.services.demand_research_service import score_search_volume
from app.services.trend_research_service import score_seasonality_risk, score_trend_direction


def _json_load(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            import json

            return json.loads(value)
        except Exception:
            return default
    return default


def _status_from_score(score: int, *, fail_threshold: int = 35, warn_threshold: int = 65) -> str:
    if score >= warn_threshold:
        return "PASS"
    if score >= fail_threshold:
        return "WARNING"
    return "FAIL"


class ValidationChecklistService:
    def __init__(self, db: Session):
        self.db = db

    def _latest_agent(self, product_id: uuid.UUID, agent_name: str) -> dict[str, Any]:
        report = (
            self.db.query(AgentReport)
            .filter(AgentReport.product_id == product_id, AgentReport.agent_name == agent_name)
            .order_by(AgentReport.created_at.desc(), AgentReport.id.desc())
            .first()
        )
        if not report or not report.output_json:
            return {}
        return _json_load(report.output_json, {})

    def _latest_validation_rows(self, product_id: uuid.UUID) -> tuple[list[ProductDemandResearch], list[ProductTrendResearch]]:
        demand_rows = self.db.query(ProductDemandResearch).filter(ProductDemandResearch.product_id == product_id).order_by(ProductDemandResearch.updated_at.desc()).all()
        trend_rows = self.db.query(ProductTrendResearch).filter(ProductTrendResearch.product_id == product_id).order_by(ProductTrendResearch.updated_at.desc()).all()
        return demand_rows, trend_rows

    def _latest_primary_source(self, product_id: uuid.UUID) -> ProductSource | None:
        return (
            self.db.query(ProductSource)
            .filter(ProductSource.product_id == product_id)
            .order_by(ProductSource.is_primary.desc().nullslast(), ProductSource.created_at.desc())
            .first()
        )

    def _score_demand(self, demand_rows: list[ProductDemandResearch], demand_agent: dict[str, Any]) -> dict[str, Any]:
        if demand_agent:
            score = int(demand_agent.get("demand_score") or 0)
            status = str(demand_agent.get("demand_status") or "UNKNOWN").upper()
            summary = f"{demand_agent.get('best_keyword') or 'Keyword demand'} · {demand_agent.get('main_demand_blocker') or 'Demand signal captured.'}"
            next_action = str(demand_agent.get("next_action") or "")
        elif demand_rows:
            best_row = max(demand_rows, key=lambda row: (int(row.demand_score or 0), int(row.monthly_search_volume or 0)))
            score = int(best_row.demand_score or score_search_volume(best_row.monthly_search_volume))
            status = "PASS" if score >= 65 else "WARNING" if score >= 35 else "FAIL"
            summary = f"{best_row.keyword} · {best_row.monthly_search_volume or 'No'} monthly search volume."
            next_action = "Collect more keyword demand data."
        else:
            score = 0
            status = "UNKNOWN"
            summary = "No keyword demand research captured yet."
            next_action = "Add keyword demand data."
        return {"status": status, "score": score, "summary": summary, "next_action": next_action}

    def _score_trend(self, trend_rows: list[ProductTrendResearch], trend_agent: dict[str, Any]) -> dict[str, Any]:
        if trend_agent:
            score = int(trend_agent.get("trend_stability_score") or 0)
            raw_status = str(trend_agent.get("trend_status") or "UNKNOWN").upper()
            if raw_status == "EVERGREEN":
                status = "PASS"
            elif raw_status == "SEASONAL":
                status = "WARNING"
            elif raw_status in {"SPIKY", "DECLINING"}:
                status = "FAIL"
            elif raw_status in {"PASS", "FAIL", "WARNING", "UNKNOWN"}:
                status = raw_status
            else:
                status = "UNKNOWN"
            summary = f"{trend_agent.get('trend_direction') or 'Trend'} · {trend_agent.get('main_trend_blocker') or 'Trend signal captured.'}"
            next_action = str(trend_agent.get("next_action") or "")
        elif trend_rows:
            best_row = max(trend_rows, key=lambda row: (int(row.trend_stability_score or 0), int(row.evergreen_score or 0)))
            score = int(best_row.trend_stability_score or score_trend_direction(best_row.trend_direction))
            seasonality = str(best_row.seasonality_risk or "UNKNOWN").upper()
            if seasonality == "HIGH" or score < 35:
                status = "FAIL"
            elif seasonality == "MEDIUM" or score < 65:
                status = "WARNING"
            else:
                status = "PASS"
            summary = f"{best_row.keyword} · {best_row.trend_direction or 'UNKNOWN'} trend."
            next_action = "Collect more trend data."
        else:
            score = 0
            status = "UNKNOWN"
            summary = "No trend research captured yet."
            next_action = "Add trend research data."
        return {"status": status, "score": score, "summary": summary, "next_action": next_action}

    def _score_market(self, market: dict[str, Any]) -> dict[str, Any]:
        verified_active = int(market.get("verified_active_listing_count") or 0)
        score = min(100, verified_active * 10)
        if verified_active >= 10:
            status = "PASS"
        elif verified_active >= 5:
            status = "WARNING"
        elif verified_active > 0:
            status = "FAIL"
        else:
            status = "UNKNOWN"
        summary = f"{verified_active} verified active listings."
        next_action = "Add verified active listings." if verified_active < 5 else "Review pricing and competition."
        return {"status": status, "score": score, "summary": summary, "next_action": next_action}

    def _score_sold(self, market: dict[str, Any]) -> dict[str, Any]:
        verified_sold = int(market.get("verified_sold_listing_count") or 0)
        verified_sold_price_count = int(market.get("verified_sold_price_count") or 0)
        verified_sold_price_missing = bool(market.get("verified_sold_price_missing", verified_sold > 0 and verified_sold_price_count == 0))
        score = min(100, verified_sold_price_count * 10)
        if verified_sold_price_missing:
            status = "WARNING"
            summary = "Verified sold evidence exists, but verified sold price data is missing."
            next_action = "Capture verified sold prices from completed-sale proof."
        elif verified_sold_price_count >= 5:
            status = "PASS"
            summary = f"{verified_sold_price_count} verified sold prices."
            next_action = "Review profitability."
        elif verified_sold > 0:
            status = "WARNING"
            summary = f"{verified_sold} verified sold listings."
            next_action = "Add verified sold evidence."
        else:
            status = "UNKNOWN"
            summary = "No sold evidence captured yet."
            next_action = "Add verified sold evidence."
        return {"status": status, "score": score, "summary": summary, "next_action": next_action}

    def _score_supplier(self, product_id: uuid.UUID, decision: dict[str, Any], profit: dict[str, Any]) -> dict[str, Any]:
        source = self._latest_primary_source(product_id)
        current_landed_cost = float(profit.get("current_landed_cost") or 0)
        current_target_sale_price = float(profit.get("current_target_sale_price") or profit.get("target_sale_price") or 0)
        landed_cost_ratio = (current_landed_cost / current_target_sale_price) if current_target_sale_price > 0 else None
        gross_margin_percent = float(profit.get("gross_margin_percent") or 0) if profit.get("gross_margin_percent") is not None else None
        if landed_cost_ratio is None:
            status = "UNKNOWN"
            score = 0
            summary = "No landed cost ratio available yet."
            next_action = "Capture verified supplier economics."
        elif landed_cost_ratio <= settings.VALIDATION_TARGET_LANDED_COST_RATIO:
            status = "PASS"
            score = 100
            summary = f"Landed cost ratio {landed_cost_ratio:.0%} is excellent."
            next_action = "Economics look strong."
        elif landed_cost_ratio <= settings.VALIDATION_MAX_ACCEPTABLE_LANDED_COST_RATIO:
            status = "WARNING"
            score = 70
            summary = f"Landed cost ratio {landed_cost_ratio:.0%} is acceptable but not ideal."
            next_action = "Try to lower landed cost."
        elif landed_cost_ratio <= settings.VALIDATION_HIGH_RISK_LANDED_COST_RATIO:
            status = "WARNING"
            score = 40
            summary = f"Landed cost ratio {landed_cost_ratio:.0%} is weak."
            next_action = "Negotiate a lower landed cost or validate a higher sale price."
        else:
            status = "FAIL"
            score = 15
            summary = f"Landed cost ratio {landed_cost_ratio:.0%} is too high."
            next_action = "Find a much cheaper supplier."
        if source and source.verification_status != "USER_VERIFIED":
            summary = f"{summary} Supplier cost exists but is not verified."
            if status == "PASS":
                status = "WARNING"
        if gross_margin_percent is not None and gross_margin_percent < settings.MIN_ACCEPTABLE_MARGIN:
            score = min(score, 35)
            if status == "PASS":
                status = "WARNING"
        return {"status": status, "score": score, "summary": summary, "next_action": next_action, "landed_cost_ratio": landed_cost_ratio, "gross_margin_percent": gross_margin_percent}

    def _score_competition(self, competition: dict[str, Any]) -> dict[str, Any]:
        score = int(competition.get("listing_gap_score") or 0)
        can_compete = bool(competition.get("can_compete", False))
        if can_compete and score >= 70:
            status = "PASS"
            next_action = "Competition gap looks usable."
        elif can_compete and score >= 55:
            status = "WARNING"
            next_action = "Improve the competitive angle."
        elif score > 0:
            status = "FAIL"
            next_action = "Find a better angle or stronger differentiation."
        else:
            status = "UNKNOWN"
            next_action = "Capture competitor evidence."
        summary = f"Competition gap score {score}."
        return {"status": status, "score": score, "summary": summary, "next_action": next_action}

    def _score_risk(self, risk: dict[str, Any]) -> dict[str, Any]:
        risk_level = str(risk.get("risk_level") or "MEDIUM").upper()
        if risk_level == "LOW":
            status = "PASS"
            score = 90
            next_action = "Risk is acceptable."
        elif risk_level == "MEDIUM":
            status = "WARNING"
            score = 60
            next_action = "Review risk flags."
        elif risk_level == "HIGH":
            status = "FAIL"
            score = 30
            next_action = "Resolve risk flags before buying."
        else:
            status = "FAIL" if bool(risk.get("blocked")) else "UNKNOWN"
            score = 0 if bool(risk.get("blocked")) else 40
            next_action = "Resolve risk flags before moving forward."
        summary = risk.get("summary") or f"Risk level is {risk_level}."
        return {"status": status, "score": score, "summary": summary, "next_action": next_action}

    def build_checklist(self, product_id: uuid.UUID) -> dict[str, Any]:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        agent_rows = (
            self.db.query(AgentReport)
            .filter(AgentReport.product_id == product_id)
            .order_by(AgentReport.created_at.desc(), AgentReport.id.desc())
            .all()
        )
        reports: dict[str, dict[str, Any]] = {}
        for row in agent_rows:
            if row.agent_name not in reports:
                reports[row.agent_name] = {"output_json": _json_load(row.output_json, {})}
        market = agent_data(reports, "market_agent")
        demand_agent = agent_data(reports, "demand_agent")
        trend_agent = agent_data(reports, "trend_agent")
        competition = agent_data(reports, "competition_agent")
        profit = agent_data(reports, "profit_agent")
        decision = agent_data(reports, "decision_agent")
        risk = agent_data(reports, "risk_agent")

        demand_rows, trend_rows = self._latest_validation_rows(product_id)
        if not demand_agent and demand_rows:
            best_demand = demand_rows[0]
            demand_agent = {
                "best_keyword": best_demand.keyword,
                "demand_score": best_demand.demand_score,
                "monthly_search_volume": best_demand.monthly_search_volume,
                "main_demand_blocker": None,
                "next_action": None,
                "demand_status": "WARNING" if best_demand.demand_score >= 35 else "FAIL",
            }
        if not trend_agent and trend_rows:
            best_trend = trend_rows[0]
            trend_agent = {
                "trend_direction": best_trend.trend_direction or "UNKNOWN",
                "trend_stability_score": best_trend.trend_stability_score,
                "evergreen_score": best_trend.evergreen_score,
                "spike_risk_score": best_trend.spike_risk_score,
                "seasonality_risk": best_trend.seasonality_risk or "UNKNOWN",
                "trend_status": "WARNING" if best_trend.trend_stability_score >= 35 else "FAIL",
            }

        market_check = self._score_market(market)
        demand_check = self._score_demand(demand_rows, demand_agent)
        sold_check = self._score_sold(market)
        trend_check = self._score_trend(trend_rows, trend_agent)
        supplier_check = self._score_supplier(product_id, decision, profit)
        competition_check = self._score_competition(competition)
        risk_check = self._score_risk(risk)

        checks = {
            "market_presence": market_check,
            "search_demand": demand_check,
            "sold_demand": sold_check,
            "trend_stability": trend_check,
            "supplier_economics": supplier_check,
            "competition_gap": competition_check,
            "risk": risk_check,
        }

        overall_validation_score = round(sum(int(check["score"]) for check in checks.values()) / len(checks))
        evidence_complete = (
            int(market.get("verified_sold_listing_count") or 0) >= 5
            and int(market.get("verified_active_listing_count") or 0) >= 5
            and int(market.get("verified_competitor_count") or competition.get("verified_competitor_count") or 0) >= 3
            and str((self._latest_primary_source(product_id).verification_status if self._latest_primary_source(product_id) else "")).upper() == "USER_VERIFIED"
            and int(market.get("test_data_evidence_count") or 0) == 0
            and float(market.get("verification_coverage") or 0) >= 1.0
        )

        decision_buy_status = str(decision.get("buy_readiness_status") or "").upper()
        decision_recommendation = str(decision.get("recommendation") or "").upper()
        decision_research_verdict = str(decision.get("research_verdict") or "").upper()
        if decision_recommendation == "BUY_SAMPLE" or decision_buy_status in {"READY", "READY_FOR_SAMPLE"} or decision_research_verdict == "READY_FOR_SAMPLE":
            validation_readiness = "READY_FOR_SAMPLE"
        elif evidence_complete:
            validation_readiness = "WATCHLIST" if overall_validation_score >= 55 else "WEAK"
        elif overall_validation_score >= 70:
            validation_readiness = "WATCHLIST"
        elif overall_validation_score >= 35:
            validation_readiness = "WEAK"
        else:
            validation_readiness = "INCOMPLETE"

        main_blocker = (
            str(decision.get("main_blocker") or "").strip()
            or next((check["summary"] for check in checks.values() if check["status"] == "FAIL"), None)
            or "None"
        )
        next_action = (
            str(decision.get("next_action") or "").strip()
            or next((check.get("next_action") for check in checks.values() if check.get("next_action")), None)
            or "Collect more validation evidence."
        )

        summary = (
            self.db.query(ProductValidationSummary)
            .filter(ProductValidationSummary.product_id == product_id)
            .first()
        )
        if summary is None:
            summary = ProductValidationSummary(product_id=product_id)
            self.db.add(summary)

        summary.market_presence_status = market_check["status"]
        summary.search_demand_status = demand_check["status"]
        summary.sold_demand_status = sold_check["status"]
        summary.trend_status = trend_check["status"]
        summary.supplier_economics_status = supplier_check["status"]
        summary.competition_status = competition_check["status"]
        summary.risk_status = risk_check["status"]
        summary.market_presence_score = int(market_check["score"])
        summary.search_demand_score = int(demand_check["score"])
        summary.sold_demand_score = int(sold_check["score"])
        summary.trend_score = int(trend_check["score"])
        summary.supplier_economics_score = int(supplier_check["score"])
        summary.competition_score = int(competition_check["score"])
        summary.risk_score = int(risk_check["score"])
        summary.overall_validation_score = overall_validation_score
        summary.validation_readiness = validation_readiness
        summary.main_validation_blocker = main_blocker
        summary.next_validation_action = next_action
        summary.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(summary)

        return {
            "product_id": product_id,
            "market_presence": market_check,
            "search_demand": demand_check,
            "sold_demand": sold_check,
            "trend_stability": trend_check,
            "supplier_economics": supplier_check,
            "competition_gap": competition_check,
            "risk": risk_check,
            "final_readiness": validation_readiness,
            "main_blocker": main_blocker,
            "next_action": next_action,
            "overall_validation_score": overall_validation_score,
        }

    def get_checklist(self, product_id: uuid.UUID) -> dict[str, Any]:
        return self.build_checklist(product_id)

    def run_validation(self, product_id: uuid.UUID) -> dict[str, Any]:
        from app.services.agent_factory import build_agents
        from app.services.research_pipeline_service import ResearchPipelineService

        pipeline = ResearchPipelineService(self.db, build_agents())
        import asyncio

        asyncio.run(pipeline.run_research_pipeline(product_id))
        return self.build_checklist(product_id)
