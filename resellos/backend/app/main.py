from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
import app.models  # noqa: F401 - ensure SQLAlchemy models register
from app.routes import (
    products_router,
    supplier_router,
    dashboard_router,
    marketplace_router,
    profit_router,
    agents_router,
    discovery_router,
    research_router,
    vision_router,
    listings_router,
    inventory_router,
    sales_router,
)

app = FastAPI(title="ResellOS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(supplier_router)
app.include_router(dashboard_router)
app.include_router(marketplace_router)
app.include_router(profit_router)
app.include_router(agents_router)
app.include_router(discovery_router)
app.include_router(research_router)
app.include_router(vision_router)
app.include_router(listings_router)
app.include_router(inventory_router)
app.include_router(sales_router)


@app.get("/")
def root():
    return {"message": "ResellOS API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def _bootstrap_sqlite_schema():
    if settings.DATABASE_URL.startswith("sqlite"):
        from app.db import engine, Base

        Base.metadata.create_all(bind=engine)
