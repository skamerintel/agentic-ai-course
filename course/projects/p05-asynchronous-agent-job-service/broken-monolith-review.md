# Review Exercise: AI-Generated Monolithic Endpoint

An AI assistant proposed this design:

```python
@app.post("/jobs")
async def create_job(payload: dict):
    engine = create_async_engine(os.environ["DATABASE_URL"])
    redis = Redis.from_url(os.environ["REDIS_URL"])
    client = AsyncOpenAI()
    if await redis.get(payload["idempotency_key"]):
        return {"status": "already_done"}
    await redis.set(payload["idempotency_key"], "started", ex=60)
    try:
        response = await client.responses.create(
            model=os.environ["OPENAI_MODEL"], input=payload["issue"]
        )
        async with AsyncSession(engine) as session:
            session.add(Job(payload=json.dumps(payload), result=response.output_text))
            await session.commit()
        return {"status": "complete", "result": response.output_text}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
```

## Required review

Identify at least twelve defects or unsupported assumptions. Include:

- Contract validation.
- Dependency and lifecycle management.
- Idempotency durability and conflicts.
- Separation of concerns.
- Asynchronous job semantics.
- Database modeling and transactions.
- Redis expiry behavior.
- Provider error disclosure.
- Cancellation and restart behavior.
- Testability and logging.

Then produce a responsibility map showing where each concern belongs in the
Project 5 architecture.
