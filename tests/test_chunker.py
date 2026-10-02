from app.rag.chunker import chunk_operational_document
from app.rag.document_loader import load_operational_document


def test_chunk_operational_document():
    document = load_operational_document()

    chunks = chunk_operational_document(document)

    assert len(chunks) == 4

    failure_codes = [
        chunk["failure_code"]
        for chunk in chunks
    ]

    assert failure_codes == [
        "TIMEOUT",
        "INSUFFICIENT_FUNDS",
        "BANK_ERROR",
        "TECHNICAL_ERROR",
    ]


def test_each_chunk_contains_its_operational_context():
    document = load_operational_document()

    chunks = chunk_operational_document(document)

    timeout_chunk = next(
        chunk
        for chunk in chunks
        if chunk["failure_code"] == "TIMEOUT"
    )

    assert "### Meaning" in timeout_chunk["content"]
    assert "### Operational Interpretation" in timeout_chunk["content"]
    assert "### Investigation Guidance" in timeout_chunk["content"]
    assert "### Important Limitation" in timeout_chunk["content"]
