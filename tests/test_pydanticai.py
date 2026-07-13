from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockModelSettings

agent = Agent(
    'bedrock:global.anthropic.claude-sonnet-5',
    system_prompt='You are a helpful assistant.',
    model_settings=BedrockModelSettings(
        bedrock_cache_messages=True,  # Automatically caches the last message
    ),
)

# The last message is automatically cached - no need for manual CachePoint
result1 = agent.run_sync('What is the capital of France?')
print(result1)

# Subsequent calls with similar conversation benefit from cache
result2 = agent.run_sync('What is the capital of Germany?')
print(result2)
print(f'Cache write: {result1.usage.cache_write_tokens}')
print(f'Cache read: {result2.usage.cache_read_tokens}')
