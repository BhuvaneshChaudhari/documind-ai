import logging

from services.embedder import generate_embeddings
from services.vector_store import search_similar

logger = logging.getLogger(__name__)


def search(query: str, k: int = 5) -> list[dict]:
    embedding = generate_embeddings([query])[0]
    results = search_similar(embedding, k=k)

    return [
        {
            "text": r["text"],
            "source": r["metadata"]["source"],
            "chunk_id": r["id"],
            "score": round(float(r["score"]), 4),
        }
        for r in results
    ]
