from app.rag.embeddings import OperationalKnowledgeEmbedder


def test_embed_text():
    embedder = OperationalKnowledgeEmbedder()

    embedding = embedder.embed_text(
        "TIMEOUT transactions should be investigated using transaction logs."
    )

    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(value, float) for value in embedding)
