from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.models.supplier import ProfitAnalysis
from app.schemas.product_schema import ProfitAnalysisCreate, ProfitAnalysisUpdate


class ProfitService:
    def __init__(self, db: Session):
        self.db = db

    def create_analysis(self, product_id: uuid.UUID, data: ProfitAnalysisCreate) -> ProfitAnalysis:
        analysis = ProfitAnalysis(
            product_id=product_id,
            scenario_name=data.scenario_name,
            expected_sale_price=data.expected_sale_price,
            product_cost=data.product_cost,
            import_shipping_per_unit=data.import_shipping_per_unit,
            landed_cost=data.landed_cost or (data.product_cost + data.import_shipping_per_unit),
            marketplace_fee=data.marketplace_fee,
            us_shipping=data.us_shipping,
            packaging_cost=data.packaging_cost,
            return_allowance=data.return_allowance,
            ad_cost=data.ad_cost,
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        self._calculate_profit_metrics(analysis)
        return analysis

    def _calculate_profit_metrics(self, analysis: ProfitAnalysis) -> None:
        landed_cost = float(analysis.landed_cost or 0)
        marketplace_fee = float(analysis.marketplace_fee or 0)
        us_shipping = float(analysis.us_shipping or 0)
        packaging_cost = float(analysis.packaging_cost or 0)
        return_allowance = float(analysis.return_allowance or 0)
        ad_cost = float(analysis.ad_cost or 0)
        sale_price = float(analysis.expected_sale_price or 0)

        total_cost = landed_cost + marketplace_fee + us_shipping + packaging_cost + return_allowance + ad_cost
        net_profit = sale_price - total_cost
        margin = (net_profit / sale_price * 100) if sale_price > 0 else 0
        roi = (net_profit / landed_cost * 100) if landed_cost > 0 else 0
        break_even = total_cost

        analysis.estimated_net_profit = net_profit
        analysis.margin_percent = margin
        analysis.roi_percent = roi
        analysis.break_even_price = break_even

        if net_profit < 0:
            analysis.verdict = "LOSS"
        elif margin >= 30:
            analysis.verdict = "EXCELLENT"
        elif margin >= 20:
            analysis.verdict = "GOOD"
        elif margin >= 10:
            analysis.verdict = "ACCEPTABLE"
        else:
            analysis.verdict = "MARGINAL"

        self.db.commit()
        self.db.refresh(analysis)

    def get_analyses(self, product_id: uuid.UUID) -> list[ProfitAnalysis]:
        return self.db.query(ProfitAnalysis).filter(ProfitAnalysis.product_id == product_id).all()

    def get_analysis(self, analysis_id: uuid.UUID) -> Optional[ProfitAnalysis]:
        return self.db.query(ProfitAnalysis).filter(ProfitAnalysis.id == analysis_id).first()

    def update_analysis(self, analysis_id: uuid.UUID, data: ProfitAnalysisUpdate) -> Optional[ProfitAnalysis]:
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return None
        update = data.model_dump(exclude_unset=True)
        for key, value in update.items():
            setattr(analysis, key, value)
        self.db.commit()
        self.db.refresh(analysis)
        self._calculate_profit_metrics(analysis)
        return analysis

    def delete_analysis(self, analysis_id: uuid.UUID) -> bool:
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return False
        self.db.delete(analysis)
        self.db.commit()
        return True
