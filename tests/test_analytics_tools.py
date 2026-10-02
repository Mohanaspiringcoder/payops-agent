from app.tools.analytics_tools import calculate_success_rate


def test_calculate_success_rate():
    result = calculate_success_rate.invoke({})

    assert result["total_transactions"] == 100
    assert result["successful_transactions"] == 92
    assert result["success_rate"] == 92.0
