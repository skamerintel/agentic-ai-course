from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import coursectl


class CourseControlTests(unittest.TestCase):
    def test_startup_guides_cover_projects_and_reference_copied_files(self) -> None:
        self.assertEqual(set(coursectl.PROJECTS), set(coursectl.PROJECT_GUIDES))
        with tempfile.TemporaryDirectory() as temporary:
            for project, guide in coursectl.PROJECT_GUIDES.items():
                destination = Path(temporary) / project
                coursectl.start_project(project, destination)
                for relative_path in guide.first_reads:
                    self.assertTrue(
                        (destination / relative_path).is_file(),
                        f"{project} startup guide references missing {relative_path}",
                    )

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
            self.assertIn(
                "normalization and scoring",
                (destination / "START_HERE.md").read_text(),
            )

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
            start_here = (destination / "START_HERE.md").read_text()
            self.assertIn("Three strict model/fixture tests", start_here)
            self.assertIn("complete the M25 proposal artifacts", start_here)

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
            self.assertIn(
                "automated tests should pass",
                (destination / "START_HERE.md").read_text(),
            )

    def test_start_summary_quotes_destination_and_explains_test_gate(self) -> None:
        destination = Path("/tmp/a learner workspace")

        summary = coursectl.render_start_summary("p08", destination)

        self.assertIn("cd '/tmp/a learner workspace'", summary)
        self.assertIn("seven proposal and artifact validator TODO gates", summary)
        self.assertIn("Read START_HERE.md", summary)

    def test_main_start_prints_guidance_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p08"
            output = io.StringIO()

            with redirect_stdout(output):
                result = coursectl.main(["start", "p08", str(destination)])

            self.assertEqual(0, result)
            self.assertIn("Created p08 learner workspace", output.getvalue())
            self.assertIn("uv run pytest", output.getvalue())

    def test_main_start_quiet_preserves_path_only_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "p08"
            output = io.StringIO()

            with redirect_stdout(output):
                result = coursectl.main(["start", "p08", str(destination), "--quiet"])

            self.assertEqual(0, result)
            self.assertEqual(f"{destination.resolve()}\n", output.getvalue())


if __name__ == "__main__":
    unittest.main()
