from __future__ import annotations

import asyncio
import threading
import unittest
from http.server import ThreadingHTTPServer

from client import fetch
from server import LabHandler


class AsyncClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        LabHandler.transient_attempts = 0
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), LabHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_retries_transient_failure_with_stable_correlation_id(self) -> None:
        response = asyncio.run(
            fetch(f"{self.base_url}/transient", "secret", max_attempts=3)
        )

        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["status"], "recovered")
        self.assertIsInstance(response.body["correlation_id"], str)

    def test_does_not_retry_bad_request(self) -> None:
        response = asyncio.run(fetch(f"{self.base_url}/invalid", "secret"))

        self.assertEqual(response.status, 400)

    def test_timeout_is_observed(self) -> None:
        with self.assertRaises(TimeoutError):
            asyncio.run(
                fetch(
                    f"{self.base_url}/slow?seconds=0.2",
                    "secret",
                    timeout_seconds=0.01,
                    max_attempts=1,
                )
            )


if __name__ == "__main__":
    unittest.main()
