from app.graph.investigation_graph import graph


def build_state(approval_status: str) -> dict:
    return {
        "question": "Investigate why payments are failing",
        "evidence": {},
        "operational_knowledge": {},
        "investigation": "",
        "validation": {},
        "retry_count": 0,
        "report": {},
        "approval_status": approval_status,
        "approval": {},
        "incident": {},
    }


def test_approved_investigation_creates_incident():
    result = graph.invoke(build_state("APPROVED"))

    assert result["validation"]["valid"] is True

    assert result["report"]["status"] == "DRAFT"
    assert result["report"]["requires_human_review"] is True

    assert result["approval"]["approved"] is True
    assert result["approval"]["action_allowed"] is True

    assert result["incident"]["created"] is True
    assert result["incident"]["status"] == "CREATED"
    assert result["incident"]["incident_id"].startswith("INC-")


def test_rejected_investigation_blocks_incident():
    result = graph.invoke(build_state("REJECTED"))

    assert result["validation"]["valid"] is True

    assert result["report"]["status"] == "DRAFT"
    assert result["report"]["requires_human_review"] is True

    assert result["approval"]["approved"] is False
    assert result["approval"]["action_allowed"] is False

    assert result["incident"]["created"] is False
    assert result["incident"]["status"] == "BLOCKED"
