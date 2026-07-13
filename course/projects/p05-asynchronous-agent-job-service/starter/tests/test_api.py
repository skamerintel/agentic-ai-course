import asyncio

import httpx
from asgi_lifespan import LifespanManager

from job_service.app import create_app
from job_service.config import Settings
from job_service.domain import JobStatus


def payload(key: str = "idem-api-0001") -> dict:
    return {
        "idempotency_key": key,
        "issue": {
            "issue_id": "ISS-API",
            "repo": "acme/payments",
            "title": "Payment failure",
            "body": "A payment failed after a timeout.",
        },
    }


async def test_submit_duplicate_and_result_contract(tmp_path) -> None:
    app = create_app(
        Settings(
            database_url=f"sqlite+aiosqlite:///{tmp_path / 'api.db'}",
            auto_run_jobs=False,
        )
    )
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            first = await client.post("/v1/jobs", json=payload())
            duplicate = await client.post("/v1/jobs", json=payload())
            job_id = first.json()["job_id"]
            result = await client.get(f"/v1/jobs/{job_id}/result")

    assert first.status_code == 202
    assert duplicate.status_code == 200
    assert duplicate.json()["job_id"] == job_id
    assert result.status_code == 409
    assert result.json()["error"]["code"] == "result_not_ready"


async def test_api_integration_reaches_persisted_result(tmp_path) -> None:
    app = create_app(
        Settings(
            database_url=f"sqlite+aiosqlite:///{tmp_path / 'integration.db'}",
            auto_run_jobs=True,
        )
    )
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            submitted = await client.post(
                "/v1/jobs",
                json=payload("idem-api-integration"),
                headers={"x-correlation-id": "corr-api-integration"},
            )
            job_id = submitted.json()["job_id"]
            current = None
            for _ in range(50):
                current = await client.get(f"/v1/jobs/{job_id}")
                if JobStatus(current.json()["status"]).terminal:
                    break
                await asyncio.sleep(0)
            result = await client.get(f"/v1/jobs/{job_id}/result")
            audit = await client.get(f"/v1/jobs/{job_id}/audit")

    assert current is not None
    assert current.json()["status"] == "succeeded"
    assert result.status_code == 200
    assert [event["event"] for event in audit.json()] == [
        "queued",
        "running",
        "succeeded",
    ]


async def test_unknown_job_has_stable_error_contract(tmp_path) -> None:
    app = create_app(
        Settings(
            database_url=f"sqlite+aiosqlite:///{tmp_path / 'missing.db'}",
            auto_run_jobs=False,
        )
    )
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get("/v1/jobs/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "job_not_found",
            "message": "The requested job does not exist.",
        }
    }
