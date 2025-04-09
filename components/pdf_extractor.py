import fitz  # PyMuPDF
import io
from typing import List, Union

def parse_page_numbers(page_input: str) -> List[int]:
    """
    Parse page number input string into a list of page numbers.
    Supports ranges (e.g., '1-5') and individual numbers (e.g., '1,3,5').
    
    Args:
        page_input: String containing page numbers (e.g., '1-5' or '1,3,5' or '1-3,5-7')
        
    Returns:
        List of page numbers (0-indexed)
    """
    pages = []
    # Split by comma to handle multiple ranges/numbers
    parts = page_input.split(',')
    
    for part in parts:
        if '-' in part:
            # Handle range
            start, end = map(int, part.split('-'))
            pages.extend(range(start - 1, end))  # Convert to 0-indexed
        else:
            # Handle single number
            pages.append(int(part) - 1)  # Convert to 0-indexed
    
    return sorted(list(set(pages)))  # Remove duplicates and sort

def extract_text_from_pages(pdf_file: io.BytesIO, page_numbers: str) -> str:
    """
    Extract text from specified pages of a PDF file.
    
    Args:
        pdf_file: BytesIO object containing the PDF
        page_numbers: String specifying pages to extract (e.g., '1-5' or '1,3,5')
        
    Returns:
        Extracted text from specified pages
    """
    try:
        # Open the PDF document
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Parse page numbers
        pages_to_extract = parse_page_numbers(page_numbers)
        
        # Validate page numbers
        if not pages_to_extract:
            raise ValueError("No valid page numbers provided")
        if max(pages_to_extract) >= len(doc):
            raise ValueError(f"Page number {max(pages_to_extract) + 1} exceeds PDF length ({len(doc)})")
        
        # Extract text from specified pages
        extracted_text = ""
        for page_num in pages_to_extract:
            page = doc[page_num]
            text = page.get_text()
            extracted_text += f"\n\n--- Page {page_num + 1} ---\n\n{text}"
        
        doc.close()
        return extracted_text.strip()
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}") 