from pathlib import Path


def test_approval_is_only_an_administrative_cli_action() -> None:
    server_source = Path("src/github_workflow_mcp/server.py").read_text(
        encoding="utf-8"
    )
    cli_source = Path("src/github_workflow_mcp/cli.py").read_text(encoding="utf-8")

    assert "approve_proposal" not in server_source
    assert 'subparsers.add_parser("approve")' in cli_source


def test_runtime_package_does_not_import_course_fixtures_at_module_import() -> None:
    source = Path("src/github_workflow_mcp/server.py").read_text(encoding="utf-8")

    assert "fixtures/" not in source
