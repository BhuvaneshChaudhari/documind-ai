import logging
import re
import time

import httpx

from config import OLLAMA_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """Use the context to answer the question. Plain text only. Be concise.

Context:
{retrieved_context}

Question:
{user_question}

Answer:"""


def _strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"^\s*[\*\-\+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def generate_answer(question: str, context_chunks: list[dict]) -> dict:
    context_parts = []
    for i, c in enumerate(context_chunks, 1):
        context_parts.append(f"[Source {i}] {c['text'].strip()}")
    retrieved_context = "\n\n".join(context_parts)

    prompt = PROMPT_TEMPLATE.format(
        retrieved_context=retrieved_context,
        user_question=question,
    )

    logger.info(f"Sending prompt to {LLM_MODEL} ({len(prompt)} chars)")

    start = time.monotonic()
    try:
        with httpx.Client(timeout=300) as client:
            resp = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 768,
"num_ctx": 4096,
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            f"Ensure Ollama is running and '{LLM_MODEL}' is pulled."
        )
    except httpx.TimeoutException:
        raise RuntimeError(
            f"Ollama timed out after 300s. The LLM took too long to respond. "
            f"Try a shorter question or use a smaller document."
        )
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Ollama error: {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")

    elapsed = time.monotonic() - start
    answer = _strip_markdown(data.get("response", "").strip())
    thinking = (data.get("thinking") or "")[:200]
    logger.info(
        f"LLM response in {elapsed:.2f}s | answer={len(answer)} chars "
        f"| done_reason={data.get('done_reason')} | thinking={thinking}"
    )

    if not answer:
        logger.warning(f"Ollama returned empty response. Full data: {data}")

    return {
        "answer": answer,
        "llm_time_seconds": round(elapsed, 2),
    }
