from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.validate_course import (
    markdown_without_code,
    validate_json_assets,
    validate_markdown_links,
    validate_toml_assets,
    validate_workflow_security,
)
from scripts.verify_reference import SENSITIVE_ENVIRONMENT_KEYS, offline_environment


class CourseValidationTests(unittest.TestCase):
    def test_markdown_code_is_not_treated_as_a_link(self) -> None:
        content = """Before
```python
globals()[response.tool_name](**arguments)
```
After
"""

        self.assertNotIn("arguments", markdown_without_code(content))

    def test_missing_markdown_target_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("[missing](docs/nope.md)\n")

            issues, checked = validate_markdown_links(root)

            self.assertEqual(1, checked)
            self.assertEqual(1, len(issues))
            self.assertIn("docs/nope.md", issues[0])

    def test_fenced_false_link_and_existing_link_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "target.md").write_text("# Target\n")
            (root / "README.md").write_text(
                "[target](target.md)\n```python\nvalue[key](not-a-link)\n```\n"
            )

            issues, checked = validate_markdown_links(root)

            self.assertEqual(2, checked)
            self.assertEqual([], issues)

    def test_invalid_jsonl_reports_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "items.jsonl").write_text('{"ok": true}\nnot-json\n')

            issues, checked = validate_json_assets(root)

            self.assertEqual(1, checked)
            self.assertEqual(1, len(issues))
            self.assertIn("items.jsonl:2", issues[0])

    def test_uv_lock_is_validated_as_toml(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "uv.lock").write_text("not = [valid\n")

            issues, checked = validate_toml_assets(root)

            self.assertEqual(1, checked)
            self.assertEqual(1, len(issues))
            self.assertIn("uv.lock", issues[0])

    def test_reference_environment_removes_live_credentials(self) -> None:
        credentials = dict.fromkeys(SENSITIVE_ENVIRONMENT_KEYS, "must-not-leak")
        with patch.dict(os.environ, credentials, clear=False):
            environment = offline_environment()

            self.assertTrue(SENSITIVE_ENVIRONMENT_KEYS.isdisjoint(environment))
            self.assertEqual("true", environment["CI"])

    def test_workflow_requires_read_permission_and_full_action_sha(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workflows = root / ".github/workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text(
                """name: CI
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
"""
            )

            issues, checked = validate_workflow_security(root)

            self.assertEqual(1, checked)
            self.assertEqual(1, len(issues))
            self.assertIn("full commit SHA", issues[0])


if __name__ == "__main__":
    unittest.main()
