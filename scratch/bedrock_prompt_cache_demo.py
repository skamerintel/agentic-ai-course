from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockModelSettings


def main() -> None:
    agent = Agent(
        "bedrock:global.anthropic.claude-sonnet-5",
        system_prompt="You are a helpful assistant.",
        model_settings=BedrockModelSettings(
            bedrock_cache_messages=True,
        ),
    )

    first = agent.run_sync("What is the capital of France?")
    print(first)

    second = agent.run_sync("What is the capital of Germany?")
    print(second)
    print(f"Cache write: {first.usage.cache_write_tokens}")
    print(f"Cache read: {second.usage.cache_read_tokens}")


if __name__ == "__main__":
    main()
