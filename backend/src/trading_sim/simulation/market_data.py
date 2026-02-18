"""Mock market data generation for simulations."""

import math
import random
from datetime import date, timedelta

from trading_sim.models.market import MarketSnapshot, PriceBar

# Realistic-ish base prices and volatilities for mock tickers
TICKER_PROFILES: dict[str, tuple[float, float]] = {
    "AAPL": (180.0, 0.02),
    "GOOGL": (140.0, 0.022),
    "MSFT": (370.0, 0.018),
    "AMZN": (175.0, 0.025),
    "TSLA": (240.0, 0.04),
    "NVDA": (480.0, 0.035),
    "JPM": (170.0, 0.015),
    "JNJ": (155.0, 0.012),
    "SPY": (470.0, 0.01),
    "BND": (72.0, 0.003),
}

DEFAULT_TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]


def _generate_price_series(
    base_price: float,
    volatility: float,
    num_days: int,
    seed: int,
) -> list[tuple[float, float, float, float, int]]:
    """Generate synthetic OHLCV data using geometric Brownian motion."""
    rng = random.Random(seed)
    drift = 0.0002  # slight upward bias

    bars: list[tuple[float, float, float, float, int]] = []
    price = base_price

    for _ in range(num_days):
        # Daily return from GBM
        daily_return = drift + volatility * rng.gauss(0, 1)
        open_price = price
        close_price = price * math.exp(daily_return)

        # Intraday high/low
        intraday_vol = abs(close_price - open_price) * rng.uniform(0.5, 2.0)
        high = max(open_price, close_price) + intraday_vol * rng.uniform(0.1, 0.5)
        low = min(open_price, close_price) - intraday_vol * rng.uniform(0.1, 0.5)
        low = max(low, 0.01)  # price floor

        volume = int(rng.gauss(10_000_000, 3_000_000))
        volume = max(volume, 100_000)

        bars.append((
            round(open_price, 2),
            round(high, 2),
            round(low, 2),
            round(close_price, 2),
            volume,
        ))
        price = close_price

    return bars


def generate_mock_data(
    tickers: list[str] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[MarketSnapshot]:
    """Generate mock market data for a set of tickers over a date range.

    Returns a list of MarketSnapshot, one per trading day.
    """
    if tickers is None:
        tickers = DEFAULT_TICKERS
    if start_date is None:
        start_date = date(2024, 1, 2)
    if end_date is None:
        end_date = date(2024, 12, 31)

    # Build trading days (skip weekends)
    trading_days: list[date] = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Mon-Fri
            trading_days.append(current)
        current += timedelta(days=1)

    num_days = len(trading_days)
    if num_days == 0:
        return []

    # Generate price series for each ticker
    ticker_bars: dict[str, list[tuple[float, float, float, float, int]]] = {}
    for i, ticker in enumerate(tickers):
        base_price, vol = TICKER_PROFILES.get(ticker, (100.0, 0.02))
        seed = hash(ticker) + hash(str(start_date)) + i
        ticker_bars[ticker] = _generate_price_series(base_price, vol, num_days, seed)

    # Assemble snapshots
    snapshots: list[MarketSnapshot] = []
    for day_idx, day in enumerate(trading_days):
        prices: dict[str, PriceBar] = {}
        for ticker in tickers:
            o, h, l, c, v = ticker_bars[ticker][day_idx]
            prices[ticker] = PriceBar(
                ticker=ticker,
                date=day,
                open=o,
                high=h,
                low=l,
                close=c,
                volume=v,
            )
        snapshots.append(MarketSnapshot(
            date=day,
            prices=prices,
            day_index=day_idx,
            total_days=num_days,
        ))

    return snapshots
