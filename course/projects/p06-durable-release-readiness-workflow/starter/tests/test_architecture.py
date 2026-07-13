from pathlib import Path


def test_graph_layer_does_not_import_openai_sdk() -> None:
    source = Path("src/release_workflow/workflow.py").read_text(encoding="utf-8")

    assert "from openai" not in source
    assert "import openai" not in source
