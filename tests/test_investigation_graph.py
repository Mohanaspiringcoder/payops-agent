from langgraph.types import Command

from app.graph.investigation_graph import graph


def build_state(thread_id: str) -> dict:
    return {
        "thread_id": thread_id,
        "question": "Investigate why payments are failing",
        "evidence": {},
        "operational_knowledge": {},
        "investigation": "",
        "validation": {},
        "retry_count": 0,
        "report": {},
        "approval_status": "REJECTED",
        "approval": {},
        "incident": {},
    }


def build_config(thread_id: str) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def test_approved_investigation_pauses_and_creates_incident():
    thread_id = "test-approved-investigation"

    paused = graph.invoke(
        build_state(thread_id),
        config=build_config(thread_id),
    )

    assert paused["report"]["status"] == "DRAFT"
    assert paused["report"]["requires_human_review"] is True
    assert paused["approval"] == {}
    assert paused["incident"] == {}
    assert paused["__interrupt__"]

    result = graph.invoke(
        Command(
            resume={
                "decision": "APPROVED",
            }
        ),
        config=build_config(thread_id),
    )

    assert result["validation"]["valid"] is True

    assert result["approval"]["approved"] is True
    assert result["approval"]["action_allowed"] is True
    assert result["approval"]["approval_status"] == "APPROVED"

    assert result["incident"]["created"] is True
    assert result["incident"]["status"] == "CREATED"
    assert result["incident"]["incident_id"].startswith("INC-")


def test_rejected_investigation_pauses_and_blocks_incident():
    thread_id = "test-rejected-investigation"

    paused = graph.invoke(
        build_state(thread_id),
        config=build_config(thread_id),
    )

    assert paused["report"]["status"] == "DRAFT"
    assert paused["report"]["requires_human_review"] is True
    assert paused["approval"] == {}
    assert paused["incident"] == {}
    assert paused["__interrupt__"]

    result = graph.invoke(
        Command(
            resume={
                "decision": "REJECTED",
            }
        ),
        config=build_config(thread_id),
    )

    assert result["validation"]["valid"] is True

    assert result["approval"]["approved"] is False
    assert result["approval"]["action_allowed"] is False
    assert result["approval"]["approval_status"] == "REJECTED"

    assert result["incident"]["created"] is False
    assert result["incident"]["status"] == "BLOCKED"
