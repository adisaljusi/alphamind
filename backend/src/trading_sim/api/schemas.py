"""Request/response schemas for the API layer."""

from datetime import date

from pydantic import BaseModel, Field


class CreateSimulationRequest(BaseModel):
    agent_ids: list[str] = Field(min_length=1, description="IDs of agents to include")
    tickers: list[str] | None = Field(default=None, description="Tickers to simulate (default: AAPL, GOOGL, MSFT, AMZN, TSLA)")
    start_date: date | None = Field(default=None, description="Simulation start date (default: 2024-01-02)")
    end_date: date | None = Field(default=None, description="Simulation end date (default: 2024-12-31)")


class UpdateAgentRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    persona_prompt: str | None = None
    model_provider: str | None = None
    model_id: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)
    initial_capital: float | None = Field(default=None, gt=0)
