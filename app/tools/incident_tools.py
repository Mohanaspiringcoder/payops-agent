from uuid import uuid4


def create_incident(report: dict, approval: dict) -> dict:
    """
    Create a simulated incident after human approval.

    No real external system is called.
    """

    if approval.get("action_allowed") is not True:
        return {
            "created": False,
            "status": "BLOCKED",
            "message": "Incident creation requires human approval.",
        }

    incident_id = f"INC-{uuid4().hex[:12].upper()}"

    return {
        "created": True,
        "status": "CREATED",
        "incident_id": incident_id,
        "title": report.get(
            "title",
            "UPI Payment Failure Investigation",
        ),
        "message": "Simulated incident created successfully.",
    }
