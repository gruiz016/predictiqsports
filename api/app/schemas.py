# api/app/schemas.py
from pydantic import BaseModel, EmailStr, Field
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class LoginResponse(BaseModel):
    token: str
    user_id: str
    email: EmailStr
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
    market: str
    selection: str
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
