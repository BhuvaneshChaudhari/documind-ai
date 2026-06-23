import logging

from fastapi import APIRouter, HTTPException

from models import SearchRequest
from retrieval.hybrid_retriever import retrieve, ensure_bm25_ready

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search")
async def search_documents(body: SearchRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    ensure_bm25_ready()

    results = retrieve(body.query, bm25_k=5, vector_k=5, final_k=5)
    return results
