import fitz  # PyMuPDF
import io
from typing import List, Union

def parse_page_numbers(page_numbers: str) -> List[int]:
    """
    Parse a string of page numbers into a list of integers.
    Supports ranges (e.g., '1-5') and individual numbers (e.g., '1,3,5').
    
    Args:
        page_numbers: String containing page numbers (e.g., '1-5' or '1,3,5')
        
    Returns:
        List of page numbers
    """
    pages = []
    for part in page_numbers.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return sorted(set(pages))  # Remove duplicates and sort

def extract_text_from_pages(pdf_content: bytes, page_numbers: str) -> str:
    """
    Extract text from specified pages of a PDF file.
    
    Args:
        pdf_content: The PDF file content as bytes
        page_numbers: String containing page numbers (e.g., '1-5' or '1,3,5')
        
    Returns:
        Extracted text from the specified pages
    """
    try:
        # Validate input
        if not pdf_content:
            raise ValueError("PDF content is empty")
        
        if not page_numbers:
            raise ValueError("No page numbers specified")
        
        # Parse page numbers
        pages_to_extract = parse_page_numbers(page_numbers)
        
        # Create a BytesIO object from the PDF content
        pdf_stream = io.BytesIO(pdf_content)
        
        # Open the PDF
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        
        # Validate page numbers
        if not pages_to_extract:
            raise ValueError("No valid page numbers found")
        
        if max(pages_to_extract) > len(doc):
            raise ValueError(f"Page number {max(pages_to_extract)} exceeds total pages ({len(doc)})")
        
        # Extract text from specified pages
        extracted_text = ""
        for page_num in pages_to_extract:
            page = doc[page_num - 1]  # Convert to 0-based index
            text = page.get_text()
            extracted_text += f"\n\n--- Page {page_num} ---\n{text}\n"
        
        # Close the document
        doc.close()
        
        return extracted_text.strip()
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}") 