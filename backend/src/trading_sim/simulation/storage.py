"""Simple in-memory + JSON file storage for simulation results."""

import json
from pathlib import Path

from trading_sim.models.results import SimulationResult, SimulationSummary

# In-memory store — sufficient for a local dev tool
_simulations: dict[str, SimulationResult] = {}

STORAGE_DIR = Path(__file__).parent.parent.parent.parent / "data"


def save_simulation(result: SimulationResult) -> None:
    """Save simulation to in-memory store and optionally to disk."""
    _simulations[result.id] = result

    # Persist to JSON
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORAGE_DIR / f"{result.id}.json"
    path.write_text(result.model_dump_json(indent=2))


def get_simulation(sim_id: str) -> SimulationResult | None:
    """Retrieve a simulation by ID."""
    if sim_id in _simulations:
        return _simulations[sim_id]

    # Try loading from disk
    path = STORAGE_DIR / f"{sim_id}.json"
    if path.exists():
        result = SimulationResult.model_validate_json(path.read_text())
        _simulations[sim_id] = result
        return result

    return None


def list_simulations() -> list[SimulationSummary]:
    """List all simulations (from memory and disk)."""
    # Load any on-disk simulations not yet in memory
    if STORAGE_DIR.exists():
        for path in STORAGE_DIR.glob("*.json"):
            sim_id = path.stem
            if sim_id not in _simulations:
                try:
                    result = SimulationResult.model_validate_json(path.read_text())
                    _simulations[sim_id] = result
                except Exception:
                    continue

    return [
        SimulationSummary(
            id=sim.id,
            status=sim.status,
            created_at=sim.created_at,
            start_date=sim.start_date,
            end_date=sim.end_date,
            tickers=sim.tickers,
            agent_ids=sim.agent_ids,
        )
        for sim in sorted(_simulations.values(), key=lambda s: s.created_at, reverse=True)
    ]
