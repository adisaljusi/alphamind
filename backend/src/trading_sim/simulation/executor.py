"""Trade execution — applies trade decisions to portfolios."""

from trading_sim.models.market import MarketSnapshot
from trading_sim.models.portfolio import Holding, Portfolio
from trading_sim.models.trades import TradeAction, TradeDecision


def execute_trade(
    portfolio: Portfolio,
    decision: TradeDecision,
    snapshot: MarketSnapshot,
) -> Portfolio:
    """Apply a trade decision to a portfolio, returning the updated portfolio.

    Validates the trade is feasible (enough cash for buys, enough shares for sells).
    Invalid trades are silently skipped (treated as holds).
    """
    ticker = decision.ticker
    price_bar = snapshot.prices.get(ticker)
    if price_bar is None:
        return portfolio

    price = price_bar.close

    if decision.action == TradeAction.BUY:
        cost = decision.quantity * price
        if cost > portfolio.cash or decision.quantity == 0:
            return portfolio

        new_holdings = dict(portfolio.holdings)
        existing = new_holdings.get(ticker)

        if existing is not None:
            total_qty = existing.quantity + decision.quantity
            total_cost = (existing.avg_cost * existing.quantity) + cost
            new_avg = total_cost / total_qty
            new_holdings[ticker] = Holding(
                ticker=ticker, quantity=total_qty, avg_cost=round(new_avg, 2)
            )
        else:
            new_holdings[ticker] = Holding(
                ticker=ticker, quantity=decision.quantity, avg_cost=round(price, 2)
            )

        return Portfolio(cash=round(portfolio.cash - cost, 2), holdings=new_holdings)

    elif decision.action == TradeAction.SELL:
        existing = portfolio.holdings.get(ticker)
        if existing is None or existing.quantity < decision.quantity or decision.quantity == 0:
            return portfolio

        proceeds = decision.quantity * price
        new_holdings = dict(portfolio.holdings)
        remaining = existing.quantity - decision.quantity

        if remaining == 0:
            del new_holdings[ticker]
        else:
            new_holdings[ticker] = Holding(
                ticker=ticker, quantity=remaining, avg_cost=existing.avg_cost
            )

        return Portfolio(cash=round(portfolio.cash + proceeds, 2), holdings=new_holdings)

    # HOLD — no changes
    return portfolio
