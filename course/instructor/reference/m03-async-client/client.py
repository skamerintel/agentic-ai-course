from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("m03-client")


@dataclass(frozen=True)
class Response:
    status: int
    body: dict[str, object]


def _blocking_get(
    url: str,
    token: str,
    correlation_id: str,
    timeout_seconds: float,
) -> Response:
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Correlation-ID": correlation_id,
        },
    )
    try:
        with urlopen(  # noqa: S310 - local course server
            request, timeout=timeout_seconds
        ) as response:
            return Response(response.status, json.loads(response.read()))
    except HTTPError as exc:
        return Response(exc.code, json.loads(exc.read()))


async def fetch(
    url: str,
    token: str,
    *,
    timeout_seconds: float = 1.0,
    max_attempts: int = 3,
) -> Response:
    correlation_id = str(uuid.uuid4())
    for attempt in range(1, max_attempts + 1):
        LOGGER.info(
            "http_attempt correlation_id=%s attempt=%s url=%s",
            correlation_id,
            attempt,
            url,
        )
        response = await asyncio.to_thread(
            _blocking_get,
            url,
            token,
            correlation_id,
            timeout_seconds,
        )
        if response.status != 503 or attempt == max_attempts:
            return response
        await asyncio.sleep(0.05 * attempt)
    raise AssertionError("attempt loop did not return")
