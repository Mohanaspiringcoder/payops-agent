def generate_incident_report(
    question: str,
    investigation: str,
    evidence: dict,
) -> dict:
    """
    Generate a structured incident report from validated investigation output.
    """

    return {
        "title": "UPI Payment Failure Investigation",
        "question": question,
        "evidence": evidence,
        "investigation": investigation,
        "status": "DRAFT",
        "requires_human_review": True,
    }
