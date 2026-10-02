from pathlib import Path
from typing import Any

import chromadb

from app.rag.embeddings import OperationalKnowledgeEmbedder


VECTOR_STORE_PATH = Path("data/generated/chroma")
COLLECTION_NAME = "operational_knowledge"


class OperationalKnowledgeVectorStore:
    """Persistent ChromaDB store for operational knowledge."""

    def __init__(self) -> None:
        VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_STORE_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        self.embedder = OperationalKnowledgeEmbedder()

    def index_chunks(
        self,
        chunks: list[dict[str, str]],
    ) -> None:
        """Index operational knowledge chunks."""

        documents = [
            chunk["content"]
            for chunk in chunks
        ]

        ids = [
            chunk["failure_code"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "failure_code": chunk["failure_code"],
            }
            for chunk in chunks
        ]

        embeddings = [
            self.embedder.embed_text(document)
            for document in documents
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(
        self,
        question: str,
        top_k: int = 1,
    ) -> list[dict[str, Any]]:
        """Search indexed knowledge using semantic similarity."""

        question_embedding = self.embedder.embed_text(question)

        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
        )

        matches = []

        for index, document in enumerate(results["documents"][0]):
            matches.append(
                {
                    "content": document,
                    "failure_code": results["metadatas"][0][index][
                        "failure_code"
                    ],
                    "distance": results["distances"][0][index],
                }
            )

        return matches
