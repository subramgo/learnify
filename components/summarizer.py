from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.tools import tool
import streamlit as st

def get_llm(provider: str = "openai") -> Any:
    """
    Get the appropriate LLM based on the provider.
    
    Args:
        provider: Either "openai" or "groq"
        
    Returns:
        The configured LLM instance
    """
    try:
        if provider == "openai":
            api_key = st.secrets["openai"]["api_key"]
            return ChatOpenAI(temperature=0, api_key=api_key)
        elif provider == "groq":
            api_key = st.secrets["groq"]["api_key"]
            return ChatGroq(temperature=0, api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except KeyError:
        raise Exception(f"API key not found in secrets.toml for provider: {provider}")

def generate_summary(text: str, provider: str = "openai") -> Dict[str, Any]:
    """
    Generate a summary of the given text using the specified provider.
    
    Args:
        text: The text to summarize
        provider: The LLM provider to use ("openai" or "groq")
        
    Returns:
        Dictionary containing the summary and metadata
    """
    try:
        # Create a prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="You are an expert at summarizing educational content. Create a concise yet comprehensive summary of the given text."),
            HumanMessage(content=text)
        ])
        
        # Get the appropriate LLM
        llm = get_llm(provider)
        
        # Create the chain
        chain = prompt | llm
        
        # Generate the summary
        response = chain.invoke({})
        
        return {
            "type": "summary",
            "content": response.content,
            "metadata": {
                "model": "gpt-4" if provider == "openai" else "mixtral-8x7b-32768",
                "provider": provider,
                "timestamp": "current_time"  # You can add actual timestamp here
            }
        }
        
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}") 