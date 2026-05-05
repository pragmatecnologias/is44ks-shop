from app.db import Base
from app.models.product import Product
from app.models.supplier import (
    ProductSource,
    MarketplaceResearch,
    CompetitorListing,
    ProfitAnalysis,
    AgentReport,
    MarketplaceEvidence,
    InventoryItem,
    Sale,
    ProductFile,
    ProductDiscoveryIdea,
    DiscoveryTask,
)

# Aliases for backwards compatibility - avoid duplicate class definitions
from app.models.supplier import MarketplaceResearch as MR, CompetitorListing as CL

__all__ = [
    "Base",
    "Product",
    "ProductSource",
    "MarketplaceResearch",
    "CompetitorListing",
    "ProfitAnalysis",
    "AgentReport",
    "MarketplaceEvidence",
    "InventoryItem",
    "Sale",
    "ProductFile",
    "ProductDiscoveryIdea",
    "DiscoveryTask",
]
