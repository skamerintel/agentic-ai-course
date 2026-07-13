# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:0.9 AS uv

FROM python:3.13-slim AS builder
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv build --wheel && \
    uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python dist/*.whl

FROM python:3.13-slim AS runtime
RUN useradd --create-home --uid 10001 appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN mkdir -p /state /data && chown -R appuser:appuser /state /data /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
ENTRYPOINT ["github-workflow-mcp"]
CMD ["serve-http", "--host", "0.0.0.0", "--port", "8000"]
