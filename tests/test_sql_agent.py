from app.agents.sql_agent import run_data_agent


def test_success_rate_data_agent():
    result = run_data_agent("What is the payment success rate?")

    assert result["intent"] == "SUCCESS_RATE"
    assert result["evidence"]["total_transactions"] == 100
    assert result["evidence"]["successful_transactions"] == 92
    assert result["evidence"]["success_rate"] == 92.0


def test_failure_analysis_data_agent():
    result = run_data_agent("Why are payments failing?")

    assert result["intent"] == "FAILURE_ANALYSIS"
    assert result["evidence"]["total_failed"] == 8
    assert result["evidence"]["failure_reasons"]["TIMEOUT"] == 3
    assert result["evidence"]["failure_reasons"]["BANK_ERROR"] == 2


def test_bank_analysis_data_agent():
    result = run_data_agent("Which bank has the most failures?")

    assert result["intent"] == "BANK_ANALYSIS"
    assert result["evidence"]["failed_by_receiver_bank"]["AXIS"] == 2
    assert result["evidence"]["failed_by_receiver_bank"]["ICICI"] == 2


def test_unknown_data_agent_request():
    result = run_data_agent("What is the weather today?")

    assert result["intent"] == "UNKNOWN"
    assert result["evidence"] == {}
