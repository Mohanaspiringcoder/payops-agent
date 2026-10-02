from app.tools.bank_tools import get_bank_failure_summary


def test_get_bank_failure_summary():
    result = get_bank_failure_summary.invoke({})

    assert result["failed_by_sender_bank"]["PNB"] == 3
    assert result["failed_by_sender_bank"]["KOTAK"] == 2
    assert result["failed_by_sender_bank"]["HDFC"] == 2
    assert result["failed_by_sender_bank"]["SBI"] == 1

    assert result["failed_by_receiver_bank"]["AXIS"] == 2
    assert result["failed_by_receiver_bank"]["ICICI"] == 2
