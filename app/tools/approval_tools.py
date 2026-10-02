from typing import Literal


ApprovalStatus = Literal["APPROVED", "REJECTED"]


def request_human_approval(
    report: dict,
    decision: ApprovalStatus,
) -> dict:
    """
    Record a human decision for an incident report.

    This is a simulated approval layer.
    No real operational action is performed here.
    """

    if decision not in {"APPROVED", "REJECTED"}:
        raise ValueError(
            "decision must be either 'APPROVED' or 'REJECTED'"
        )

    return {
        "report_id": report.get("title"),
        "approval_status": decision,
        "approved": decision == "APPROVED",
        "action_allowed": decision == "APPROVED",
    }
