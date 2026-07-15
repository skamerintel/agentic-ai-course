from model_api_lab.experiment import run_offline


def test_offline_experiment_runs_all_fixture_records() -> None:
    records = run_offline("data/incidents.jsonl", "fixtures")

    assert len(records) == 3
    assert {record.result.api for record in records} == {"messages"}
    assert all(record.incident_id.startswith("INC-") for record in records)
