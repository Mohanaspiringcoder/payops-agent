from app.rag.chunker import chunk_operational_document
from app.rag.document_loader import load_operational_document
from app.rag.vector_store import OperationalKnowledgeVectorStore


def test_vector_store_indexes_and_retrieves():
    document = load_operational_document()
    chunks = chunk_operational_document(document)

    store = OperationalKnowledgeVectorStore()

    store.index_chunks(chunks)

    results = store.search(
        "What should I investigate when a payment times out?",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["failure_code"] == "TIMEOUT"
    assert results[0]["content"]
    assert results[0]["distance"] >= 0
