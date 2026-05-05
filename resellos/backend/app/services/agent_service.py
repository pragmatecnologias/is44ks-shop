from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.agent_report import AgentReport


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def save_report(self, product_id: uuid.UUID, agent_name: str, report_type: str,
                   input_json: str, output_json: str, summary: str,
                   confidence: Optional[str] = None) -> AgentReport:
        report = AgentReport(
            product_id=product_id,
            agent_name=agent_name,
            report_type=report_type,
            input_json=input_json,
            output_json=output_json,
            summary=summary,
            confidence=confidence,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_reports(self, product_id: uuid.UUID) -> list[AgentReport]:
        return self.db.query(AgentReport).filter(AgentReport.product_id == product_id).all()

    def get_report(self, report_id: uuid.UUID) -> Optional[AgentReport]:
        return self.db.query(AgentReport).filter(AgentReport.id == report_id).first()