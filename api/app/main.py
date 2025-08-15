# api/app/main.py
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import stripe

# --- Config ---
DEV_SKIP_AUTH = os.getenv("DEV_SKIP_AUTH", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI(title="Sports Prediction & Parlay API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth dependency ---
async def require_auth(authorization: str | None = Header(default=None)):
    if DEV_SKIP_AUTH:
        return {"user_id": "dev-user", "sub_active": True}
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    # TODO: validate JWT/token and subscription status
    if token == "demo":
        return {"user_id": "demo", "sub_active": True}
    raise HTTPException(status_code=403, detail="Forbidden")

# --- Schemas ---
class Prediction(BaseModel):
    game_id: str
    date: str
    home: str
    away: str
    p_home_win: float
    expected_total: float | None = None
    pred_home_runs: float | None = None
    pred_away_runs: float | None = None
    confidence: float | None = None

class ParlayLeg(BaseModel):
    game_id: str
    market: str  # "ML" or "TOTAL"
    selection: str  # "HOME"|"AWAY"|"OVER"|"UNDER"
    line: float | None = None
    price_decimal: float
    leg_probability: float

class ParlayEvalRequest(BaseModel):
    stake_cents: int = Field(ge=1)
    legs: list[ParlayLeg]

class ParlayEvalResponse(BaseModel):
    combined_decimal_odds: float
    p_parlay_win: float
    expected_value_cents: int
    ev_positive: bool

# --- Health ---
@app.get("/health")
async def health():
    return {"ok": True}

# --- Public endpoints ---
@app.get("/v1/predictions/history")
async def history(from_date: str | None = None, to_date: str | None = None):
    # Stubbed public data (replace with DB queries later)
    sample = [{
        "game_id": "uuid-1",
        "date": "2025-08-01",
        "home": "NYY",
        "away": "BOS",
        "p_home_win": 0.62,
        "expected_total": 8.4,
        "pred_home_runs": 5.1,
        "pred_away_runs": 3.3,
        "confidence": 0.78,
        "result": {"winner": "HOME", "home_runs": 6, "away_runs": 3, "win": True}
    }]
    return sample

@app.get("/v1/accuracy")
async def accuracy(window: str = "30d"):
    # Stub rollup (replace with DB)
    return {"window": window, "as_of": "2025-08-14", "win_pct": 0.586, "roi_pct": 0.072, "n_picks": 210}

# --- Private endpoints (require subscription) ---
@app.get("/v1/predictions/today")
async def todays_predictions(user=Depends(require_auth)):
    # Stub list (replace with DB or model service)
    return [Prediction(
        game_id="uuid-today-1",
        date="2025-08-14",
        home="NYY",
        away="BOS",
        p_home_win=0.60,
        expected_total=8.3,
        pred_home_runs=4.7,
        pred_away_runs=3.6,
        confidence=0.75
    )]

@app.post("/v1/parlays/evaluate", response_model=ParlayEvalResponse)
async def evaluate_parlay(body: ParlayEvalRequest, user=Depends(require_auth)):
    # Basic EV calculator (independent legs; correlation handling later)
    from math import prod
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

# --- Stripe webhook (safe no-op if secrets unset) ---
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not STRIPE_WEBHOOK_SECRET:
        # Accept silently in dev
        return {"ok": True, "skipped": True}

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # TODO: handle subscription events: checkout.session.completed, customer.subscription.updated/deleted, invoice.payment_failed
    return {"ok": True}
