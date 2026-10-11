"""
Central API Router combining all sub-routers.
"""
from fastapi import APIRouter
from app.api.routes import advisor, documents, health, prices

api_router = APIRouter()

# Include health routes at root
api_router.include_router(health.router)

# Include v1 endpoints
api_router.include_router(prices.router)
api_router.include_router(documents.router)
api_router.include_router(advisor.router)
