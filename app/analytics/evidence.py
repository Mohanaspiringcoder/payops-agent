from typing import Any


def build_failure_evidence(failure_data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert raw failure data into deterministic, verified evidence.

    The calculations in this layer are performed by Python rather than
    the LLM so that factual metrics remain reliable and reproducible.
    """

    total_failed = failure_data.get("total_failed", 0)
    failure_reasons = failure_data.get("failure_reasons", {})

    if not failure_reasons:
        return {
            "total_failed": total_failed,
            "failure_reasons": {},
            "most_common_failure_reason": None,
            "most_common_failure_count": 0,
            "most_common_failure_percentage": 0.0,
        }

    most_common_reason, most_common_count = max(
        failure_reasons.items(),
        key=lambda item: item[1],
    )

    percentage = (
        (most_common_count / total_failed) * 100
        if total_failed > 0
        else 0.0
    )

    return {
        "total_failed": total_failed,
        "failure_reasons": failure_reasons,
        "most_common_failure_reason": most_common_reason,
        "most_common_failure_count": most_common_count,
        "most_common_failure_percentage": round(percentage, 2),
    }
