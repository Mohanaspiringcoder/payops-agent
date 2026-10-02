from app.tools.knowledge_tools import retrieve_operational_knowledge


def test_retrieve_operational_knowledge():
    result = retrieve_operational_knowledge(
        "What should I investigate when a payment times out?"
    )

    assert result["query"] == (
        "What should I investigate when a payment times out?"
    )

    assert result["results"]

    first_result = result["results"][0]

    assert first_result["failure_code"] == "TIMEOUT"
    assert first_result["content"]
    assert first_result["distance"] >= 0
