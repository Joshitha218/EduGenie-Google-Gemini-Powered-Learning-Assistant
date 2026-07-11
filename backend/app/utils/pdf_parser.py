from pypdf import PdfReader
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from PDF bytes using pypdf.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        logger.info("PDF parser opened document. Page count=%s", len(reader.pages))
        text = ""
        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            logger.info("PDF page %s extracted text length=%s", index, len(page_text or ""))
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file: {str(e)}")
