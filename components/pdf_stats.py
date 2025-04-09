import streamlit as st
import fitz  # PyMuPDF
import io
from typing import Dict, Any
import pandas as pd

def get_pdf_statistics(pdf_file: io.BytesIO) -> Dict[str, Any]:
    """
    Analyze a PDF file and return various statistics.
    
    Args:
        pdf_file: A BytesIO object containing the PDF file
        
    Returns:
        Dictionary containing PDF statistics
    """
    # Open the PDF document
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    # Initialize statistics
    stats = {
        "total_pages": len(doc),
        "page_dimensions": [],
        "total_images": 0,
        "total_text_blocks": 0,
        "total_lines": 0,
        "total_words": 0,
        "total_characters": 0,
        "metadata": doc.metadata
    }
    
    # Analyze each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get page dimensions
        stats["page_dimensions"].append({
            "page": page_num + 1,
            "width": page.rect.width,
            "height": page.rect.height
        })
        
        # Get images
        images = page.get_images()
        stats["total_images"] += len(images)
        
        # Get text blocks and analyze text
        blocks = page.get_text("dict")["blocks"]
        stats["total_text_blocks"] += len(blocks)
        
        for block in blocks:
            if "lines" in block:
                stats["total_lines"] += len(block["lines"])
                for line in block["lines"]:
                    if "spans" in line:
                        for span in line["spans"]:
                            stats["total_words"] += len(span["text"].split())
                            stats["total_characters"] += len(span["text"])
    
    doc.close()
    return stats

def display_pdf_statistics(pdf_file: io.BytesIO):
    """
    Display PDF statistics in a Streamlit interface.
    
    Args:
        pdf_file: A BytesIO object containing the PDF file
    """
    try:
        stats = get_pdf_statistics(pdf_file)
        
        # Display basic statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Pages", stats["total_pages"])
        with col2:
            st.metric("Total Images", stats["total_images"])
        with col3:
            st.metric("Total Text Blocks", stats["total_text_blocks"])
        
        # Display text statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Lines", stats["total_lines"])
        with col2:
            st.metric("Total Words", stats["total_words"])
        with col3:
            st.metric("Total Characters", stats["total_characters"])
        
        # Display metadata
        st.subheader("Document Metadata")
        metadata_df = pd.DataFrame([stats["metadata"]])
        st.dataframe(metadata_df)
        
    except Exception as e:
        st.error(f"Error analyzing PDF: {str(e)}") 