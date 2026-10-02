from app.tools.incident_tools import create_incident


def test_approved_incident_is_created():
    report = {
        "title": "UPI Payment Failure Investigation"
    }

    approval = {
        "approved": True,
        "action_allowed": True,
    }

    result = create_incident(report, approval)

    assert result["created"] is True
    assert result["status"] == "CREATED"
    assert result["incident_id"].startswith("INC-")
    assert result["title"] == "UPI Payment Failure Investigation"


def test_rejected_incident_is_blocked():
    report = {
        "title": "UPI Payment Failure Investigation"
    }

    approval = {
        "approved": False,
        "action_allowed": False,
    }

    result = create_incident(report, approval)

    assert result["created"] is False
    assert result["status"] == "BLOCKED"
    assert result["message"] == "Incident creation requires human approval."


def test_missing_approval_is_blocked():
    report = {
        "title": "UPI Payment Failure Investigation"
    }

    approval = {}

    result = create_incident(report, approval)

    assert result["created"] is False
    assert result["status"] == "BLOCKED"
