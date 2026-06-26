import logging

import httpx

logger = logging.getLogger(__name__)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    from config import EMBEDDING_MODEL, HF_API_TOKEN

    if not HF_API_TOKEN:
        raise RuntimeError(
            "HF_API_TOKEN is not set. Get a free token at hf.co/settings/tokens"
        )

    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json={"inputs": texts})
        resp.raise_for_status()
        embeddings = resp.json()

    if isinstance(embeddings, list) and len(embeddings) == len(texts):
        return embeddings

    raise RuntimeError(f"Unexpected embedding response: {type(embeddings)}")
