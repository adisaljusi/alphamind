"""Portfolio schemas."""

from pydantic import BaseModel, Field


class Holding(BaseModel):
    ticker: str
    quantity: int = Field(ge=0)
    avg_cost: float = Field(ge=0)


class Portfolio(BaseModel):
    """Current state of an agent's portfolio."""

    cash: float
    holdings: dict[str, Holding]

    @property
    def total_value(self) -> float:
        """Cash only — call value_at_prices for full valuation."""
        return self.cash

    def value_at_prices(self, prices: dict[str, float]) -> float:
        """Calculate total portfolio value given current market prices."""
        holdings_value = sum(
            h.quantity * prices.get(h.ticker, h.avg_cost)
            for h in self.holdings.values()
        )
        return self.cash + holdings_value
