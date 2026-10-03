from langgraph.types import Command
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
        },
config={
    "configurable": {
        "thread_id": "test-success-rate-routing",
    }
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
        },
config={
    "configurable": {
        "thread_id": "test-failure-analysis-routing",
    }
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
        },
config={
    "configurable": {
        "thread_id": "test-bank-analysis-routing",
    }
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

    thread_id = "test-routing-investigation"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    paused = routing_graph.graph.invoke(
        {
            "thread_id": thread_id,
            "question": "Investigate why payments are failing",
            "intent": "",
            "result": {},
        },
        config=config,
    )

    assert paused["intent"] == "INVESTIGATION"
    assert paused["result"] == {}
    assert paused["__interrupt__"]

    interrupt_payload = paused["__interrupt__"][0].value

    assert interrupt_payload["type"] == "incident_approval"
    assert interrupt_payload["report"]["status"] == "DRAFT"

    result = routing_graph.graph.invoke(
        Command(
            resume={
                "decision": "APPROVED",
            }
        ),
        config=config,
    )

    assert result["intent"] == "INVESTIGATION"

    investigation_result = result["result"]

    assert investigation_result["evidence"]["total_failed"] == 8
    assert (
        investigation_result["evidence"]["failure_reasons"]["TIMEOUT"]
        == 3
    )
    assert investigation_result["validation"]["valid"] is True
    assert investigation_result["approval"]["approved"] is True
    assert investigation_result["incident"]["status"] == "CREATED"


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
        },
config={
    "configurable": {
        "thread_id": "test-out-of-scope-routing",
    }
}
    )

    assert result["intent"] == "OUT_OF_SCOPE"
    assert result["result"]["status"] == "OUT_OF_SCOPE"
    assert "outside the scope" in result["result"]["message"].lower()
