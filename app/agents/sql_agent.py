from app.database.queries import (
    get_bank_failure_summary,
    get_failure_summary,
    get_success_rate,
)


def run_data_agent(question: str) -> dict:
    """
    Route an operational question to the appropriate database query
    and return verified structured evidence.

    The planner determines the high-level workflow.
    This agent is responsible for retrieving the required database
    evidence.
    """

    question_lower = question.lower()

    success_keywords = [
        "success rate",
        "successful transactions",
        "success percentage",
        "how many succeeded",
        "percentage of payments succeeded",
    ]

    bank_keywords = [
        "which bank",
        "which banks",
        "bank failures",
        "sender bank",
        "receiver bank",
        "failure by bank",
        "failures by bank",
        "breakdown by bank",
    ]

    investigation_keywords = [
        "investigate",
        "investigation",
        "root cause",
        "root-cause",
        "perform an investigation",
        "analyze why",
        "what should we investigate",
    ]

    failure_keywords = [
        "payment failures",
        "payment failure",
        "failed payments",
        "failed transactions",
        "failure reason",
        "failure reasons",
        "why are payments failing",
        "why did payments fail",
        "why are transactions failing",
        "timeouts",
        "bank errors",
    ]

    if any(keyword in question_lower for keyword in success_keywords):
        return {
            "intent": "SUCCESS_RATE",
            "evidence": get_success_rate(),
        }

    if any(keyword in question_lower for keyword in bank_keywords):
        return {
            "intent": "BANK_ANALYSIS",
            "evidence": get_bank_failure_summary(),
        }

    if (
        any(keyword in question_lower for keyword in investigation_keywords)
        or any(keyword in question_lower for keyword in failure_keywords)
    ):
        return {
            "intent": "FAILURE_ANALYSIS",
            "evidence": get_failure_summary(),
        }

    return {
        "intent": "UNKNOWN",
        "evidence": {},
    }
