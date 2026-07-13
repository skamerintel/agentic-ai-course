from __future__ import annotations

import argparse
import json
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class LabHandler(BaseHTTPRequestHandler):
    transient_attempts = 0

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        correlation_id = self.headers.get("X-Correlation-ID")

        if parsed.path == "/ok":
            self._json(
                HTTPStatus.OK,
                {"status": "ok", "correlation_id": correlation_id},
            )
            return
        if parsed.path == "/transient":
            type(self).transient_attempts += 1
            if type(self).transient_attempts <= 2:
                self._json(
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    {"status": "retry", "attempt": type(self).transient_attempts},
                )
                return
            self._json(
                HTTPStatus.OK,
                {"status": "recovered", "correlation_id": correlation_id},
            )
            return
        if parsed.path == "/invalid":
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid request"})
            return
        if parsed.path == "/slow":
            seconds = float(parse_qs(parsed.query).get("seconds", ["1"])[0])
            time.sleep(seconds)
            self._json(
                HTTPStatus.OK,
                {"status": "slow", "seconds": seconds},
            )
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), LabHandler)
    print(f"listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
