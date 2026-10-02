import app.graph.routing_graph as routing_graph


def test_success_rate_routing(monkeypatch):
    monkeypatch.setattr(
        routing_graph,
        "plan_request",
        lambda question: "SUCCESS_RATE",
    )

    result = routing_graph.graph.invoke(
        {
            "question": "What is the payment success rate?",
            "intent": "",
            "result": {},
        }
    )

    assert result["intent"] == "SUCCESS_RATE"
    assert result["result"]["total_transactions"] == 100
    assert result["result"]["successful_transactions"] == 92
    assert result["result"]["success_rate"] == 92.0


def test_failure_analysis_routing(monkeypatch):
    monkeypatch.setattr(
        routing_graph,
        "plan_request",
        lambda question: "FAILURE_ANALYSIS",
    )

    result = routing_graph.graph.invoke(
        {
            "question": "Why are payments failing?",
            "intent": "",
            "result": {},
        }
    )

    assert result["intent"] == "FAILURE_ANALYSIS"
    assert result["result"]["total_failed"] == 8
    assert result["result"]["failure_reasons"]["TIMEOUT"] == 3
    assert result["result"]["failure_reasons"]["BANK_ERROR"] == 2


def test_bank_analysis_routing(monkeypatch):
    monkeypatch.setattr(
        routing_graph,
        "plan_request",
        lambda question: "BANK_ANALYSIS",
    )

    result = routing_graph.graph.invoke(
        {
            "question": "Which bank has the most failures?",
            "intent": "",
            "result": {},
        }
    )

    assert result["intent"] == "BANK_ANALYSIS"
    assert result["result"]["failed_by_receiver_bank"]["AXIS"] == 2
    assert result["result"]["failed_by_receiver_bank"]["ICICI"] == 2


def test_investigation_routing(monkeypatch):
    monkeypatch.setattr(
        routing_graph,
        "plan_request",
        lambda question: "INVESTIGATION",
    )

    result = routing_graph.graph.invoke(
        {
            "question": "Investigate why payments are failing",
            "intent": "",
            "result": {},
        }
    )

    assert result["intent"] == "INVESTIGATION"

    investigation_result = result["result"]

    assert investigation_result["evidence"]["total_failed"] == 8
    assert (
        investigation_result["evidence"]["failure_reasons"]["TIMEOUT"]
        == 3
    )

    assert investigation_result["validation"]["valid"] is True


def test_out_of_scope_routing(monkeypatch):
    monkeypatch.setattr(
        routing_graph,
        "plan_request",
        lambda question: "OUT_OF_SCOPE",
    )

    result = routing_graph.graph.invoke(
        {
            "question": "What is the weather today?",
            "intent": "",
            "result": {},
        }
    )

    assert result["intent"] == "OUT_OF_SCOPE"
    assert result["result"]["status"] == "OUT_OF_SCOPE"
    assert "outside the scope" in result["result"]["message"].lower()
