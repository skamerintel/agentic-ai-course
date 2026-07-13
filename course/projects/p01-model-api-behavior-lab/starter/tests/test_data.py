from model_api_lab.data import load_incidents


def test_loads_all_supplied_incidents() -> None:
    incidents = load_incidents("data/incidents.jsonl")

    assert len(incidents) == 8
    assert incidents[0].id == "INC-001"
    assert len(incidents[0].fact_checks) == 5
