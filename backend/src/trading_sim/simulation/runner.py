"""Main simulation runner — orchestrates agents over market data."""

import asyncio
import logging
import uuid
from datetime import date

from trading_sim.agents.trading_agent import create_trading_agent, get_agent_decision
from trading_sim.config import AgentConfig
from trading_sim.models.market import MarketSnapshot
from trading_sim.models.portfolio import Holding, Portfolio
from trading_sim.models.results import AgentResult, SimulationResult, SimulationStatus
from trading_sim.models.trades import TradeDecision
from trading_sim.simulation.executor import execute_trade
from trading_sim.simulation.market_data import generate_mock_data
from trading_sim.simulation.metrics import calculate_metrics
from trading_sim.simulation.storage import save_simulation

logger = logging.getLogger(__name__)

# How often agents make decisions (every N trading days)
DECISION_INTERVAL = 5


async def _run_agent_simulation(
    config: AgentConfig,
    snapshots: list[MarketSnapshot],
) -> AgentResult:
    """Run a single agent through the entire market data sequence."""
    agent = create_trading_agent(config)
    portfolio = Portfolio(cash=config.initial_capital, holdings={})

    trades: list[TradeDecision] = []
    portfolio_history: list[float] = []
    date_labels: list[str] = []
    history: list[MarketSnapshot] = []

    for i, snapshot in enumerate(snapshots):
        prices = {t: bar.close for t, bar in snapshot.prices.items()}
        current_value = portfolio.value_at_prices(prices)
        portfolio_history.append(round(current_value, 2))
        date_labels.append(str(snapshot.date))

        # Agents decide every DECISION_INTERVAL days
        if i % DECISION_INTERVAL == 0 and i > 0:
            decision = await get_agent_decision(
                agent, config, snapshot, history, portfolio
            )
            trades.append(decision)
            portfolio = execute_trade(portfolio, decision, snapshot)

        history.append(snapshot)

    metrics = calculate_metrics(portfolio_history, trades, config.initial_capital)

    return AgentResult(
        agent_id=config.id,
        agent_name=config.name,
        portfolio=portfolio,
        trades=trades,
        portfolio_history=portfolio_history,
        date_labels=date_labels,
        metrics=metrics,
    )


async def run_simulation(
    agent_configs: list[AgentConfig],
    tickers: list[str] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sim_id: str | None = None,
) -> SimulationResult:
    """Run a full simulation with multiple agents on the same market data."""
    if sim_id is None:
        sim_id = str(uuid.uuid4())[:8]

    effective_start = start_date or date(2024, 1, 2)
    effective_end = end_date or date(2024, 12, 31)

    result = SimulationResult(
        id=sim_id,
        status=SimulationStatus.RUNNING,
        start_date=effective_start,
        end_date=effective_end,
        tickers=tickers or [],
        agent_ids=[c.id for c in agent_configs],
    )
    await save_simulation(result)

    try:
        snapshots = generate_mock_data(tickers, effective_start, effective_end)
        result.tickers = list(snapshots[0].prices.keys()) if snapshots else []

        # Run all agents concurrently
        tasks = [_run_agent_simulation(config, snapshots) for config in agent_configs]
        agent_results = await asyncio.gather(*tasks)

        for agent_result in agent_results:
            result.agent_results[agent_result.agent_id] = agent_result

        result.status = SimulationStatus.COMPLETED

    except Exception as e:
        logger.exception("Simulation %s failed", sim_id)
        result.status = SimulationStatus.FAILED
        result.error = str(e)

    await save_simulation(result)
    return result
