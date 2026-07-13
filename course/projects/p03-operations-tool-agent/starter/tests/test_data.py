from operations_agent.data import OperationsStore, load_scenarios


def test_loads_scenarios_and_deduplicates_incidents() -> None:
    scenarios = load_scenarios("fixtures/scenarios.json")
    store = OperationsStore("data")

    incidents = store.search_incidents("checkout", 5)

    assert len(scenarios) == 9
    assert [item["incident_id"] for item in incidents] == ["INC-101", "INC-102"]
