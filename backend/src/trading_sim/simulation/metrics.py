"""Performance metrics calculation."""

import math

from trading_sim.models.results import PerformanceMetrics
from trading_sim.models.trades import TradeAction, TradeDecision


def calculate_metrics(
    portfolio_history: list[float],
    trades: list[TradeDecision],
    initial_capital: float,
) -> PerformanceMetrics:
    """Calculate performance metrics from portfolio history and trade log."""
    if len(portfolio_history) < 2:
        return PerformanceMetrics()

    # Total return
    final_value = portfolio_history[-1]
    total_return_pct = ((final_value - initial_capital) / initial_capital) * 100

    # Daily returns
    daily_returns: list[float] = []
    for i in range(1, len(portfolio_history)):
        prev = portfolio_history[i - 1]
        if prev > 0:
            daily_returns.append((portfolio_history[i] - prev) / prev)

    # Sharpe ratio (annualized, assuming 252 trading days, risk-free rate = 0)
    sharpe_ratio = 0.0
    if daily_returns:
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / max(len(daily_returns) - 1, 1)
        std_return = math.sqrt(variance)
        if std_return > 0:
            sharpe_ratio = round((mean_return / std_return) * math.sqrt(252), 2)

    # Max drawdown
    max_drawdown_pct = 0.0
    peak = portfolio_history[0]
    for value in portfolio_history:
        if value > peak:
            peak = value
        drawdown = ((peak - value) / peak) * 100 if peak > 0 else 0.0
        if drawdown > max_drawdown_pct:
            max_drawdown_pct = drawdown

    # Win rate (trades that were profitable)
    actual_trades = [t for t in trades if t.action != TradeAction.HOLD]
    total_trades = len(actual_trades)
    wins = sum(1 for t in actual_trades if t.action == TradeAction.SELL and t.confidence > 0.5)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0

    return PerformanceMetrics(
        total_return_pct=round(total_return_pct, 2),
        sharpe_ratio=sharpe_ratio,
        max_drawdown_pct=round(max_drawdown_pct, 2),
        win_rate=round(win_rate, 1),
        total_trades=total_trades,
    )
