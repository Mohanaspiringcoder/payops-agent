from app.rag.document_loader import load_operational_document


def test_load_operational_document():
    document = load_operational_document()

    assert document
    assert "# UPI Payment Failure Code Reference" in document
    assert "## TIMEOUT" in document
    assert "## INSUFFICIENT_FUNDS" in document
    assert "## BANK_ERROR" in document
    assert "## TECHNICAL_ERROR" in document
