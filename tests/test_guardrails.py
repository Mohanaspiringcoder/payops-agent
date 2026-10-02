from app.analytics.guardrails import validate_investigation_response


EVIDENCE = {
    "total_failed": 8,
    "failure_reasons": {
        "TIMEOUT": 3,
        "INSUFFICIENT_FUNDS": 2,
        "BANK_ERROR": 2,
        "TECHNICAL_ERROR": 1,
    },
    "most_common_failure_reason": "TIMEOUT",
    "most_common_failure_count": 3,
    "most_common_failure_percentage": 37.5,
}


def test_valid_investigation_response_passes():
    response = """
OBSERVED EVIDENCE:
There were 8 failed transactions.
TIMEOUT was the most common failure reason with 3 failures.

INTERPRETATION:
TIMEOUT represents the largest observed failure category.

LIMITATIONS:
The available evidence does not establish the underlying cause.

NEXT INVESTIGATION:
Examine transaction-level timeout details.
"""

    result = validate_investigation_response(response, EVIDENCE)

    assert result["valid"] is True
    assert result["errors"] == []


def test_unsupported_network_claim_fails():
    response = """
OBSERVED EVIDENCE:
There were 8 failed transactions.

INTERPRETATION:
TIMEOUT failures were caused by network failure.

LIMITATIONS:
The available evidence is limited.

NEXT INVESTIGATION:
Examine network logs.
"""

    result = validate_investigation_response(response, EVIDENCE)

    assert result["valid"] is False
    assert any(
        "Unsupported causal claim detected" in error
        for error in result["errors"]
    )

def test_unsupported_numeric_relationship_fails():
    response = """
OBSERVED EVIDENCE:
There were 8 failed transactions.
TIMEOUT occurred 3 times.

INTERPRETATION:
TIMEOUT was 3 times more frequent than the total failure count.

LIMITATIONS:
The available evidence does not establish the underlying cause.

NEXT INVESTIGATION:
Examine transaction-level timeout details.
"""

    result = validate_investigation_response(
        response,
        EVIDENCE,
    )

    assert result["valid"] is False
    assert any(
        "numeric values" in error
        for error in result["errors"]
    )

def test_causal_claim_in_interpretation_fails_even_with_limitation_elsewhere():
    response = """
OBSERVED EVIDENCE:
There were 8 failed transactions.
TIMEOUT occurred 3 times.

INTERPRETATION:
The TIMEOUT failures could be caused by network problems or server overload.

LIMITATIONS:
The available evidence does not establish the underlying cause.

NEXT INVESTIGATION:
Examine transaction-level timestamps for the failed transactions.
"""

    result = validate_investigation_response(
        response,
        EVIDENCE,
    )

    assert result["valid"] is False
    assert any(
        "Unsupported causal claim" in error
        for error in result["errors"]
    )


def test_unsupported_suggests_primary_cause_fails():
    response = """
OBSERVED EVIDENCE:
There were 8 failed transactions.
TIMEOUT occurred 3 times.

INTERPRETATION:
The most common failure reason is TIMEOUT.
This suggests that network issues were the primary cause
of these failures.

LIMITATIONS:
The available evidence does not establish the underlying cause.

NEXT INVESTIGATION:
Examine transaction-level timestamps for failed transactions.
"""

    result = validate_investigation_response(
        response,
        EVIDENCE,
    )

    assert result["valid"] is False
