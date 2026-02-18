"""Configuration loading for agent and model settings."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ModelParameters(BaseModel):
    temperature: float = 0.5
    max_tokens: int = 1024


class AgentConfig(BaseModel):
    id: str
    name: str
    description: str
    persona_prompt: str
    model_provider: str = "openai"
    model_id: str = "gpt-4o"
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    initial_capital: float = 100_000.0


class AppConfig(BaseModel):
    agents: list[AgentConfig]


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load agent configuration from YAML file."""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "agents.yaml"

    with open(config_path) as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    return AppConfig.model_validate(raw)
