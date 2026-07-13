from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import coursectl


class CourseControlTests(unittest.TestCase):
    def test_reference_mode_allows_solution(self) -> None:
        config = {"course": {"solution_access": "reference"}}

        self.assertTrue(coursectl.solution_allowed("p01", config, {}))

    def test_gated_mode_requires_unlock(self) -> None:
        config = {"course": {"solution_access": "gated"}}

        self.assertFalse(coursectl.solution_allowed("p01", config, {}))
        self.assertTrue(
            coursectl.solution_allowed("p01", config, {"unlocked": {"p01": True}})
        )

    def test_start_project_copies_shared_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p01"

            coursectl.start_project("p01", destination)

            self.assertTrue((destination / "pyproject.toml").is_file())
            self.assertTrue((destination / "data/incidents.jsonl").is_file())
            self.assertTrue((destination / "fixtures/openai_responses.json").is_file())
            self.assertTrue((destination / "reports/experiment-contract.md").is_file())

    def test_start_project_two_copies_schema_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p02"

            coursectl.start_project("p02", destination)

            self.assertTrue((destination / "data/requests.jsonl").is_file())
            self.assertTrue((destination / "data/ground_truth.jsonl").is_file())
            self.assertTrue((destination / "reports/schema-decision.md").is_file())
            self.assertTrue((destination / "weak-schema-review.md").is_file())

    def test_start_project_three_copies_agent_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p03"

            coursectl.start_project("p03", destination)

            self.assertTrue((destination / "data/services.json").is_file())
            self.assertTrue((destination / "fixtures/scenarios.json").is_file())
            self.assertTrue((destination / "reports/tool-catalog.md").is_file())
            self.assertTrue((destination / "broken-agent-loop-review.md").is_file())

    def test_start_project_four_excludes_mentor_holdout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p04"

            coursectl.start_project("p04", destination)

            self.assertTrue((destination / "data/issues-dev.jsonl").is_file())
            self.assertTrue((destination / "data/known-issues.jsonl").is_file())
            self.assertTrue((destination / "reports/labeling-policy.md").is_file())
            self.assertFalse((destination / "data/holdout-issues.jsonl").exists())

    def test_start_project_five_copies_service_assets_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p05"

            coursectl.start_project("p05", destination)

            self.assertTrue((destination / "docker-compose.yml").is_file())
            self.assertTrue((destination / "data/job-scenarios.jsonl").is_file())
            self.assertTrue(
                (destination / "reports/architecture-decision.md").is_file()
            )
            self.assertTrue((destination / "broken-monolith-review.md").is_file())
            self.assertFalse((destination / "data/holdout-scenarios.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
