import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("smartmail")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AI-powered newsletter creation, "
        "campaign management, email delivery, "
        "and analytics platform."
    ),
    docs_url="/docs" if settings.DEBUG else "/docs",
    redoc_url="/redoc" if settings.DEBUG else "/redoc",
)


# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
    ],
)


# ------------------------------------------------------------------
# Trusted hosts
# ------------------------------------------------------------------

allowed_hosts = [
    "localhost",
    "127.0.0.1",
]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)


# ------------------------------------------------------------------
# Request middleware
# ------------------------------------------------------------------

@app.middleware("http")
async def request_context(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        logger.exception(
            "Unhandled exception | "
            "request_id=%s | method=%s | path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        raise

    duration = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = (
        f"{duration:.4f}"
    )

    return response


# ------------------------------------------------------------------
# Security headers
# ------------------------------------------------------------------

@app.middleware("http")
async def security_headers(
    request: Request,
    call_next,
):
    response = await call_next(request)

    response.headers.setdefault(
        "X-Content-Type-Options",
        "nosniff",
    )

    response.headers.setdefault(
        "X-Frame-Options",
        "DENY",
    )

    response.headers.setdefault(
        "Referrer-Policy",
        "strict-origin-when-cross-origin",
    )

    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=()",
    )

    return response


# ------------------------------------------------------------------
# Exception handlers
# ------------------------------------------------------------------

@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = request.headers.get(
        "X-Request-ID",
        "unknown",
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed.",
            "request_id": request_id,
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = request.headers.get(
        "X-Request-ID",
        "unknown",
    )

    logger.exception(
        "Unhandled application error | "
        "request_id=%s",
        request_id,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
            "request_id": request_id,
        },
    )


# ------------------------------------------------------------------
# Health endpoints
# ------------------------------------------------------------------

@app.get(
    "/",
    tags=["Health"],
)
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ok",
    }


@app.get(
    "/health",
    tags=["Health"],
)
def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }


# ------------------------------------------------------------------
# API
# ------------------------------------------------------------------

app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)