# Asynchronous Agent Job Service

This is the learner implementation workspace for Project 5. Read `PROJECT.md`
and complete the decision records in `reports/` before implementing TODOs.

The default local configuration uses SQLite, an in-memory progress adapter, and
a deterministic provider so the test suite is offline. Docker Compose provides
PostgreSQL and Redis for explicit integration work.

```bash
uv sync
uv run pytest
uv run job-service
```

The service listens on `http://127.0.0.1:8000` by default. OpenAPI documentation
is available at `/docs`.
