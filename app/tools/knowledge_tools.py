from typing import Any

from app.rag.retriever import OperationalKnowledgeRetriever


retriever = OperationalKnowledgeRetriever()


def retrieve_operational_knowledge(
    question: str,
    top_k: int = 2,
) -> dict[str, Any]:
    """Retrieve relevant operational knowledge for an investigation."""

    results = retriever.retrieve(
        question=question,
        top_k=top_k,
    )

    return {
        "query": question,
        "results": results,
    }
