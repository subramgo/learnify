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

def generate_quiz(text: str, provider: str = "openai") -> Dict[str, Any]:
    """
    Generate a quiz with multiple choice questions from the given text.
    
    Args:
        text: The text to generate questions from
        provider: The LLM provider to use ("openai" or "groq")
        
    Returns:
        Dictionary containing the quiz questions and answers
    """
    try:
        # Create a prompt template for quiz generation
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert at creating educational quizzes. 
            Create 3 multiple choice questions based on the given text. 
            Each question should have 4 options (A, B, C, D) and only one correct answer.
            Format the response as a JSON object with the following structure:
            {
                "questions": [
                    {
                        "question": "question text",
                        "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
                        "correct_answer": "A"
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
        
        # Generate the quiz
        response = chain.invoke({})
        
        # Parse the JSON response
        quiz_data = json.loads(response.content)
        
        return {
            "type": "quiz",
            "content": quiz_data,
            "metadata": {
                "model": "gpt-4" if provider == "openai" else "mixtral-8x7b-32768",
                "provider": provider,
                "timestamp": "current_time"
            }
        }
        
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")

def evaluate_quiz(quiz_data: Dict, user_answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Evaluate the user's answers to the quiz.
    
    Args:
        quiz_data: The quiz data containing questions and correct answers
        user_answers: Dictionary of user's answers (question index -> answer)
        
    Returns:
        Dictionary containing evaluation results
    """
    total_questions = len(quiz_data["questions"])
    correct_answers = 0
    
    # Check each answer
    for i, question in enumerate(quiz_data["questions"]):
        if str(i) in user_answers and user_answers[str(i)] == question["correct_answer"]:
            correct_answers += 1
    
    percentage = (correct_answers / total_questions) * 100
    
    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "percentage": percentage,
        "user_answers": user_answers
    } 