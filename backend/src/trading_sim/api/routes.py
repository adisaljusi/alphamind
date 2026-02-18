"""Litestar route handlers for the trading simulation API."""

from __future__ import annotations

import asyncio
import uuid
from datetime import date as date_type
from typing import Any

from litestar import Controller, get, post, put
from litestar.exceptions import NotFoundException, ValidationException

from trading_sim.api.schemas import CreateSimulationRequest, UpdateAgentRequest
from trading_sim.config import AgentConfig, AppConfig, ModelParameters, load_config
from trading_sim.models.results import SimulationResult, SimulationStatus, SimulationSummary
from trading_sim.models.trades import TradeDecision
from trading_sim.simulation.runner import run_simulation
from trading_sim.simulation.storage import get_simulation, list_simulations, save_simulation

# Mutable config — loaded once at startup, can be updated via API
_config: AppConfig | None = None


def _get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = load_config()
    return _config


def _agent_to_dict(a: AgentConfig) -> dict[str, Any]:
    return {
        "id": a.id,
        "name": a.name,
        "description": a.description,
        "persona_prompt": a.persona_prompt,
        "model_provider": a.model_provider,
        "model_id": a.model_id,
        "temperature": a.parameters.temperature,
        "max_tokens": a.parameters.max_tokens,
        "initial_capital": a.initial_capital,
    }


class AgentController(Controller):
    path = "/agents"

    @get("/")
    async def list_agents(self) -> list[dict[str, Any]]:
        """List all configured trading agents."""
        config = _get_config()
        return [_agent_to_dict(a) for a in config.agents]

    @get("/{agent_id:str}")
    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        """Get a single agent config by ID."""
        config = _get_config()
        for a in config.agents:
            if a.id == agent_id:
                return _agent_to_dict(a)
        raise NotFoundException(detail=f"Agent '{agent_id}' not found")

    @put("/{agent_id:str}")
    async def update_agent(self, agent_id: str, data: UpdateAgentRequest) -> dict[str, Any]:
        """Update an agent's configuration."""
        config = _get_config()
        for i, a in enumerate(config.agents):
            if a.id == agent_id:
                updates: dict[str, Any] = {}
                if data.name is not None:
                    updates["name"] = data.name
                if data.description is not None:
                    updates["description"] = data.description
                if data.persona_prompt is not None:
                    updates["persona_prompt"] = data.persona_prompt
                if data.model_provider is not None:
                    updates["model_provider"] = data.model_provider
                if data.model_id is not None:
                    updates["model_id"] = data.model_id
                if data.initial_capital is not None:
                    updates["initial_capital"] = data.initial_capital

                param_updates: dict[str, Any] = {}
                if data.temperature is not None:
                    param_updates["temperature"] = data.temperature
                if data.max_tokens is not None:
                    param_updates["max_tokens"] = data.max_tokens
                if param_updates:
                    updates["parameters"] = ModelParameters(
                        temperature=data.temperature if data.temperature is not None else a.parameters.temperature,
                        max_tokens=data.max_tokens if data.max_tokens is not None else a.parameters.max_tokens,
                    )

                updated = a.model_copy(update=updates)
                config.agents[i] = updated
                return _agent_to_dict(updated)

        raise NotFoundException(detail=f"Agent '{agent_id}' not found")


class SimulationController(Controller):
    path = "/simulations"

    @get("/")
    async def list_sims(self) -> list[SimulationSummary]:
        """List all simulation runs."""
        return await list_simulations()

    @post("/")
    async def create_simulation(self, data: CreateSimulationRequest) -> SimulationResult:
        """Start a new simulation run."""
        config = _get_config()
        agent_map = {a.id: a for a in config.agents}

        selected: list[AgentConfig] = []
        for aid in data.agent_ids:
            if aid not in agent_map:
                raise ValidationException(detail=f"Unknown agent ID: '{aid}'")
            selected.append(agent_map[aid])

        sim_id = str(uuid.uuid4())[:8]

        placeholder = SimulationResult(
            id=sim_id,
            status=SimulationStatus.PENDING,
            start_date=data.start_date or date_type(2024, 1, 2),
            end_date=data.end_date or date_type(2024, 12, 31),
            tickers=data.tickers or [],
            agent_ids=data.agent_ids,
        )
        await save_simulation(placeholder)

        async def _run() -> None:
            await run_simulation(
                agent_configs=selected,
                tickers=data.tickers,
                start_date=data.start_date,
                end_date=data.end_date,
                sim_id=sim_id,
            )

        asyncio.create_task(_run())
        return placeholder

    @get("/{sim_id:str}")
    async def get_sim(self, sim_id: str) -> SimulationResult:
        """Get simulation results by ID."""
        result = await get_simulation(sim_id)
        if result is None:
            raise NotFoundException(detail=f"Simulation '{sim_id}' not found")
        return result

    @get("/{sim_id:str}/trades")
    async def get_sim_trades(self, sim_id: str, agent_id: str | None = None) -> list[TradeDecision]:
        """Get trades for a simulation, optionally filtered by agent."""
        result = await get_simulation(sim_id)
        if result is None:
            raise NotFoundException(detail=f"Simulation '{sim_id}' not found")

        trades: list[TradeDecision] = []
        for aid, agent_result in result.agent_results.items():
            if agent_id is not None and aid != agent_id:
                continue
            trades.extend(agent_result.trades)

        trades.sort(key=lambda t: t.timestamp)
        return trades
