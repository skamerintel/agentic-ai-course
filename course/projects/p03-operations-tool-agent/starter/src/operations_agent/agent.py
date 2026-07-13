from __future__ import annotations

from dataclasses import dataclass

from operations_agent.model import ModelSession
from operations_agent.models import AgentResult
from operations_agent.tools import ToolRegistry


@dataclass(frozen=True)
class AgentConfig:
    max_iterations: int = 6
    max_total_tool_calls: int = 10
    max_repeated_calls_per_signature: int = 2


DEFAULT_AGENT_CONFIG = AgentConfig()


def run_agent(
    session: ModelSession,
    registry: ToolRegistry,
    config: AgentConfig = DEFAULT_AGENT_CONFIG,
) -> AgentResult:
    raise NotImplementedError("implement the explicit model-tool loop")
