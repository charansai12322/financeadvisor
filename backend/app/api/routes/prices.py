"""
Market spot price endpoints.
"""
from fastapi import APIRouter
from app.schemas.prices import PriceResponse
from app.services.market_data import market_data_service

router = APIRouter(prefix="/api/v1/prices", tags=["Prices"])


@router.get("/gold", response_model=PriceResponse, summary="Get live spot Gold price in INR")
async def get_gold_price():
    """Fetches real-time spot gold (XAU) quote converted into Indian Rupees (INR)."""
    return await market_data_service.get_spot_price("gold")


@router.get("/silver", response_model=PriceResponse, summary="Get live spot Silver price in INR")
async def get_silver_price():
    """Fetches real-time spot silver (XAG) quote converted into Indian Rupees (INR)."""
    return await market_data_service.get_spot_price("silver")


@router.get("/{asset}", response_model=PriceResponse, summary="Get live spot price for supported asset")
async def get_asset_price(asset: str):
    """
    Fetches real-time commodity spot rate by alias.
    Supported assets: gold, silver, xau, xag.
    """
    return await market_data_service.get_spot_price(asset)
