from app.tools.approval_tools import request_human_approval


def test_approved_action_is_allowed():
    report = {
        "title": "UPI Payment Failure Investigation"
    }

    result = request_human_approval(
        report=report,
        decision="APPROVED",
    )

    assert result["approval_status"] == "APPROVED"
    assert result["approved"] is True
    assert result["action_allowed"] is True


def test_rejected_action_is_blocked():
    report = {
        "title": "UPI Payment Failure Investigation"
    }

    result = request_human_approval(
        report=report,
        decision="REJECTED",
    )

    assert result["approval_status"] == "REJECTED"
    assert result["approved"] is False
    assert result["action_allowed"] is False


def test_invalid_approval_decision():
    report = {
        "title": "UPI Payment Failure Investigation"
    }

    try:
        request_human_approval(
            report=report,
            decision="MAYBE",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "decision must be either" in str(exc)
