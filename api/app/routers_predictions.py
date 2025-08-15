# api/app/routers_predictions.py
from fastapi import APIRouter, Depends, HTTPException
from math import prod
from .auth import require_auth
from .schemas import Prediction, ParlayEvalRequest, ParlayEvalResponse

router=APIRouter(prefix="/v1", tags=["predictions"])

@router.get("/predictions/history")
async def history(from_date:str|None=None, to_date:str|None=None):
    return [{
        "game_id":"uuid-1","date":"2025-08-01","home":"NYY","away":"BOS",
        "p_home_win":0.62,"expected_total":8.4,"pred_home_runs":5.1,"pred_away_runs":3.3,"confidence":0.78,
        "result":{"winner":"HOME","home_runs":6,"away_runs":3,"win":True}
    }]

@router.get("/accuracy")
async def accuracy(window:str="30d"):
    return {"window":window,"as_of":"2025-08-14","win_pct":0.586,"roi_pct":0.072,"n_picks":210}

@router.get("/predictions/today")
async def todays_predictions(user=Depends(require_auth)):
    return [Prediction(game_id="uuid-today-1",date="2025-08-15",home="NYY",away="BOS",p_home_win=0.60,expected_total=8.3,pred_home_runs=4.7,pred_away_runs=3.6,confidence=0.75)]

@router.post("/parlays/evaluate", response_model=ParlayEvalResponse)
async def evaluate_parlay(body:ParlayEvalRequest, user=Depends(require_auth)):
    if not body.legs: raise HTTPException(status_code=400, detail="No legs provided")
    combined = prod(l.price_decimal for l in body.legs)
    pwin = prod(max(0.0,min(1.0,l.leg_probability)) for l in body.legs)
    payout = int(round(body.stake_cents*combined - body.stake_cents))
    ev = pwin*payout - (1-pwin)*body.stake_cents
    return ParlayEvalResponse(combined_decimal_odds=round(combined,4), p_parlay_win=round(pwin,6), expected_value_cents=int(round(ev)), ev_positive=ev>=0)
