from __future__ import annotations

import argparse

import uvicorn

from github_workflow_mcp.factory import (
    build_components,
    build_http_app,
    ensure_state_parent,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="github-workflow-mcp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    http = subparsers.add_parser("serve-http")
    http.add_argument("--host", default="127.0.0.1")
    http.add_argument("--port", type=int, default=8000)

    subparsers.add_parser("serve-stdio")

    approve = subparsers.add_parser("approve")
    approve.add_argument("proposal_id")
    approve.add_argument("--actor", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    ensure_state_parent()
    if args.command == "serve-http":
        uvicorn.run(build_http_app(), host=args.host, port=args.port)
    elif args.command == "serve-stdio":
        server, _store = build_components()
        server.run(transport="stdio", show_banner=False)
    else:
        _server, store = build_components()
        proposal = store.approve(args.proposal_id, args.actor)
        print(proposal.model_dump_json(indent=2))
    return 0
