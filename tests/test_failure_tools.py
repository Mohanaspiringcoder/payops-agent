from app.tools.failure_tools import get_failure_summary


def test_get_failure_summary():
    result = get_failure_summary.invoke({})

    assert result["total_failed"] == 8
    assert result["failure_reasons"]["TIMEOUT"] == 3
    assert result["failure_reasons"]["BANK_ERROR"] == 2
    assert result["failure_reasons"]["INSUFFICIENT_FUNDS"] == 2
    assert result["failure_reasons"]["TECHNICAL_ERROR"] == 1
