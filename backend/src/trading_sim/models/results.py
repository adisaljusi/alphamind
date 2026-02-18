"""Simulation result schemas."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field

from trading_sim.models.portfolio import Portfolio
from trading_sim.models.trades import TradeDecision


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PerformanceMetrics(BaseModel):
    total_return_pct: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown_pct: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0


class AgentResult(BaseModel):
    """Results for a single agent in a simulation."""

    agent_id: str
    agent_name: str
    portfolio: Portfolio
    trades: list[TradeDecision] = Field(default_factory=list)
    portfolio_history: list[float] = Field(
        default_factory=list,
        description="Portfolio value at each time step",
    )
    date_labels: list[str] = Field(
        default_factory=list,
        description="Date labels corresponding to portfolio_history",
    )
    metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)


class SimulationResult(BaseModel):
    """Full results of a simulation run."""

    id: str
    status: SimulationStatus = SimulationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    start_date: date
    end_date: date
    tickers: list[str]
    agent_ids: list[str]
    agent_results: dict[str, AgentResult] = Field(default_factory=dict)
    error: str | None = None


class SimulationSummary(BaseModel):
    """Lightweight summary for listing simulations."""

    id: str
    status: SimulationStatus
    created_at: datetime
    start_date: date
    end_date: date
    tickers: list[str]
    agent_ids: list[str]
