"""
Live Integration Tests against real external endpoints and persistent Chroma DB.
Separately runnable. Never fabricates responses. Gated by actual credentials.
"""
import os
import pytest
from app.core.config import get_settings
from app.services.document_retrieval import document_retrieval_service
from app.services.market_data import market_data_service


@pytest.mark.asyncio
async def test_live_gold_market_api():
    """Live call to api.gold-api.com for Gold (XAU) in INR."""
    resp = await market_data_service.get_spot_price("gold")
    assert resp.asset == "Gold"
    assert resp.symbol == "XAU"
    assert resp.currency == "INR"
    assert resp.price_per_troy_ounce > 0
    assert resp.price_per_gram > 0
    assert resp.metadata.source == "Gold-API"


@pytest.mark.asyncio
async def test_live_silver_market_api():
    """Live call to api.gold-api.com for Silver (XAG) in INR."""
    resp = await market_data_service.get_spot_price("silver")
    assert resp.asset == "Silver"
    assert resp.symbol == "XAG"
    assert resp.currency == "INR"
    assert resp.price_per_troy_ounce > 0
    assert resp.price_per_gram > 0
    assert resp.metadata.source == "Gold-API"


def test_live_document_retrieval_from_chroma():
    """Live query against the indexed Chroma collection."""
    res = document_retrieval_service.search_documents("What is the GST rate on laptops?", top_k=2)
    assert res.total_results > 0
    assert len(res.chunks) > 0
    first_chunk = res.chunks[0]
    assert first_chunk.source != ""
    assert first_chunk.content != ""


@pytest.mark.asyncio
async def test_live_gemini_inference():
    """
    Live inference call to Gemini 3.8 Flash.
    SKIPPED if GEMINI_API_KEY is not configured in .env.
    """
    settings = get_settings()
    if not settings.is_gemini_configured:
        pytest.skip("BLOCKED: GEMINI_API_KEY is not configured in local .env. Live model inference skipped.")

    from app.services.gemini import gemini_model_factory
    model = gemini_model_factory.get_model()
    resp = await model.ainvoke("Say 'Finance Advisor Ready' and nothing else.")
    content_text = resp.content if isinstance(resp.content, str) else "".join(
        c.get("text", "") if isinstance(c, dict) else str(c) for c in resp.content
    )
    assert "Finance Advisor Ready" in content_text


