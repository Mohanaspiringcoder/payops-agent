from app.rag.chunker import chunk_operational_document
from app.rag.document_loader import load_operational_document
from app.rag.vector_store import OperationalKnowledgeVectorStore


def main() -> None:
    document = load_operational_document()
    chunks = chunk_operational_document(document)

    vector_store = OperationalKnowledgeVectorStore()
    vector_store.index_chunks(chunks)

    print(f"Indexed {len(chunks)} operational knowledge chunks.")


if __name__ == "__main__":
    main()
