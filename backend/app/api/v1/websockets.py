"""Simulated live market WebSocket.

There is no real-time feed in this build. `/ws/market` pushes the demo
provider's current (deterministically-jittered) quotes on an interval so
the frontend can exercise its live-update code paths. Every payload is
flagged `is_demo: true`.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.providers.demo_market_data import get_demo_market_data_provider

router = APIRouter()
logger = logging.getLogger("marketpulse.ws")

PUSH_INTERVAL_SECONDS = 3


@router.websocket("/ws/market")
async def market_stream(websocket: WebSocket):
    await websocket.accept()
    provider = get_demo_market_data_provider()
    try:
        while True:
            indices = await provider.get_index_quotes()
            await websocket.send_json(
                {
                    "type": "market_update",
                    "is_demo": True,
                    "indices": [i.model_dump(mode="json") for i in indices],
                }
            )
            await asyncio.sleep(PUSH_INTERVAL_SECONDS)
    except WebSocketDisconnect:
        logger.info("market websocket client disconnected")
