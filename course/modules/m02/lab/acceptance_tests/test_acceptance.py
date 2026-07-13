import pytest

from ticket_rules import validate_ticket


def test_strips_only_outer_title_whitespace() -> None:
    assert validate_ticket("  Printer   unavailable  ", "HIGH") == (
        "Printer   unavailable",
        "high",
    )


@pytest.mark.parametrize("title", ["", " ", "\n\t"])
def test_rejects_blank_title(title: str) -> None:
    with pytest.raises(ValueError, match="title"):
        validate_ticket(title, "low")


@pytest.mark.parametrize("priority", ["urgent", "p1", "", "highest"])
def test_rejects_unknown_priority(priority: str) -> None:
    with pytest.raises(ValueError, match="priority"):
        validate_ticket("Printer unavailable", priority)
