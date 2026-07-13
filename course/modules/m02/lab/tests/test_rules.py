from unittest.mock import patch

from ticket_rules import validate_ticket


@patch("ticket_rules.rules.validate_ticket")
def test_validation_returns_normalized_values(mock_validate) -> None:
    mock_validate.return_value = ("Printer unavailable", "high")

    assert mock_validate(" Printer unavailable ", "HIGH") == (
        "Printer unavailable",
        "high",
    )


def test_public_function_is_importable() -> None:
    assert callable(validate_ticket)
