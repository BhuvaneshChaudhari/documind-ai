from fastapi import APIRouter
from config import LLM_MODEL, EMBEDDING_MODEL

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/config")
async def config():
    return {"llm_model": LLM_MODEL, "embedding_model": EMBEDDING_MODEL}
