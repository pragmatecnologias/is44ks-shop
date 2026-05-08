from app.db import Base
from app.models.portfolio import ShopConcept, ProductCollection, PortfolioItem
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
from app.models.production import (
    ProductionCampaign,
    ProductionCapability,
    MachineCandidate,
    MachineEvidence,
    MachineProductFamily,
    ProductionCostScenario,
    MachineDecision,
    machine_capabilities,
)

# Aliases for backwards compatibility - avoid duplicate class definitions
from app.models.supplier import MarketplaceResearch as MR, CompetitorListing as CL

__all__ = [
    "Base",
    "ShopConcept",
    "ProductCollection",
    "PortfolioItem",
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
    "ProductionCampaign",
    "ProductionCapability",
    "MachineCandidate",
    "MachineEvidence",
    "MachineProductFamily",
    "ProductionCostScenario",
    "MachineDecision",
    "machine_capabilities",
]
