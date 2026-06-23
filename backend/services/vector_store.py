import logging

import chromadb
from chromadb.config import Settings

from config import CHROMA_DIR, COLLECTION_NAME

logger = logging.getLogger(__name__)

_client = None
_collection = None


def _get_client():
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB client initialized at {CHROMA_DIR}")
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        existing = _collection.count()
        logger.info(f"Collection '{COLLECTION_NAME}' ready ({existing} existing records)")
    return _collection


def delete_all_chunks() -> None:
    collection = get_collection()
    existing = collection.count()
    if existing == 0:
        return
    all_ids = collection.get()["ids"]
    collection.delete(ids=all_ids)
    logger.info(f"Deleted all {existing} chunks from collection")


def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
    filename: str,
) -> int:
    collection = get_collection()

    ids = [f"{filename}_chunk_{c['index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": filename,
            "chunk_index": c["index"],
            "char_count": c["char_count"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    total = collection.count()
    logger.info(f"Stored {len(chunks)} chunks from '{filename}' (total in DB: {total})")
    return total


def search_similar(
    query_embedding: list[float],
    k: int = 5,
) -> list[dict]:
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    if results["ids"] and results["ids"][0]:
        for idx, doc_id in enumerate(results["ids"][0]):
            hits.append({
                "id": doc_id,
                "text": results["documents"][0][idx],
                "metadata": results["metadatas"][0][idx],
                "score": 1 - results["distances"][0][idx],
            })

    return hits
