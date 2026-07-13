def test_fixture_reads_are_bounded(fixture_gateway) -> None:
    result = fixture_gateway.list_issues("acme", "payments-service", limit=2)

    assert len(result.items) == 2
    assert result.truncated is True


def test_untrusted_issue_text_is_preserved_as_data(fixture_gateway) -> None:
    result = fixture_gateway.list_issues("acme", "payments-service", limit=10)

    issue = next(item for item in result.items if item.number == 42)
    assert "Ignore prior instructions" in issue.body


def test_fixture_comment_key_is_idempotent(fixture_gateway) -> None:
    first = fixture_gateway.create_issue_comment(
        "acme",
        "payments-service",
        41,
        "A bounded approved comment",
        idempotency_key="proposal-1",
    )
    second = fixture_gateway.create_issue_comment(
        "acme",
        "payments-service",
        41,
        "A bounded approved comment",
        idempotency_key="proposal-1",
    )

    assert first == second
    assert fixture_gateway.comment_calls == 1
