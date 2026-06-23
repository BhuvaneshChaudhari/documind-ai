import re
import logging

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    if not text or not text.strip():
        return []

    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return []

    segments = _split_long_paragraphs(paragraphs, chunk_size)

    chunks: list[str] = []
    i = 0

    while i < len(segments):
        chunk_start = i
        chunk_parts: list[str] = []
        chunk_len = 0

        while i < len(segments):
            sep = "\n\n" if chunk_parts else ""
            seg = segments[i]
            new_len = chunk_len + len(sep) + len(seg)

            if new_len <= chunk_size:
                chunk_parts.append(seg)
                chunk_len = new_len
                i += 1
            else:
                break

        if chunk_parts:
            chunks.append("\n\n".join(chunk_parts))
        else:
            chunks.append(segments[i])
            i += 1

        if chunk_overlap > 0 and i > chunk_start:
            backtrack_len = 0
            backtrack_count = 0
            for j in range(i - 1, chunk_start - 1, -1):
                backtrack_len += len(segments[j]) + (
                    2 if backtrack_count > 0 else 0
                )
                if backtrack_len > chunk_overlap:
                    break
                backtrack_count += 1
            backtrack_count = min(backtrack_count, i - chunk_start - 1)
            i -= backtrack_count

    return [
        {"text": c, "index": idx, "char_count": len(c)}
        for idx, c in enumerate(chunks)
    ]


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def _split_long_paragraphs(
    paragraphs: list[str], chunk_size: int
) -> list[str]:
    segments: list[str] = []
    for p in paragraphs:
        if len(p) <= chunk_size:
            segments.append(p)
        else:
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(s) <= chunk_size:
                    segments.append(s)
                else:
                    words = s.split()
                    buf: list[str] = []
                    buf_len = 0
                    for w in words:
                        wlen = len(w) + (1 if buf else 0)
                        if buf_len + wlen <= chunk_size:
                            buf.append(w)
                            buf_len += wlen
                        else:
                            if buf:
                                segments.append(" ".join(buf))
                            buf = [w]
                            buf_len = len(w)
                    if buf:
                        segments.append(" ".join(buf))
    return segments
