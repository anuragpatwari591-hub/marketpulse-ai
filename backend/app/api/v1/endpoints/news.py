from typing import Optional

from fastapi import APIRouter

from app.providers.demo_news import get_demo_news_provider

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
async def get_news(limit: int = 20, symbol: Optional[str] = None):
    provider = get_demo_news_provider()
    articles = await provider.get_latest(limit=limit, symbol=symbol)
    return {"is_demo": True, "items": articles}
