from app.agents.planner import plan_request


def test_success_rate_intent():
    assert plan_request("What is the payment success rate?") == "SUCCESS_RATE"


def test_failure_analysis_intent():
    assert plan_request("Why are payments failing?") == "FAILURE_ANALYSIS"


def test_bank_analysis_intent():
    assert plan_request("Which bank has the most failures?") == "BANK_ANALYSIS"
