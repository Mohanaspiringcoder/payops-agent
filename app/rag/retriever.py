from typing import Any

from app.rag.vector_store import OperationalKnowledgeVectorStore


class OperationalKnowledgeRetriever:
    """Retrieve operational knowledge from the persistent vector store."""

    def __init__(self) -> None:
        self.vector_store = OperationalKnowledgeVectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 1,
    ) -> list[dict[str, Any]]:
        """Return the most relevant operational knowledge."""

        return self.vector_store.search(
            question=question,
            top_k=top_k,
        )
