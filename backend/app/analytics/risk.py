"""Risk / position-sizing calculator. Never places orders - pure math."""
from __future__ import annotations

from app.schemas.signals import RiskRequest, RiskResult


def calculate_risk(req: RiskRequest) -> RiskResult:
    warnings: list[str] = []

    if req.account_size <= 0:
        raise ValueError("account_size must be positive")
    if not (0 < req.max_risk_pct <= 100):
        raise ValueError("max_risk_pct must be between 0 and 100")
    if req.lot_size <= 0:
        raise ValueError("lot_size must be positive")

    risk_per_unit = abs(req.entry - req.stop_loss)
    if risk_per_unit == 0:
        raise ValueError("entry and stop_loss cannot be equal")

    max_monetary_risk = req.account_size * (req.max_risk_pct / 100)
    max_quantity_raw = max_monetary_risk / risk_per_unit
    max_lots = int(max_quantity_raw // req.lot_size)
    max_quantity = max_lots * req.lot_size

    if max_quantity == 0:
        warnings.append(
            "Calculated position size is smaller than one lot; either increase account size/risk% "
            "or choose an instrument with a smaller lot size."
        )

    position_size_value = max_quantity * req.entry
    potential_loss = max_quantity * risk_per_unit
    potential_profit = None
    risk_reward = None
    if req.target is not None:
        reward_per_unit = abs(req.target - req.entry)
        potential_profit = max_quantity * reward_per_unit
        risk_reward = round(reward_per_unit / risk_per_unit, 2) if risk_per_unit else None
        if risk_reward is not None and risk_reward < 1.5:
            warnings.append(f"Risk/reward ratio is {risk_reward}, below the commonly used 1.5 minimum.")

    if position_size_value > req.account_size:
        warnings.append("Position size value exceeds account size - this assumes leverage/margin is available.")

    return RiskResult(
        max_monetary_risk=round(max_monetary_risk, 2),
        risk_per_unit=round(risk_per_unit, 2),
        max_quantity=max_quantity,
        max_lots=max_lots,
        position_size_value=round(position_size_value, 2),
        potential_loss=round(potential_loss, 2),
        potential_profit=round(potential_profit, 2) if potential_profit is not None else None,
        risk_reward_ratio=risk_reward,
        warnings=warnings,
    )
