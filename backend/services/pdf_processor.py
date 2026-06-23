import logging
import warnings
import io
import contextlib

from pypdf import PdfReader

logger = logging.getLogger(__name__)

# Completely suppress pypdf's noisy warnings (images, embedded files, etc.)
logging.getLogger("pypdf").setLevel(logging.CRITICAL)

MAX_PAGES = 200


def extract_text_from_pdf(file_path: str) -> str:
    logger.info(f"Extracting text from: {file_path}")

    stderr_capture = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr_capture):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                reader = PdfReader(file_path)
    except Exception as e:
        raise ValueError(f"Cannot read PDF file: {e}")

    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported")

    if len(reader.pages) > MAX_PAGES:
        raise ValueError(
            f"PDF has {len(reader.pages)} pages, which exceeds the "
            f"maximum of {MAX_PAGES} pages."
        )

    pages: list[str] = []
    with contextlib.redirect_stderr(stderr_capture):
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append(text)
            logger.debug(f"Page {i + 1}: {len(text or '')} chars extracted")

            if i >= 2 and not pages:
                raise ValueError(
                    "No extractable text found in this PDF. "
                    "It may be a scanned/image-based document. "
                    "Please upload a PDF with selectable text."
                )

    full_text = "\n".join(pages).strip()
    if not full_text:
        raise ValueError(
            "No extractable text found in this PDF. "
            "It may be a scanned/image-based document. "
            "Please upload a PDF with selectable text."
        )

    logger.info(
        f"Successfully extracted {len(full_text)} chars from {len(reader.pages)} pages"
    )
    return full_text
