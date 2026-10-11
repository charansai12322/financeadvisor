"""
Advisor orchestration request and response schemas.
"""
from typing import List
from pydantic import BaseModel, Field


class AdvisorRequest(BaseModel):
    """User question submission for financial advisory."""
    question: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="User financial query (Gold/Silver prices, GST rules, or personal finance)",
        examples=["What is the current gold price in INR and what GST will I pay?"],
    )


class AdvisorSourceItem(BaseModel):
    """Document evidence citation used in synthesized answer."""
    title: str = Field(description="Document reference title")
    source_file: str = Field(description="Originating PDF filename")
    page_label: str = Field(description="Page reference e.g. 'Page 6'")
    snippet: str = Field(description="Extracted grounding excerpt")


class AdvisorMarketItem(BaseModel):
    """Live market data point utilized in the response."""
    asset: str = Field(description="Asset name (Gold or Silver)")
    symbol: str = Field(description="Commodity symbol (XAU or XAG)")
    price_per_gram: float = Field(description="Spot price per gram in INR")
    price_per_10g: float = Field(description="Spot price per 10 grams in INR")
    currency: str = Field(default="INR", description="Currency denomination")
    source: str = Field(default="Gold-API", description="Market data provider")


class AdvisorResponse(BaseModel):
    """Structured response from the Finance Advisor."""
    answer: str = Field(description="Synthesized advisor response text")
    sources: List[AdvisorSourceItem] = Field(default_factory=list, description="Grounding document sources cited")
    market_data: List[AdvisorMarketItem] = Field(default_factory=list, description="Market prices cited")
    model: str = Field(description="Gemini model identifier used for generation")
    request_id: str = Field(description="Unique request correlation ID")
