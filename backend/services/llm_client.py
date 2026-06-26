import logging
import re
import time

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, LLM_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise document Q&A assistant. Answer the user's question based solely on the provided context. Be concise and use plain text — no markdown. If the context has the information, answer directly. Only say you cannot find the information if the context genuinely does not contain the answer."""


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

    user_message = f"""Context:
{retrieved_context}

Question:
{question}

Answer:"""

    logger.info(f"Sending prompt to Groq ({GROQ_MODEL}) ({len(user_message)} chars)")

    start = time.monotonic()
    try:
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            max_tokens=768,
        )
    except Exception as e:
        raise RuntimeError(f"Groq API request failed: {e}")

    elapsed = time.monotonic() - start
    answer = _strip_markdown((resp.choices[0].message.content or "").strip())
    logger.info(f"Groq response in {elapsed:.2f}s | answer={len(answer)} chars | model={GROQ_MODEL}")

    if not answer:
        logger.warning("Groq returned empty response")

    return {
        "answer": answer,
        "llm_time_seconds": round(elapsed, 2),
    }
