from fastapi import APIRouter

from app.routes.products import router as products_router, supplier_router
from app.routes.marketplace import router as marketplace_router
from app.routes.profit import router as profit_router
from app.routes.agents import router as agents_router
from app.routes.research import router as research_router
from app.routes.listings import router as listings_router
from app.routes.inventory import router as inventory_router
from app.routes.sales import router as sales_router

__all__ = [
    "products_router",
    "supplier_router",
    "marketplace_router",
    "profit_router",
    "agents_router",
    "research_router",
    "listings_router",
    "inventory_router",
    "sales_router",
]