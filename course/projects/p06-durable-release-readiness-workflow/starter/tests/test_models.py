import pytest
from pydantic import ValidationError

from release_workflow.models import ApprovalResponse
from release_workflow.workflow import approval_command


def test_edit_requires_an_edited_decision() -> None:
    with pytest.raises(ValidationError):
        ApprovalResponse.model_validate(
            {"action": "edit", "rationale": "Change required"},
            strict=False,
        )


def test_approval_command_builds_typed_edit() -> None:
    approval = approval_command(
        "edit",
        "Ready after documentation merges",
        edited_decision="ready_with_conditions",
        conditions=["Merge PR-812"],
    )

    assert approval.action.value == "edit"
    assert approval.edited_decision is not None
    assert approval.edited_decision.value == "ready_with_conditions"
