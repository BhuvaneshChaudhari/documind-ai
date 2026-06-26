import logging

from services.vector_store import search_similar

logger = logging.getLogger(__name__)


def search(query: str, k: int = 5) -> list[dict]:
    results = search_similar(query, k=k)

    return [
        {
            "text": r["text"],
            "source": r["metadata"]["source"],
            "chunk_id": r["id"],
            "score": round(float(r["score"]), 4),
        }
        for r in results
    ]
