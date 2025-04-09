from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import streamlit as st
import json

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

def generate_analytics_questions(text: str, provider: str = "openai") -> Dict[str, Any]:
    """
    Generate analytical questions from the given text.
    
    Args:
        text: The text to generate questions from
        provider: The LLM provider to use ("openai" or "groq")
        
    Returns:
        Dictionary containing the questions and evaluation criteria
    """
    try:
        # Create a prompt template for question generation
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert at creating analytical questions that test deep understanding.
            Create 3 analytical questions based on the given text. These should be open-ended questions that require
            critical thinking and analysis. Format the response as a JSON object with the following structure:
            {
                "questions": [
                    {
                        "question": "question text",
                        "evaluation_criteria": ["criterion1", "criterion2", "criterion3"]
                    },
                    ...
                ]
            }"""),
            HumanMessage(content=text)
        ])
        
        # Get the appropriate LLM
        llm = get_llm(provider)
        
        # Create the chain
        chain = prompt | llm
        
        # Generate the questions
        response = chain.invoke({})
        
        # Parse the JSON response
        questions_data = json.loads(response.content)
        
        return {
            "type": "analytics_questions",
            "content": questions_data,
            "metadata": {
                "model": "gpt-4" if provider == "openai" else "mixtral-8x7b-32768",
                "provider": provider,
                "timestamp": "current_time"
            }
        }
        
    except Exception as e:
        raise Exception(f"Error generating analytics questions: {str(e)}")

def evaluate_answer(question: str, answer: str, evaluation_criteria: List[str], provider: str = "openai") -> Dict[str, Any]:
    """
    Evaluate the user's answer to an analytical question.
    
    Args:
        question: The question text
        answer: The user's answer
        evaluation_criteria: List of criteria to evaluate against
        provider: The LLM provider to use ("openai" or "groq")
        
    Returns:
        Dictionary containing evaluation results and suggestions
    """
    try:
        # Create a prompt template for answer evaluation
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert at evaluating analytical answers.
            Evaluate the following answer based on these criteria: {', '.join(evaluation_criteria)}
            
            Provide:
            1. A score from 0-100
            2. Specific feedback on how well the answer addresses each criterion
            3. Suggestions for improvement
            4. A model answer that demonstrates the best way to address the question
            
            Format your response as a JSON object with the following structure:
            {{
                "score": score,
                "feedback": "detailed feedback",
                "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
                "model_answer": "example of a good answer"
            }}"""),
            HumanMessage(content=f"Question: {question}\n\nAnswer: {answer}")
        ])
        
        # Get the appropriate LLM
        llm = get_llm(provider)
        
        # Create the chain
        chain = prompt | llm
        
        # Generate the evaluation
        response = chain.invoke({})
        
        # Parse the JSON response
        evaluation = json.loads(response.content)
        
        return evaluation
        
    except Exception as e:
        raise Exception(f"Error evaluating answer: {str(e)}") 