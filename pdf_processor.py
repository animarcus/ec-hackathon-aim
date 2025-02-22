import PyPDF2
import logging
from docx import Document
import os

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    logger.debug(f"Attempting to extract text from PDF: {file_path}")
    try:
        text = ""
        with open(file_path, 'rb') as file:
            logger.debug("File opened successfully")
            pdf_reader = PyPDF2.PdfReader(file)
            logger.debug(f"PDF has {len(pdf_reader.pages)} pages")
            for page in pdf_reader.pages:
                text += page.extract_text()
        logger.debug(f"Successfully extracted {len(text)} characters of text")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        logger.exception("Full traceback:")
        raise