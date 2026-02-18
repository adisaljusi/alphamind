"""PostgreSQL-backed storage for simulation results."""

from __future__ import annotations

from sqlalchemy import select

from trading_sim.db.engine import get_session_factory
from trading_sim.db.tables import SimulationRow
from trading_sim.models.results import SimulationResult, SimulationSummary


async def save_simulation(result: SimulationResult) -> None:
    """Upsert a simulation result into the database."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        row = await session.get(SimulationRow, result.id)
        data = result.model_dump(mode="json")

        if row is None:
            row = SimulationRow(
                id=result.id,
                status=data["status"],
                created_at=result.created_at,
                start_date=result.start_date,
                end_date=result.end_date,
                tickers=data["tickers"],
                agent_ids=data["agent_ids"],
                agent_results=data["agent_results"],
                error=data.get("error"),
            )
            session.add(row)
        else:
            row.status = data["status"]
            row.tickers = data["tickers"]
            row.agent_ids = data["agent_ids"]
            row.agent_results = data["agent_results"]
            row.error = data.get("error")

        await session.commit()


async def get_simulation(sim_id: str) -> SimulationResult | None:
    """Retrieve a simulation by ID."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        row = await session.get(SimulationRow, sim_id)
        if row is None:
            return None
        return _row_to_result(row)


async def list_simulations() -> list[SimulationSummary]:
    """List all simulations ordered by creation time descending."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        stmt = select(SimulationRow).order_by(SimulationRow.created_at.desc())
        rows = (await session.execute(stmt)).scalars().all()
        return [
            SimulationSummary(
                id=row.id,
                status=row.status,
                created_at=row.created_at,
                start_date=row.start_date,
                end_date=row.end_date,
                tickers=row.tickers,
                agent_ids=row.agent_ids,
            )
            for row in rows
        ]


def _row_to_result(row: SimulationRow) -> SimulationResult:
    return SimulationResult(
        id=row.id,
        status=row.status,
        created_at=row.created_at,
        start_date=row.start_date,
        end_date=row.end_date,
        tickers=row.tickers,
        agent_ids=row.agent_ids,
        agent_results=row.agent_results,
        error=row.error,
    )
