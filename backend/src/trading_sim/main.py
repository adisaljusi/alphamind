"""Litestar application entry point."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from litestar import Litestar
from litestar.config.cors import CORSConfig

from trading_sim.api.routes import AgentController, SimulationController
from trading_sim.db.engine import close_db, init_db
from trading_sim.settings import get_cors_origins
from trading_sim.telemetry import setup_telemetry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    setup_telemetry()
    await init_db()
    yield
    await close_db()


app = Litestar(
    route_handlers=[AgentController, SimulationController],
    path="/api",
    cors_config=CORSConfig(
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    lifespan=[lifespan],
    debug=False,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("trading_sim.main:app", host="0.0.0.0", port=8000, reload=True)
