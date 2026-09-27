from datetime import datetime, timezone

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}


@router.get("/system/status")
async def system_status():
    settings = get_settings()
    return {
        "application": settings.app_name,
        "version": __version__,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc),
        "database": {"status": "not_configured", "note": "running in-memory demo mode; Postgres integration is on the roadmap"},
        "redis": {"status": "not_configured", "note": "running without cache; Redis integration is on the roadmap"},
        "providers": settings.provider_status(),
        "workers": {"status": "not_running", "note": "background workers (alerts, scheduled scans) are on the roadmap"},
        "websocket": {"status": "available", "endpoints": ["/ws/market"]},
    }
