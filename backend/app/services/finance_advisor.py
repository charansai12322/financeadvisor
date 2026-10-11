"""
Finance Advisor Orchestration Service.
Coordinates Gemini LLM, Market Data tools, and Document Retrieval tools
to synthesize grounded financial advisory responses.
"""
import uuid
from typing import List, Optional
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from app.core.config import get_settings
from app.core.exceptions import (
    GeminiInferenceException,
    GeminiQuotaExceededException,
    GeminiRateLimitException,
    GeminiUnconfiguredException,
)
from app.core.logging import logger
from app.schemas.advisor import (
    AdvisorMarketItem,
    AdvisorRequest,
    AdvisorResponse,
    AdvisorSourceItem,
)
from app.services.document_retrieval import (
    DocumentRetrievalService,
    document_retrieval_service,
)
from app.services.gemini import gemini_model_factory
from app.services.market_data import (
    MarketDataService,
    market_data_service,
)
from app.utils.price_units import normalize_asset

SYSTEM_PROMPT = """You are a Personal Finance AI Advisor for Indian citizens.

You have access to these tools:
- search_finance_docs: Search official Indian government documents for GST rates, investment guidance, tax saving options, and financial education.
- get_market_price: Get live spot market prices for gold and silver in Indian Rupees.

Help the user by looking up the relevant data using your tools and giving clear, specific answers with actual numbers and rates. Always mention the source of your information. All monetary values should be in Indian Rupees (₹) unless specified otherwise.
Distinguish general financial educational guidance from personalized regulated investment advice. Never promise investment returns or make unauthorized buy/sell recommendations.
"""


def build_tools(m_service: MarketDataService, d_service: DocumentRetrievalService):
    """Factory creating LangChain tools bound to the active service instances."""

    @tool
    def search_finance_docs(question: str) -> str:
        """Search official Indian government financial documents for GST rates, tax provisions, and financial education."""
        return d_service.format_agent_tool_context(question=question, top_k=3)

    @tool
    def get_market_price(asset: str) -> str:
        """Get live spot market price for a financial asset in Indian Rupees. Supported assets: gold, silver."""
        norm = normalize_asset(asset)
        if not norm:
            return "Supported assets: gold, silver"
        import asyncio
        try:
            # Run async call in event loop if active or via asyncio.run
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        res = pool.submit(asyncio.run, m_service.get_spot_price(asset)).result()
                else:
                    res = loop.run_until_complete(m_service.get_spot_price(asset))
            except RuntimeError:
                res = asyncio.run(m_service.get_spot_price(asset))
            return res.formatted
        except Exception as e:
            return f"Could not fetch live market price for {asset}: {str(e)}"

    return [search_finance_docs, get_market_price]


class FinanceAdvisorService:
    """High-level service orchestrating tools and Gemini generation."""

    def __init__(
        self,
        m_service: Optional[MarketDataService] = None,
        d_service: Optional[DocumentRetrievalService] = None,
    ):
        self._settings = get_settings()
        self.market_service = m_service or market_data_service
        self.doc_service = d_service or document_retrieval_service
        self.tools = build_tools(self.market_service, self.doc_service)

    async def advise(self, request: AdvisorRequest, request_id: Optional[str] = None) -> AdvisorResponse:
        """
        Processes a user question through the LangGraph React agent.
        Extracts cited sources and market data for structured output.
        """
        req_id = request_id or str(uuid.uuid4())
        question = request.question.strip()

        if not self._settings.is_gemini_configured:
            raise GeminiUnconfiguredException(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your local .env file."
            )

        model = gemini_model_factory.get_model()
        agent = create_react_agent(
            model=model,
            tools=self.tools,
            prompt=SYSTEM_PROMPT,
        )

        try:
            logger.info(f"[{req_id}] Invoking agent for query: {question[:80]}...")
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": question}]
            })

            messages = result.get("messages", [])
            if not messages:
                raise GeminiInferenceException("Agent returned empty message trajectory")

            final_message = messages[-1]
            raw_content = getattr(final_message, "content", str(final_message))
            if isinstance(raw_content, list):
                answer = "".join(
                    c.get("text", "") if isinstance(c, dict) else str(c)
                    for c in raw_content
                ).strip()
            else:
                answer = str(raw_content).strip()


            # Inspect tool calls in message trajectory to populate sources and market data
            cited_sources: List[AdvisorSourceItem] = []
            cited_market_data: List[AdvisorMarketItem] = []

            for msg in messages:
                # ToolMessage contains tool execution outputs
                if hasattr(msg, "name") and msg.name == "search_finance_docs":
                    content_str = str(msg.content)
                    if "Source:" in content_str:
                        # Extract source metadata if present
                        cited_sources.append(
                            AdvisorSourceItem(
                                title="Official Reference Document",
                                source_file="CBIC GST / SEBI Reference",
                                page_label="Referenced Chunks",
                                snippet=content_str[:250],
                            )
                        )
                elif hasattr(msg, "name") and msg.name == "get_market_price":
                    content_str = str(msg.content)
                    if "Gold" in content_str or "Silver" in content_str:
                        asset_name = "Gold" if "Gold" in content_str else "Silver"
                        symbol = "XAU" if "Gold" in content_str else "XAG"
                        cited_market_data.append(
                            AdvisorMarketItem(
                                asset=asset_name,
                                symbol=symbol,
                                price_per_gram=0.0,
                                price_per_10g=0.0,
                                currency="INR",
                                source="Gold-API",
                            )
                        )

            return AdvisorResponse(
                answer=answer,
                sources=cited_sources,
                market_data=cited_market_data,
                model=self._settings.gemini_model,
                request_id=req_id,
            )

        except GeminiUnconfiguredException:
            raise
        except (GeminiRateLimitException, GeminiQuotaExceededException):
            raise
        except Exception as e:
            err_str = str(e)
            logger.error(f"[{req_id}] Agent execution failed: {err_str}")

            lower_err = err_str.lower()
            if "resource_exhausted" in lower_err or "429" in lower_err or "quota" in lower_err or "rate" in lower_err:
                if "quota" in lower_err or "billing" in lower_err or "credit" in lower_err:
                    raise GeminiQuotaExceededException(
                        message="Gemini API quota has been exhausted. Please verify your project quota or billing in Google AI Studio.",
                        details={"request_id": req_id, "error_type": "quota_exhausted"},
                    )
                else:
                    raise GeminiRateLimitException(
                        message="Gemini API rate limit reached. Please wait a moment before sending another request.",
                        details={"request_id": req_id, "error_type": "rate_limited"},
                    )

            raise GeminiInferenceException(
                message="Financial advisor agent inference failed. Please check network connectivity or try again.",
                details={"request_id": req_id, "error_type": "provider_error"},
            )


# Singleton advisor service
finance_advisor_service = FinanceAdvisorService()
