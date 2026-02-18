"""Trading agent creation and decision-making using Pydantic AI."""

from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from trading_sim.config import AgentConfig
from trading_sim.models.market import MarketSnapshot
from trading_sim.models.portfolio import Portfolio
from trading_sim.models.trades import TradeAction, TradeDecision
from trading_sim.strategies.prompts import build_market_prompt

logger = logging.getLogger(__name__)


class AgentTradeOutput(BaseModel):
    """Structured output the LLM must produce."""

    action: str = Field(description="One of: buy, sell, hold")
    ticker: str = Field(description="The ticker symbol to trade, or 'N/A' for hold")
    quantity: int = Field(ge=0, description="Number of shares (0 for hold)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level 0.0-1.0")
    reasoning: str = Field(description="Explanation of why this decision was made")


def _build_model_string(config: AgentConfig) -> str:
    """Build the model string for Pydantic AI from agent config."""
    provider = config.model_provider.lower()
    model_id = config.model_id

    if provider == "openai":
        return f"openai:{model_id}"
    elif provider == "anthropic":
        return f"anthropic:{model_id}"
    elif provider == "google" or provider == "gemini":
        return f"google-gla:{model_id}"
    else:
        return f"{provider}:{model_id}"


def create_trading_agent(config: AgentConfig) -> Agent[None, AgentTradeOutput]:
    """Create a Pydantic AI agent for a trading persona."""
    system_prompt = (
        f"You are {config.name}, a trading agent.\n\n"
        f"{config.persona_prompt}\n\n"
        "You will receive market data and your current portfolio. "
        "Make exactly ONE trading decision per turn. "
        "Respond with a structured decision: action (buy/sell/hold), "
        "ticker, quantity, confidence (0-1), and your reasoning."
    )

    model_str = _build_model_string(config)

    agent: Agent[None, AgentTradeOutput] = Agent(
        model=model_str,
        result_type=AgentTradeOutput,
        system_prompt=system_prompt,
    )

    return agent


async def get_agent_decision(
    agent: Agent[None, AgentTradeOutput],
    config: AgentConfig,
    snapshot: MarketSnapshot,
    history: list[MarketSnapshot],
    portfolio: Portfolio,
) -> TradeDecision:
    """Run the agent on current market data and return a structured trade decision.

    Falls back to a HOLD decision if the LLM call fails.
    """
    prices = {t: bar.close for t, bar in snapshot.prices.items()}
    prompt = build_market_prompt(snapshot, history, portfolio, prices)

    try:
        result = await agent.run(prompt)
        output = result.data

        action_str = output.action.lower().strip()
        if action_str == "buy":
            action = TradeAction.BUY
        elif action_str == "sell":
            action = TradeAction.SELL
        else:
            action = TradeAction.HOLD

        ticker = output.ticker if action != TradeAction.HOLD else list(snapshot.prices.keys())[0]
        price = prices.get(ticker, 0.0)

        return TradeDecision(
            agent_id=config.id,
            timestamp=datetime.utcnow(),
            ticker=ticker,
            action=action,
            quantity=output.quantity if action != TradeAction.HOLD else 0,
            confidence=output.confidence,
            reasoning=output.reasoning,
            price_at_decision=price if price > 0 else 1.0,
        )
    except Exception as e:
        logger.warning("Agent %s failed, defaulting to HOLD: %s", config.id, e)
        first_ticker = list(snapshot.prices.keys())[0]
        return TradeDecision(
            agent_id=config.id,
            timestamp=datetime.utcnow(),
            ticker=first_ticker,
            action=TradeAction.HOLD,
            quantity=0,
            confidence=0.0,
            reasoning=f"Agent error, defaulting to hold: {e}",
            price_at_decision=prices.get(first_ticker, 1.0),
        )
