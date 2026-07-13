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

    def test_start_project_six_excludes_recovery_holdout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p06"

            coursectl.start_project("p06", destination)

            self.assertTrue((destination / "data/release-manifests.jsonl").is_file())
            self.assertTrue((destination / "fixtures/crash-replay.json").is_file())
            self.assertTrue(
                (destination / "reports/state-and-graph-design.md").is_file()
            )
            self.assertTrue((destination / "broken-graph-review.md").is_file())
            self.assertFalse((destination / "data/holdout-scenarios.jsonl").exists())

    def test_start_project_seven_copies_delivery_assets_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p07"

            coursectl.start_project("p07", destination)

            self.assertTrue((destination / "Dockerfile").is_file())
            self.assertTrue((destination / "docker-compose.yml").is_file())
            self.assertTrue((destination / "fixtures/github-api.json").is_file())
            self.assertTrue((destination / "reports/capability-catalog.md").is_file())
            self.assertTrue((destination / "broken-tool-catalog-review.md").is_file())
            self.assertFalse((destination / "data/holdout-scenarios.jsonl").exists())

    def test_start_project_eight_copies_studio_but_not_mentor_challenges(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p08"

            coursectl.start_project("p08", destination)

            self.assertTrue((destination / "data/capstone-options.json").is_file())
            self.assertTrue((destination / "fixtures/weak-proposal.json").is_file())
            self.assertTrue((destination / "reports/project-brief.md").is_file())
            self.assertTrue((destination / "candidate-briefs.md").is_file())
            self.assertFalse((destination / "mentor-challenges.jsonl").exists())

    def test_project_eight_reference_adds_exemplar_not_product_solution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p08-reference"

            coursectl.materialize_solution("p08", destination)

            self.assertTrue(
                (destination / "examples/support-escalation-proposal.json").is_file()
            )
            self.assertTrue(
                (destination / "src/capstone_studio/validator.py").is_file()
            )
            self.assertFalse((destination / "src/capstone_product").exists())


if __name__ == "__main__":
    unittest.main()
