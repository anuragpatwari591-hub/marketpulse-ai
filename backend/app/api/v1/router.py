from fastapi import APIRouter

from app.api.v1.endpoints import market, news, risk, screener, signals, stocks, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(market.router)
api_router.include_router(stocks.router)
api_router.include_router(screener.router)
api_router.include_router(signals.router)
api_router.include_router(news.router)
api_router.include_router(risk.router)
