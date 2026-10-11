"""
FastAPI Application Entry Point.
Configures CORS, Request ID middleware, structured logging, and global exception handlers.
"""
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure backend root directory is on sys.path for any invocation entrypoint
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.router import api_router
from app.core.config import get_settings

from app.core.exceptions import FinanceAdvisorException
from app.core.logging import logger
from app.repositories.vector_store import vector_store_repository
from app.schemas.common import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager: logs startup diagnostics."""
    settings = get_settings()
    logger.info("==================================================================")
    logger.info("FINANCE ADVISOR BACKEND STARTING UP")
    logger.info(f"Environment:       {settings.app_env}")
    logger.info(f"Host:              {settings.app_host}:{settings.app_port}")
    logger.info(f"Gemini Configured: {settings.is_gemini_configured}")
    logger.info(f"Model ID:          {settings.gemini_model}")
    logger.info(f"CORS Origins:      {settings.parsed_cors_origins}")

    # Inspect vector store index status
    status = vector_store_repository.get_status()
    logger.info(f"Vector Store:      {status['total_chunks']} chunks in collection '{status['collection_name']}'")
    logger.info("==================================================================")
    yield
    logger.info("FINANCE ADVISOR BACKEND SHUTTING DOWN")


def create_app() -> FastAPI:
    """Application factory constructing the configured FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title="Personal Finance AI Advisor Backend",
        description=(
            "Production-ready backend providing real-time bullion market data (XAU/XAG in INR), "
            "grounded GST and financial document retrieval, and Gemini 3.8 Flash agent orchestration."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 1. CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Request ID & Performance Logging Middleware
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Request-ID"] = req_id

        logger.info(
            f"[{req_id}] {request.method} {request.url.path} -> "
            f"HTTP {response.status_code} ({duration_ms:.2f}ms)"
        )
        return response

    # 3. Custom Domain Exception Handler
    @app.exception_handler(FinanceAdvisorException)
    async def finance_advisor_exception_handler(request: Request, exc: FinanceAdvisorException):
        req_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                status_code=exc.status_code,
                message=exc.message,
                details=exc.details,
                request_id=req_id,
            ).model_dump(),
        )

    # 4. Request Validation Error Handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="ValidationError",
                status_code=422,
                message="Invalid request payload or query parameters",
                details={"errors": exc.errors()},
                request_id=req_id,
            ).model_dump(),
        )

    # 5. Global Unhandled Exception Handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", None)
        logger.error(f"[{req_id}] Unhandled server exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="InternalServerError",
                status_code=500,
                message="An unexpected internal server error occurred. Please try again later.",
                details=None,
                request_id=req_id,
            ).model_dump(),
        )

    # 6. Mount API Router
    app.include_router(api_router)

    return app


app = create_app()
