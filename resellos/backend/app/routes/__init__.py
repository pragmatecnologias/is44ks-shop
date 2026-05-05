from fastapi import APIRouter

from app.routes.products import router as products_router, supplier_router
from app.routes.dashboard import router as dashboard_router
from app.routes.marketplace import router as marketplace_router
from app.routes.profit import router as profit_router
from app.routes.agents import router as agents_router
from app.routes.discovery import router as discovery_router
from app.routes.product_ideas import router as product_ideas_router
from app.routes.research import router as research_router
from app.routes.listings import router as listings_router
from app.routes.inventory import router as inventory_router
from app.routes.sales import router as sales_router

__all__ = [
    "products_router",
    "supplier_router",
    "dashboard_router",
    "marketplace_router",
    "profit_router",
    "agents_router",
    "discovery_router",
    "product_ideas_router",
    "research_router",
    "listings_router",
    "inventory_router",
    "sales_router",
]
