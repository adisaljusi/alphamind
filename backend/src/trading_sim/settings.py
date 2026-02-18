"""Application settings loaded from environment variables."""

from __future__ import annotations

import os


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://trading:trading@localhost:5432/trading_sim",
    )


def get_otel_endpoint() -> str:
    return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")


def get_otel_enabled() -> bool:
    return os.getenv("OTEL_ENABLED", "true").lower() in ("true", "1", "yes")


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]
