import logging
import time

from fastapi import APIRouter, HTTPException

from models import QuestionRequest, QuestionResponse, SourceItem
from retrieval.hybrid_retriever import retrieve, ensure_bm25_ready
from services.llm_client import generate_answer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    total_start = time.monotonic()

    ensure_bm25_ready()

    retrieve_start = time.monotonic()
    results = retrieve(
        request.question,
        bm25_k=5,
        vector_k=5,
        final_k=5,
    )
    retrieve_time = time.monotonic() - retrieve_start

    hybrid = results["hybrid_results"]
    if not hybrid:
        logger.warning("No relevant chunks found for the query")
        return {
            "answer": "I could not find this information in the uploaded documents.",
            "confidence_score": 0.0,
            "sources": [],
        }

    logger.info(
        f"Retrieval: {len(hybrid)} chunks in {retrieve_time:.3f}s"
    )

    llm_start = time.monotonic()
    llm_result = generate_answer(request.question, hybrid)
    llm_time = time.monotonic() - llm_start

    top_score = hybrid[0]["final_score"]
    avg_score = sum(c["final_score"] for c in hybrid) / len(hybrid)

    is_not_found = "could not find this information" in llm_result["answer"].lower()
    confidence_score = round(min(top_score * 0.7 + avg_score * 0.3 + 0.15, 1.0), 4)
    if is_not_found:
        confidence_score = round(min(confidence_score, 0.3), 4)

    total_time = time.monotonic() - total_start

    logger.info(
        f"Total /ask: {total_time:.3f}s "
        f"(retrieval={retrieve_time:.3f}s, llm={llm_time:.3f}s)"
    )

    sources = [
        SourceItem(
            text=c["text"].strip(),
            source_file=c["source"],
            score=c["final_score"],
        )
        for c in hybrid
    ]

    return QuestionResponse(
        answer=llm_result["answer"],
        confidence_score=confidence_score,
        sources=sources,
    )
