# api/app/routers_predictions.py
from fastapi import APIRouter, Depends, HTTPException
from math import prod
from .auth import require_auth
from .schemas import Prediction, ParlayEvalRequest, ParlayEvalResponse

router = APIRouter(prefix="/v1", tags=["predictions"])

@router.get("/predictions/history")
async def history(from_date: str | None = None, to_date: str | None = None):
    # Seeded sample rows for UI demo; replace with DB query in Phase 3
    return [
  {
    "game_id": "uuid-1",
    "date": "2025-08-10",
    "home": "NYY",
    "away": "BOS",
    "p_home_win": 0.62,
    "expected_total": 8.4,
    "pred_home_runs": 5.1,
    "pred_away_runs": 3.3,
    "confidence": 0.78,
    "result": {
      "winner": "HOME",
      "home_runs": 6,
      "away_runs": 3,
      "win": True
    }
  },
  {
    "game_id": "uuid-2",
    "date": "2025-08-11",
    "home": "LAD",
    "away": "SF",
    "p_home_win": 0.55,
    "expected_total": 8.0,
    "pred_home_runs": 4.2,
    "pred_away_runs": 3.8,
    "confidence": 0.64,
    "result": {
      "winner": "AWAY",
      "home_runs": 3,
      "away_runs": 4,
      "win": False
    }
  },
  {
    "game_id": "uuid-3",
    "date": "2025-08-12",
    "home": "ATL",
    "away": "PHI",
    "p_home_win": 0.58,
    "expected_total": 9.1,
    "pred_home_runs": 5.0,
    "pred_away_runs": 4.1,
    "confidence": 0.69,
    "result": {
      "winner": "HOME",
      "home_runs": 7,
      "away_runs": 4,
      "win": True
    }
  },
  {
    "game_id": "uuid-4",
    "date": "2025-08-13",
    "home": "HOU",
    "away": "TEX",
    "p_home_win": 0.47,
    "expected_total": 8.7,
    "pred_home_runs": 4.1,
    "pred_away_runs": 4.6,
    "confidence": 0.55,
    "result": {
      "winner": "AWAY",
      "home_runs": 3,
      "away_runs": 6,
      "win": False
    }
  },
  {
    "game_id": "uuid-5",
    "date": "2025-08-14",
    "home": "CHC",
    "away": "STL",
    "p_home_win": 0.51,
    "expected_total": 8.2,
    "pred_home_runs": 4.3,
    "pred_away_runs": 3.9,
    "confidence": 0.58,
    "result": {
      "winner": "HOME",
      "home_runs": 5,
      "away_runs": 4,
      "win": True
    }
  }
]

@router.get("/accuracy")
async def accuracy(window: str = "30d"):
    return {"window": window, "as_of": "2025-08-14", "win_pct": 0.586, "roi_pct": 0.072, "n_picks": 210}

@router.get("/predictions/today")
async def todays_predictions(user=Depends(require_auth)):
    return [Prediction(
        game_id="uuid-today-1",
        date="2025-08-15",
        home="NYY",
        away="BOS",
        p_home_win=0.60,
        expected_total=8.3,
        pred_home_runs=4.7,
        pred_away_runs=3.6,
        confidence=0.75
    )]

@router.post("/parlays/evaluate", response_model=ParlayEvalResponse)
async def evaluate_parlay(body: ParlayEvalRequest, user=Depends(require_auth)):
    if not body.legs:
        raise HTTPException(status_code=400, detail="No legs provided")
    combined_decimal_odds = prod(leg.price_decimal for leg in body.legs)
    p_parlay_win = prod(max(0.0, min(1.0, leg.leg_probability)) for leg in body.legs)
    payout_cents = int(round(body.stake_cents * combined_decimal_odds - body.stake_cents))
    expected_value = p_parlay_win * payout_cents - (1 - p_parlay_win) * body.stake_cents
    return ParlayEvalResponse(
        combined_decimal_odds=round(combined_decimal_odds, 4),
        p_parlay_win=round(p_parlay_win, 6),
        expected_value_cents=int(round(expected_value)),
        ev_positive=expected_value >= 0
    )
