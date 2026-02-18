FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project metadata first for better layer caching
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .

# Copy application code
COPY config/ config/
COPY src/ src/

# Install the project itself
RUN uv pip install --system --no-cache -e .

EXPOSE 8000

CMD ["uvicorn", "trading_sim.main:app", "--host", "0.0.0.0", "--port", "8000"]
