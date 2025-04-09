from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import streamlit as st

def summarize_text(text: str) -> str:
    """
    Generate a summary of the input text using OpenAI.
    
    Args:
        text: The text to summarize
        
    Returns:
        Generated summary
    """
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert at summarizing educational content. Create a concise and informative summary of the provided text."),
        HumanMessage(content=text)
    ])
    
    # Initialize OpenAI LLM
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0,
        api_key=st.secrets["openai"]["api_key"]
    )
    
    # Create the chain
    chain = prompt | llm
    
    # Generate the summary
    response = chain.invoke({})
    return response.content

def generate_summary(text: str) -> Dict[str, Any]:
    """
    Generate a summary of the input text.
    
    Args:
        text: The text to summarize
        
    Returns:
        Dictionary containing the summary and metadata
    """
    try:
        # Generate the summary
        summary = summarize_text(text)
        
        # Return the result with metadata
        return {
            "content": summary,
            "metadata": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview"
            }
        }
        
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}") 