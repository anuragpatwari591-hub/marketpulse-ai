import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1.router import api_router
from app.api.v1.websockets import router as ws_router
from app.core.config import get_settings
from app.core.logging import configure_logging, new_request_id, request_id_ctx

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("marketpulse")

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="MarketPulse AI - Indian stock-market intelligence and research platform (demo-mode API).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    req_id = new_request_id()
    token = request_id_ctx.set(req_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_completed",
            extra={"extra_fields": {"path": request.url.path, "method": request.method, "duration_ms": duration_ms}},
        )
        request_id_ctx.reset(token)
    response.headers["X-Request-ID"] = req_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        extra={"extra_fields": {"path": request.url.path}},
        exc_info=exc,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["system"])
async def root_health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router)
