from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.product import Product
from app.models.supplier import AgentReport


class ListingService:
    def __init__(self, db: Session):
        self.db = db

    def get_listing_report(self, product_id: uuid.UUID) -> Optional[dict]:
        report = (
            self.db.query(AgentReport)
            .filter(AgentReport.product_id == product_id, AgentReport.agent_name == "listing")
            .first()
        )
        if report and report.output_json:
            import json
            return json.loads(report.output_json)
        return None

    def get_all_listing_reports(self, skip: int = 0, limit: int = 100) -> list[dict]:
        reports = (
            self.db.query(AgentReport)
            .filter(AgentReport.agent_name == "listing")
            .offset(skip)
            .limit(limit)
            .all()
        )
        results = []
        for r in reports:
            if r.output_json:
                import json
                data = json.loads(r.output_json)
                data["product_id"] = str(r.product_id)
                data["agent_report_id"] = str(r.id)
                results.append(data)
        return results
