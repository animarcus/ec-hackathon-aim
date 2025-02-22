import logging
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        logger.debug(f"Attempting to extract text from PDF: {file_path}")

        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()

        if not text:
            logger.warning("No text extracted from PDF")
            return ""

        logger.debug(f"Successfully extracted {len(text)} characters of text")
        return text.strip()

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise