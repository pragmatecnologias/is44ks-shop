from __future__ import annotations

from app.agents import (
    CompetitionAgent,
    DecisionAgent,
    DemandAgent,
    ListingAgent,
    MarketAgent,
    ProfitAgent,
    ReorderAgent,
    RiskAgent,
    TrendAgent,
)
from app.llm import get_llm_provider


def build_agents() -> dict[str, object]:
    llm = get_llm_provider()
    return {
        "risk": RiskAgent(llm),
        "market": MarketAgent(llm),
        "demand": DemandAgent(llm),
        "trend": TrendAgent(llm),
        "competition": CompetitionAgent(llm),
        "profit": ProfitAgent(llm),
        "reorder": ReorderAgent(llm),
        "listing": ListingAgent(llm),
        "decision": DecisionAgent(llm),
    }
