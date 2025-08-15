# api/app/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, Integer, Numeric, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
import uuid
from datetime import datetime, date

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=None, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stripe_sub_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

class Game(Base):
    __tablename__ = "games"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    game_date: Mapped[date] = mapped_column(Date, nullable=False)
    league: Mapped[str] = mapped_column(Text, nullable=False)
    home_abbr: Mapped[str] = mapped_column(Text, nullable=False)
    away_abbr: Mapped[str] = mapped_column(Text, nullable=False)
    venue: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    model_version: Mapped[str] = mapped_column(Text, nullable=False)
    p_home_win: Mapped[float] = mapped_column(Numeric, nullable=False)
    expected_total: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    pred_home_runs: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    pred_away_runs: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    extras_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class Outcome(Base):
    __tablename__ = "outcomes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    actual_home_runs: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    actual_away_runs: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    winner: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
