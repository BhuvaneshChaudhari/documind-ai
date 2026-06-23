import logging
import re

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

_bm25: BM25Okapi | None = None
_chunks_data: list[dict] = []
_dirty: bool = True


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def rebuild_index(chunks: list[dict]) -> None:
    global _bm25, _chunks_data, _dirty
    _chunks_data = chunks
    tokenized = [_tokenize(c["text"]) for c in chunks]
    _bm25 = BM25Okapi(tokenized)
    _dirty = False
    logger.info(f"BM25 index rebuilt with {len(chunks)} chunks")


def mark_dirty() -> None:
    global _dirty
    _dirty = True


def clear_index() -> None:
    global _bm25, _chunks_data, _dirty
    _bm25 = None
    _chunks_data = []
    _dirty = True
    logger.info("BM25 index cleared")


def search(query: str, k: int = 5) -> list[dict]:
    if _bm25 is None or _dirty:
        logger.warning("BM25 index not ready or stale — run rebuild_index() first")
        return []

    tokens = _tokenize(query)
    scores = _bm25.get_scores(tokens)

    indexed = sorted(
        enumerate(scores), key=lambda x: x[1], reverse=True
    )

    results = []
    for idx, score in indexed:
        if score <= 0:
            continue
        c = _chunks_data[idx]
        results.append({
            "text": c["text"],
            "source": c["metadata"]["source"],
            "chunk_id": c["id"],
            "score": round(float(score), 4),
        })
        if len(results) >= k:
            break

    return results
