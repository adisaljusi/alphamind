"""SQLAlchemy table definitions for the trading simulation."""

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SimulationRow(Base):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    tickers: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    agent_ids: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    agent_results: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
