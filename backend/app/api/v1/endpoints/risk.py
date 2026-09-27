from fastapi import APIRouter, HTTPException

from app.analytics.risk import calculate_risk
from app.schemas.signals import RiskRequest, RiskResult

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/calculate", response_model=RiskResult)
async def calculate(req: RiskRequest):
    try:
        return calculate_risk(req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
