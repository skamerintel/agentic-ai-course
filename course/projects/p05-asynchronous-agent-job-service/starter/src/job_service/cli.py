from __future__ import annotations

import argparse

import uvicorn


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="job-service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args(argv)
    uvicorn.run(
        "job_service.app:create_app",
        host=args.host,
        port=args.port,
        factory=True,
    )
    return 0
