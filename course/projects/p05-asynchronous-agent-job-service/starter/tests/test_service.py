from job_service.domain import IssueInput, JobStatus, JobSubmission
from job_service.progress import InMemoryProgressStore
from job_service.provider import DeterministicTriageProvider, ProviderFailure
from job_service.service import JobService


def submission(key: str = "idem-service-001") -> JobSubmission:
    return JobSubmission(
        idempotency_key=key,
        issue=IssueInput(
            issue_id="ISS-SERVICE",
            repo="acme/payments",
            title="Payment failure",
            body="The payment request failed.",
        ),
    )


class FailingProvider:
    name = "failing-provider"

    async def triage(self, issue, correlation_id):
        raise ProviderFailure("provider_timeout", "The provider timed out.")


async def test_service_runs_job_and_emits_progress(repository) -> None:
    progress = InMemoryProgressStore()
    service = JobService(
        repository,
        progress,
        DeterministicTriageProvider(),
        auto_run=False,
    )
    job, created = await service.submit(submission(), "corr-service")
    await service.run_job(job.job_id)

    completed = await service.get_job(job.job_id)
    events = await progress.recent(job.job_id)

    assert created is True
    assert completed.status is JobStatus.SUCCEEDED
    assert [event.event for event in events] == [
        "queued",
        "running",
        "provider_started",
        "succeeded",
    ]


async def test_service_classifies_provider_failure(repository) -> None:
    progress = InMemoryProgressStore()
    service = JobService(repository, progress, FailingProvider(), auto_run=False)
    job, _ = await service.submit(submission("idem-service-002"), "corr-fail")
    await service.run_job(job.job_id)

    failed = await service.get_job(job.job_id)

    assert failed.status is JobStatus.FAILED
    assert failed.error_code == "provider_timeout"


async def test_service_cancels_queued_job_without_provider_call(repository) -> None:
    progress = InMemoryProgressStore()
    service = JobService(
        repository,
        progress,
        DeterministicTriageProvider(),
        auto_run=False,
    )
    job, _ = await service.submit(submission("idem-service-003"), "corr-cancel")

    cancelled = await service.cancel(job.job_id)

    assert cancelled.status is JobStatus.CANCELLED
