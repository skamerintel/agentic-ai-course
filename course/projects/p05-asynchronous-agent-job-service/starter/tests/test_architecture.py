from pathlib import Path


def test_http_layer_does_not_import_provider_sdk_or_sqlalchemy() -> None:
    source = Path("src/job_service/app.py").read_text(encoding="utf-8").casefold()

    assert "from openai" not in source
    assert "import openai" not in source
    assert "from sqlalchemy" not in source
    assert "import sqlalchemy" not in source
