from app.analytics.evidence import build_failure_evidence


def test_build_failure_evidence():
    failure_data = {
        "total_failed": 8,
        "failure_reasons": {
            "TIMEOUT": 3,
            "INSUFFICIENT_FUNDS": 2,
            "BANK_ERROR": 2,
            "TECHNICAL_ERROR": 1,
        },
    }

    result = build_failure_evidence(failure_data)

    assert result["total_failed"] == 8
    assert result["failure_reasons"]["TIMEOUT"] == 3
    assert result["failure_reasons"]["INSUFFICIENT_FUNDS"] == 2
    assert result["failure_reasons"]["BANK_ERROR"] == 2
    assert result["failure_reasons"]["TECHNICAL_ERROR"] == 1

    assert result["most_common_failure_reason"] == "TIMEOUT"
    assert result["most_common_failure_count"] == 3
    assert result["most_common_failure_percentage"] == 37.5
