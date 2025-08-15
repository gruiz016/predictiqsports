-- 0001_init.sql — Initial schema for MVP

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- API KEYS
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at TIMESTAMPTZ
);

-- SUBSCRIPTIONS
CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  stripe_customer_id TEXT,
  stripe_sub_id TEXT,
  plan TEXT CHECK (plan IN ('monthly','quarterly','yearly')),
  status TEXT CHECK (status IN ('active','past_due','canceled')),
  current_period_end TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- GAMES
CREATE TABLE IF NOT EXISTS games (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_date DATE NOT NULL,
  league TEXT NOT NULL DEFAULT 'MLB',
  home_abbr TEXT NOT NULL,
  away_abbr TEXT NOT NULL,
  venue TEXT,
  start_time_et TIMESTAMPTZ,
  sportsbook_line_home_ml NUMERIC,
  sportsbook_total NUMERIC,
  park_factor NUMERIC,
  weather_json JSONB
);

-- PREDICTIONS (staging/current)
CREATE TABLE IF NOT EXISTS predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  model_version TEXT NOT NULL,
  p_home_win NUMERIC NOT NULL,
  expected_total NUMERIC,
  pred_home_runs NUMERIC,
  pred_away_runs NUMERIC,
  confidence NUMERIC,
  extras_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- PREDICTION ARCHIVE (immutable/public)
CREATE TABLE IF NOT EXISTS prediction_archive (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  model_version_snapshot TEXT NOT NULL,
  p_home_win NUMERIC NOT NULL,
  expected_total NUMERIC,
  pred_home_runs NUMERIC,
  pred_away_runs NUMERIC,
  confidence NUMERIC,
  raw_json JSONB,
  sha256_chain TEXT, -- tamper-evident hash chain (computed by backend insert)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- OUTCOMES
CREATE TABLE IF NOT EXISTS outcomes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  actual_home_runs NUMERIC,
  actual_away_runs NUMERIC,
  winner TEXT CHECK (winner IN ('HOME','AWAY')),
  closed_at TIMESTAMPTZ,
  source TEXT
);

-- PARLAYS
CREATE TABLE IF NOT EXISTS parlays (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  stake_cents INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  expected_value_cents INTEGER,
  combined_decimal_odds NUMERIC,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- PARLAY LEGS
CREATE TABLE IF NOT EXISTS parlay_legs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  parlay_id UUID NOT NULL REFERENCES parlays(id) ON DELETE CASCADE,
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  market TEXT CHECK (market IN ('ML','TOTAL')),
  selection TEXT CHECK (selection IN ('HOME','AWAY','OVER','UNDER')),
  line NUMERIC,
  price_decimal NUMERIC,
  leg_probability NUMERIC,
  correlated_group_id TEXT
);

-- ODDS SNAPSHOTS
CREATE TABLE IF NOT EXISTS odds_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
  book TEXT,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  home_ml_decimal NUMERIC,
  away_ml_decimal NUMERIC,
  total NUMERIC,
  over_price_dec NUMERIC,
  under_price_dec NUMERIC
);

-- ACCURACY ROLLUPS
CREATE TABLE IF NOT EXISTS accuracy_rollups (
  window TEXT CHECK (window IN ('7d','30d','90d')),
  as_of_date DATE NOT NULL,
  win_pct NUMERIC,
  roi_pct NUMERIC,
  avg_confidence NUMERIC,
  n_picks INTEGER,
  PRIMARY KEY (window, as_of_date)
);

-- STRIPE EVENTS
CREATE TABLE IF NOT EXISTS stripe_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  type TEXT NOT NULL,
  payload_json JSONB NOT NULL,
  processed_at TIMESTAMPTZ
);

-- AUDIT LOG
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  entity TEXT,
  entity_id UUID,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  details_json JSONB
);

-- Immutability: prevent UPDATE/DELETE on prediction_archive
CREATE OR REPLACE FUNCTION deny_mutations() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'prediction_archive is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS prediction_archive_no_update ON prediction_archive;
CREATE TRIGGER prediction_archive_no_update
BEFORE UPDATE OR DELETE ON prediction_archive
FOR EACH ROW EXECUTE FUNCTION deny_mutations();
