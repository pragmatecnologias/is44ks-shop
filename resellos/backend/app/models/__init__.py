from app.db import Base
from app.models.product import Product
from app.models.campaign import DiscoveryCampaign, DiscoveryCampaignTask
from app.models.product_validation import ProductDemandResearch, ProductTrendResearch, ProductValidationSummary
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
    ProductIdea,
    DiscoveryTask,
    ProductDiscoveryIdea,
)
from app.models.external_research import ExternalResearchJob, EvidenceCandidate
from app.models.vision import VisionAnalysisReport

# Aliases for backwards compatibility - avoid duplicate class definitions
from app.models.supplier import MarketplaceResearch as MR, CompetitorListing as CL

__all__ = [
    "Base",
    "Product",
    "DiscoveryCampaign",
    "DiscoveryCampaignTask",
    "ProductDemandResearch",
    "ProductTrendResearch",
    "ProductValidationSummary",
    "ProductSource",
    "MarketplaceResearch",
    "CompetitorListing",
    "ProfitAnalysis",
    "AgentReport",
    "MarketplaceEvidence",
    "InventoryItem",
    "Sale",
    "ProductFile",
    "ProductIdea",
    "ProductDiscoveryIdea",
    "DiscoveryTask",
    "ExternalResearchJob",
    "EvidenceCandidate",
    "VisionAnalysisReport",
]
