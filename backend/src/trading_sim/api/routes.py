"""FastAPI route handlers for the trading simulation API."""

import asyncio
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from trading_sim.api.schemas import CreateSimulationRequest, UpdateAgentRequest
from trading_sim.config import AgentConfig, AppConfig, ModelParameters, load_config
from trading_sim.models.results import SimulationResult, SimulationStatus, SimulationSummary
from trading_sim.models.trades import TradeDecision
from trading_sim.simulation.runner import run_simulation
from trading_sim.simulation.storage import get_simulation, list_simulations, save_simulation

router = APIRouter()

# Mutable config — loaded once at startup, can be updated via API
_config: AppConfig | None = None


def _get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = load_config()
    return _config


# --- Agent endpoints ---


@router.get("/agents")
def list_agents() -> list[dict[str, Any]]:
    """List all configured trading agents."""
    config = _get_config()
    return [
        {
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
        for a in config.agents
    ]


@router.get("/agents/{agent_id}")
def get_agent(agent_id: str) -> dict[str, Any]:
    """Get a single agent config by ID."""
    config = _get_config()
    for a in config.agents:
        if a.id == agent_id:
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
    raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.put("/agents/{agent_id}")
def update_agent(agent_id: str, body: UpdateAgentRequest) -> dict[str, Any]:
    """Update an agent's configuration."""
    config = _get_config()
    for i, a in enumerate(config.agents):
        if a.id == agent_id:
            updates: dict[str, Any] = {}
            if body.name is not None:
                updates["name"] = body.name
            if body.description is not None:
                updates["description"] = body.description
            if body.persona_prompt is not None:
                updates["persona_prompt"] = body.persona_prompt
            if body.model_provider is not None:
                updates["model_provider"] = body.model_provider
            if body.model_id is not None:
                updates["model_id"] = body.model_id
            if body.initial_capital is not None:
                updates["initial_capital"] = body.initial_capital

            param_updates: dict[str, Any] = {}
            if body.temperature is not None:
                param_updates["temperature"] = body.temperature
            if body.max_tokens is not None:
                param_updates["max_tokens"] = body.max_tokens
            if param_updates:
                updates["parameters"] = ModelParameters(
                    temperature=body.temperature if body.temperature is not None else a.parameters.temperature,
                    max_tokens=body.max_tokens if body.max_tokens is not None else a.parameters.max_tokens,
                )

            updated = a.model_copy(update=updates)
            config.agents[i] = updated
            return get_agent(agent_id)

    raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


# --- Simulation endpoints ---


@router.get("/simulations", response_model=list[SimulationSummary])
def list_sims() -> list[SimulationSummary]:
    """List all simulation runs."""
    return list_simulations()


@router.post("/simulations", response_model=SimulationResult)
async def create_simulation(
    body: CreateSimulationRequest,
    background_tasks: BackgroundTasks,
) -> SimulationResult:
    """Start a new simulation run."""
    config = _get_config()
    agent_map = {a.id: a for a in config.agents}

    selected: list[AgentConfig] = []
    for aid in body.agent_ids:
        if aid not in agent_map:
            raise HTTPException(status_code=400, detail=f"Unknown agent ID: '{aid}'")
        selected.append(agent_map[aid])

    # Run simulation in background so the POST returns immediately
    import uuid
    sim_id = str(uuid.uuid4())[:8]

    # Create a placeholder result
    from datetime import date as date_type
    placeholder = SimulationResult(
        id=sim_id,
        status=SimulationStatus.PENDING,
        start_date=body.start_date or date_type(2024, 1, 2),
        end_date=body.end_date or date_type(2024, 12, 31),
        tickers=body.tickers or [],
        agent_ids=body.agent_ids,
    )
    save_simulation(placeholder)

    async def _run() -> None:
        await run_simulation(
            agent_configs=selected,
            tickers=body.tickers,
            start_date=body.start_date,
            end_date=body.end_date,
            sim_id=sim_id,
        )

    # Use asyncio.create_task so it runs in the same event loop
    asyncio.create_task(_run())

    return placeholder


@router.get("/simulations/{sim_id}", response_model=SimulationResult)
def get_sim(sim_id: str) -> SimulationResult:
    """Get simulation results by ID."""
    result = get_simulation(sim_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{sim_id}' not found")
    return result


@router.get("/simulations/{sim_id}/trades", response_model=list[TradeDecision])
def get_sim_trades(sim_id: str, agent_id: str | None = None) -> list[TradeDecision]:
    """Get trades for a simulation, optionally filtered by agent."""
    result = get_simulation(sim_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Simulation '{sim_id}' not found")

    trades: list[TradeDecision] = []
    for aid, agent_result in result.agent_results.items():
        if agent_id is not None and aid != agent_id:
            continue
        trades.extend(agent_result.trades)

    trades.sort(key=lambda t: t.timestamp)
    return trades
