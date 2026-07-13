from __future__ import annotations

import argparse
import asyncio
import logging
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("m03-client")


def _blocking_get(url: str, token: str) -> str:
    request = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(request) as response:  # noqa: S310 - local course server
        return response.read().decode()


async def fetch(url: str, token: str) -> str:
    """Intentionally flawed client for the learner to repair."""
    LOGGER.info("requesting url=%s token=%s", url, token)
    return await asyncio.to_thread(_blocking_get, url, token)


async def run(url: str, token: str) -> None:
    task = asyncio.create_task(fetch(url, token))
    LOGGER.info("started task=%s", task.get_name())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--token", default="course-secret-token")
    args = parser.parse_args()
    asyncio.run(run(args.url, args.token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
