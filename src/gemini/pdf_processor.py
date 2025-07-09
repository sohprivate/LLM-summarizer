"""PDF processing and text extraction module."""
import PyPDF2
from typing import Optional
from loguru import logger


def extract_text_from_pdf(pdf_path: str, max_pages: int = 10) -> Optional[str]:
    """Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to extract (to avoid token limits)
    
    Returns:
        Extracted text or None if error
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get total pages
            num_pages = len(pdf_reader.pages)
            pages_to_read = min(num_pages, max_pages)
            
            logger.info(f"PDF has {num_pages} pages, reading first {pages_to_read} pages")
            
            # Extract text from pages
            text_parts = []
            for page_num in range(pages_to_read):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
            
            full_text = "\n\n".join(text_parts)
            
            # Basic validation
            if len(full_text) < 100:
                logger.warning(f"Extracted text is too short ({len(full_text)} chars)")
                return None
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        return None


def get_first_page_text(pdf_path: str) -> Optional[str]:
    """Extract text from the first page only (useful for title/abstract)."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                return None
            
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            return text.strip() if text else None
    
    except Exception as e:
        logger.error(f"Error extracting first page from PDF {pdf_path}: {e}")
        return None