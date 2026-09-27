from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FactorContribution(BaseModel):
    factor: str
    weight_pct: float
    raw_score: float
    weighted_score: float
    evidence: str


class Signal(BaseModel):
    symbol: str
    direction: str  # "bullish" | "bearish" | "neutral"
    score: float  # 0-100, an analytical composite score - NOT a probability
    label: str  # Very Strong | Strong | Watch | Weak | Neutral
    contributions: list[FactorContribution]
    risks: list[str]
    invalidation: str
    scenarios: list[str]
    timestamp: datetime
    data_freshness: str
    sources: list[str]
    is_demo: bool = True
    disclaimer: str = (
        "This is an analytical score derived from historical/demo data. "
        "It is not a guarantee, not investment advice, and not a certainty "
        "of future price movement."
    )


class RiskRequest(BaseModel):
    account_size: float
    max_risk_pct: float
    entry: float
    stop_loss: float
    target: Optional[float] = None
    lot_size: int = 1


class RiskResult(BaseModel):
    max_monetary_risk: float
    risk_per_unit: float
    max_quantity: int
    max_lots: int
    position_size_value: float
    potential_loss: float
    potential_profit: Optional[float]
    risk_reward_ratio: Optional[float]
    warnings: list[str]
