"""
Finance Advisor AI conversation endpoint.
"""
from fastapi import APIRouter, Request
from app.schemas.advisor import AdvisorRequest, AdvisorResponse
from app.services.finance_advisor import finance_advisor_service

router = APIRouter(prefix="/api/v1/advisor", tags=["Advisor"])


@router.post("/ask", response_model=AdvisorResponse, summary="Ask financial advisory question")
async def ask_advisor(request: AdvisorRequest, raw_request: Request):
    """
    Submits question to the Gemini-powered personal finance advisor agent.
    Grounds responses in live market prices and official GST reference documents.
    """
    request_id = getattr(raw_request.state, "request_id", None)
    return await finance_advisor_service.advise(request=request, request_id=request_id)
