# Async Client Lab

This lab uses only Python's standard library. It contains a local HTTP server
with deterministic success, transient-failure, validation-failure, and slow
response endpoints plus an intentionally flawed asynchronous client.

Start the server:

```bash
python course/modules/m03/lab/server.py
```

In another terminal, run the client:

```bash
python course/modules/m03/lab/client.py http://127.0.0.1:8765/ok
```

Repair the client and add tests for:

- Timeout behavior against `/slow?seconds=2`.
- Bounded retries against `/transient`.
- No retry against `/invalid`.
- One stable correlation identifier across attempts.
- Redaction of the authorization token.
- Observation of every task exception.
