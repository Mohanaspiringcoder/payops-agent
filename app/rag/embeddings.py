from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class OperationalKnowledgeEmbedder:
    """Create embeddings for operational knowledge."""

    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_text(self, text: str) -> list[float]:
        """Convert text into an embedding vector."""
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()
