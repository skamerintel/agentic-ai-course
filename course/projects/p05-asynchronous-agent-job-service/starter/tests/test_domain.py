import pytest
from pydantic import ValidationError

from job_service.domain import IssueInput, JobStatus, JobSubmission


def test_terminal_states_are_explicit() -> None:
    assert JobStatus.SUCCEEDED.terminal
    assert JobStatus.FAILED.terminal
    assert JobStatus.CANCELLED.terminal
    assert not JobStatus.RUNNING.terminal


def test_submission_rejects_short_idempotency_key() -> None:
    with pytest.raises(ValidationError):
        JobSubmission(
            idempotency_key="short",
            issue=IssueInput(
                issue_id="ISS-1",
                repo="acme/service",
                title="Failure",
                body="A useful description",
            ),
        )
