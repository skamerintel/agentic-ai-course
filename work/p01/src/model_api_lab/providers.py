from __future__ import annotations

import time

from model_api_lab.models import Incident, ProviderResult
from model_api_lab.prompting import SYSTEM_INSTRUCTIONS, user_prompt


def call_openai_responses(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    """Call OpenAI Responses. Import the SDK inside this function."""
    raise NotImplementedError("implement the live Responses adapter")


def call_openai_chat(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    """Call OpenAI Chat Completions. Import the SDK inside this function."""
    raise NotImplementedError("implement the live Chat Completions adapter")


def call_anthropic_messages(
    incident: Incident, model: str, timeout_seconds: float = 60.0
) -> ProviderResult:
    """Call Claude via AWS Bedrock, using pydantic-ai's BedrockConverseModel."""
    from pydantic_ai import Agent, ModelSettings
    from pydantic_ai.models.bedrock import BedrockConverseModel
    from pydantic_ai.providers.bedrock import BedrockProvider

    bedrock_model = BedrockConverseModel(
        model, provider=BedrockProvider(region_name="us-east-2")
    )
    agent = Agent(
        bedrock_model,
        system_prompt=SYSTEM_INSTRUCTIONS,
        model_settings=ModelSettings(timeout=timeout_seconds),
    )

    started = time.perf_counter()
    result = agent.run_sync(user_prompt(incident))
    latency_ms = (time.perf_counter() - started) * 1000

    response = result.response
    usage = result.usage

    return ProviderResult(
        provider="anthropic",
        api="messages",
        model=model,
        text=result.output,
        latency_ms=latency_ms,
        response_id=response.provider_response_id,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        output_types=("text",),
    )
