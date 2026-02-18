"""OpenTelemetry setup for the trading simulation platform."""

from __future__ import annotations

import logging

from trading_sim.settings import get_otel_enabled, get_otel_endpoint

logger = logging.getLogger(__name__)


def setup_telemetry(service_name: str = "trading-sim") -> None:
    """Configure OpenTelemetry tracing and metrics export."""
    if not get_otel_enabled():
        logger.info("OpenTelemetry disabled via OTEL_ENABLED")
        return

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(endpoint=get_otel_endpoint(), insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)

    # Instrument SQLAlchemy
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument()
    except Exception:
        logger.debug("SQLAlchemy instrumentation not available", exc_info=True)

    # Instrument asyncpg
    try:
        from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

        AsyncPGInstrumentor().instrument()
    except Exception:
        logger.debug("asyncpg instrumentation not available", exc_info=True)

    logger.info("OpenTelemetry configured — exporting to %s", get_otel_endpoint())
