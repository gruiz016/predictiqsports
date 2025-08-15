# api/app/routers_parlay.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from math import prod

from .access import require_active_subscription

router = APIRouter(prefix="/v1/parlay", tags=["parlay"])

class ParlayPick(BaseModel):
    market: str = Field(..., description="e.g., ML, Spread, Total")
    selection: str = Field(..., description="e.g., NYY ML or Over 8.5")
    odds_type: Literal["american","decimal"]
    odds: float

class BuildParlayRequest(BaseModel):
    stake: float = 10.0
    picks: List[ParlayPick]

class BuildParlayResponse(BaseModel):
    legs: int
    stake: float
    combined_decimal: float
    combined_american: int
    potential_payout: float
    potential_profit: float

def american_to_decimal(a: float) -> float:
    if a > 0:
        return 1 + (a / 100.0)
    else:
        return 1 + (100.0 / abs(a))

def decimal_to_american(d: float) -> int:
    if d >= 2.0:
        return int(round((d - 1) * 100))
    else:
        return int(round(-100 / (d - 1)))

@router.post("/build", response_model=BuildParlayResponse, dependencies=[Depends(require_active_subscription)])
async def build_parlay(payload: BuildParlayRequest):
    if not payload.picks:
        raise HTTPException(status_code=400, detail="No picks provided")
    decimal_odds = []
    for p in payload.picks:
        if p.odds_type == "decimal":
            decimal_odds.append(p.odds)
        else:
            decimal_odds.append(american_to_decimal(p.odds))
    combined_decimal = prod(decimal_odds)
    combined_american = decimal_to_american(combined_decimal)
    payout = round(payload.stake * combined_decimal, 2)
    profit = round(payout - payload.stake, 2)
    return BuildParlayResponse(
        legs=len(payload.picks),
        stake=payload.stake,
        combined_decimal=round(combined_decimal, 4),
        combined_american=combined_american,
        potential_payout=payout,
        potential_profit=profit,
    )
