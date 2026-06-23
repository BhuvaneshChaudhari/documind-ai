import logging

from retrieval import bm25_retriever, vector_retriever
from services.vector_store import get_collection

logger = logging.getLogger(__name__)


def _normalize(results: list[dict]) -> list[dict]:
    if not results:
        return results
    scores = [r["score"] for r in results]
    lo, hi = min(scores), max(scores)
    if hi == lo:
        for r in results:
            r["normalized_score"] = 1.0
    else:
        for r in results:
            r["normalized_score"] = round((r["score"] - lo) / (hi - lo), 4)
    return results


def _use_raw_scores(results: list[dict]) -> list[dict]:
    for r in results:
        r["normalized_score"] = r["score"]
    return results


def _load_all_chunks_from_db() -> list[dict]:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    results = collection.get(include=["documents", "metadatas"])
    chunks = []
    for i in range(len(results["ids"])):
        chunks.append({
            "id": results["ids"][i],
            "text": results["documents"][i],
            "metadata": results["metadatas"][i],
        })
    return chunks


def ensure_bm25_ready() -> None:
    chunks = _load_all_chunks_from_db()
    if chunks:
        bm25_retriever.rebuild_index(chunks)
        logger.info(f"BM25 index primed with {len(chunks)} chunks")
    else:
        logger.info("No chunks in DB — BM25 index left empty")


def retrieve(
    query: str,
    bm25_k: int = 5,
    vector_k: int = 5,
    final_k: int = 5,
    bm25_weight: float = 0.5,
) -> dict:
    bm25_results = bm25_retriever.search(query, k=bm25_k)
    vec_results = vector_retriever.search(query, k=vector_k)

    logger.info(f"BM25 results: {len(bm25_results)}, Vector results: {len(vec_results)}")

    bm25_results = _normalize(bm25_results) if bm25_results else []
    vec_results = _use_raw_scores(vec_results)

    merged: dict[str, dict] = {}
    for r in bm25_results:
        merged[r["chunk_id"]] = {
            "text": r["text"],
            "source": r["source"],
            "bm25_score": r["normalized_score"],
            "vector_score": 0.0,
        }
    for r in vec_results:
        if r["chunk_id"] in merged:
            merged[r["chunk_id"]]["vector_score"] = r["normalized_score"]
        else:
            merged[r["chunk_id"]] = {
                "text": r["text"],
                "source": r["source"],
                "bm25_score": 0.0,
                "vector_score": r["normalized_score"],
            }

    hybrid = []
    for cid, data in merged.items():
        data["final_score"] = round(
            bm25_weight * data["bm25_score"]
            + (1 - bm25_weight) * data["vector_score"],
            4,
        )
        data["chunk_id"] = cid
        hybrid.append(data)

    hybrid.sort(key=lambda x: x["final_score"], reverse=True)
    hybrid = hybrid[:final_k]

    logger.info(f"Hybrid results: {len(hybrid)} (after dedup + rank)")

    return {
        "bm25_results": bm25_results,
        "vector_results": vec_results,
        "hybrid_results": hybrid,
    }
