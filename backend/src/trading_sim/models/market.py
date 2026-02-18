"""Market data schemas."""

from datetime import date

from pydantic import BaseModel, Field


class PriceBar(BaseModel):
    """OHLCV price bar for a single ticker on a single day."""

    ticker: str
    date: date
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: int = Field(ge=0)


class MarketSnapshot(BaseModel):
    """All available market data for a single trading day."""

    date: date
    prices: dict[str, PriceBar]
    day_index: int = Field(ge=0, description="Day number in the simulation")
    total_days: int = Field(gt=0, description="Total days in the simulation")
