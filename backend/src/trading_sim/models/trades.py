"""Trade decision schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TradeAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class TradeDecision(BaseModel):
    """Structured output from an AI trading agent."""

    agent_id: str
    timestamp: datetime
    ticker: str
    action: TradeAction
    quantity: int = Field(ge=0, description="Number of shares")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in decision 0-1")
    reasoning: str = Field(description="LLM's reasoning for this trade")
    price_at_decision: float = Field(gt=0)
