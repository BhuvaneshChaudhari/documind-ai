import logging
import asyncio

from fastapi import APIRouter, HTTPException, UploadFile, File

from config import UPLOAD_DIR, MAX_FILE_SIZE_MB, CHUNK_SIZE, CHUNK_OVERLAP
from services.pdf_processor import extract_text_from_pdf
from services.chunker import chunk_text
from services.vector_store import store_chunks, delete_all_chunks
from retrieval.bm25_retriever import clear_index

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
CHUNK_PREVIEW_COUNT = 2


async def _run_blocking(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fn, *args)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / file.filename
    if file_path.exists():
        logger.warning(f"Overwriting existing file: {file_path}")
        file_path.unlink()

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit",
        )

    try:
        await _run_blocking(delete_all_chunks)
        await _run_blocking(clear_index)
        logger.info("Cleared previous documents")

        await _run_blocking(file_path.write_bytes, contents)
        logger.info(f"Saved: {file_path} ({len(contents)} bytes)")

        text = await _run_blocking(extract_text_from_pdf, str(file_path))
        chunks = await _run_blocking(chunk_text, text, CHUNK_SIZE, CHUNK_OVERLAP)

        logger.info(f"Created {len(chunks)} chunks")

        total_stored = await _run_blocking(store_chunks, chunks, file.filename)
        await _run_blocking(clear_index)

        previews = [
            {
                "index": c["index"],
                "text_preview": c["text"][:150],
                "char_count": c["char_count"],
            }
            for c in chunks[:CHUNK_PREVIEW_COUNT]
        ]

        return {
            "message": "File uploaded, embedded, and stored successfully",
            "filename": file.filename,
            "file_size_bytes": len(contents),
            "text_length": len(text),
            "chunk_count": len(chunks),
            "embedding_dimension": 384,
            "total_chunks_in_db": total_stored,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "chunk_previews": previews,
        }
    except HTTPException:
        raise
    except ValueError as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        file_path.unlink(missing_ok=True)
        logger.error(f"Upload failed for {file.filename}: {e}\n{tb}")
        detail = f"Failed to process file: {e}\n{tb}"
        raise HTTPException(status_code=500, detail=detail)
