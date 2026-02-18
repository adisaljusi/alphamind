"""Build market context prompts for agent decision-making."""

from trading_sim.models.market import MarketSnapshot
from trading_sim.models.portfolio import Portfolio


def build_market_prompt(
    snapshot: MarketSnapshot,
    history: list[MarketSnapshot],
    portfolio: Portfolio,
    prices: dict[str, float],
) -> str:
    """Build a prompt describing current market state and portfolio for an agent."""
    lines: list[str] = []

    lines.append(f"=== Trading Day: {snapshot.date} (Day {snapshot.day_index + 1}/{snapshot.total_days}) ===\n")

    # Current prices
    lines.append("CURRENT MARKET DATA:")
    for ticker, bar in sorted(snapshot.prices.items()):
        lines.append(
            f"  {ticker}: Open=${bar.open:.2f} High=${bar.high:.2f} "
            f"Low=${bar.low:.2f} Close=${bar.close:.2f} Vol={bar.volume:,}"
        )

    # Recent price history (last 5 days if available)
    recent = history[-5:] if len(history) > 5 else history
    if recent:
        lines.append("\nRECENT PRICE HISTORY (close prices):")
        tickers = sorted(snapshot.prices.keys())
        header = "  Date       " + "  ".join(f"{t:>10}" for t in tickers)
        lines.append(header)
        for snap in recent:
            row = f"  {snap.date}  "
            row += "  ".join(
                f"${snap.prices[t].close:>9.2f}" if t in snap.prices else f"{'N/A':>10}"
                for t in tickers
            )
            lines.append(row)

    # Portfolio state
    total_value = portfolio.value_at_prices(prices)
    lines.append(f"\nYOUR PORTFOLIO (Total Value: ${total_value:,.2f}):")
    lines.append(f"  Cash: ${portfolio.cash:,.2f}")
    if portfolio.holdings:
        for ticker, holding in sorted(portfolio.holdings.items()):
            current_price = prices.get(ticker, holding.avg_cost)
            market_value = holding.quantity * current_price
            pnl = (current_price - holding.avg_cost) * holding.quantity
            lines.append(
                f"  {ticker}: {holding.quantity} shares @ avg ${holding.avg_cost:.2f} "
                f"(mkt value: ${market_value:,.2f}, P&L: ${pnl:+,.2f})"
            )
    else:
        lines.append("  No holdings")

    lines.append("\nAVAILABLE TICKERS: " + ", ".join(sorted(snapshot.prices.keys())))
    lines.append(
        "\nMake your trading decision. You may BUY, SELL, or HOLD. "
        "If buying or selling, specify the ticker, quantity, and your reasoning."
    )

    return "\n".join(lines)
