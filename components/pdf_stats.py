import streamlit as st
import fitz  # PyMuPDF
import io
from typing import Dict, Any
import pandas as pd

def get_pdf_statistics(pdf_content: bytes) -> Dict[str, Any]:
    """
    Analyze a PDF file and return statistics about its content.
    
    Args:
        pdf_content: The PDF file content as bytes
        
    Returns:
        Dictionary containing PDF statistics
    """
    try:
        # Open the PDF from bytes
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        # Initialize counters
        total_images = 0
        total_text_blocks = 0
        total_lines = 0
        total_words = 0
        total_characters = 0
        
        # Process each page
        for page in doc:
            # Count images
            total_images += len(page.get_images())
            
            # Get text blocks
            blocks = page.get_text("dict")["blocks"]
            total_text_blocks += len(blocks)
            
            # Process each block
            for block in blocks:
                if "lines" in block:
                    total_lines += len(block["lines"])
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                text = span["text"]
                                total_words += len(text.split())
                                total_characters += len(text)
        
        # Get metadata
        metadata = doc.metadata
        
        # Close the document
        doc.close()
        
        return {
            "total_pages": len(doc),
            "total_images": total_images,
            "total_text_blocks": total_text_blocks,
            "total_lines": total_lines,
            "total_words": total_words,
            "total_characters": total_characters,
            "metadata": metadata
        }
        
    except Exception as e:
        raise Exception(f"Error analyzing PDF: {str(e)}")

def display_pdf_statistics(pdf_file: io.BytesIO):
    """
    Display PDF statistics in a Streamlit interface.
    
    Args:
        pdf_file: A BytesIO object containing the PDF file
    """
    try:
        stats = get_pdf_statistics(pdf_file.read())
        
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