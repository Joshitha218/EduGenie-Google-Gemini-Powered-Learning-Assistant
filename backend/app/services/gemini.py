import os
import json
import logging
import time
from typing import Dict, Any, List
import google.generativeai as genai
from backend.app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
def initialize_gemini():
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            logger.info("Gemini API successfully configured.")
            return True
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {str(e)}")
    else:
        logger.warning("GEMINI_API_KEY is not set. Using simulated fallbacks.")
    return False

# Initialize on import
API_CONFIGURED = initialize_gemini()

def _call_gemini_with_retry(prompt: str, model_name: str = "gemini-2.5-flash", json_mode: bool = True, retries: int = 3) -> str:
    """
    Helper function to invoke Gemini model with exponential backoff retry logic.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API Key is not configured.")
    
    for attempt in range(retries):
        try:
            model = genai.GenerativeModel(model_name)
            generation_config = {}
            if json_mode:
                generation_config = {"response_mime_type": "application/json"}
                
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            if response and response.text:
                return response.text
            else:
                raise ValueError("Received empty response from Gemini API.")
        except Exception as e:
            logger.error(f"Gemini API call attempt {attempt+1} failed: {str(e)}")
            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt)  # 1s, 2s, 4s backoff
    return ""

def _parse_json_safely(text: str) -> Dict[str, Any]:
    """
    Cleans and parses JSON from the response text.
    """
    text = text.strip()
    # Remove markdown code fences if present
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {text}. Error: {str(e)}")
        # Attempt minimal regex or manual cleanup if parsing failed
        raise ValueError("Response from AI was not valid JSON.")

# =====================================================================
# MODULE SERVICE IMPLEMENTATIONS
# =====================================================================

def ask_gemini_qa(question: str) -> Dict[str, Any]:
    """
    Q&A Module: Answers questions, returns related concepts and educational context.
    Uses gemini-1.5-pro (or gemini-1.5-flash as fallback).
    """
    if not settings.GEMINI_API_KEY:
        return get_simulated_qa(question)
        
    prompt = f"""
    You are an expert tutor. Answer the user's question in a comprehensive, educational, and easy-to-understand way.
    Provide the response strictly in JSON format with the following keys:
    - "Answer": A detailed, clear, and rich response answering the question, using markdown formatting inside the string where appropriate.
    - "RelatedConcepts": A list of 3-5 related academic concepts or topics that the student should study next.
    - "AdditionalContext": Any interesting historical context, real-world analogies, or extra facts related to the question.

    User Question: {question}
    """
    try:
        response_text = _call_gemini_with_retry(prompt, model_name="gemini-2.5-flash", json_mode=True)
        return _parse_json_safely(response_text)
    except Exception as e:
        logger.error(f"Q&A Gemini call failed: {str(e)}. Falling back to simulation.")
        return get_simulated_qa(question)

def generate_gemini_quiz(topic: str, difficulty: str, count: int) -> Dict[str, Any]:
    """
    Quiz Module: Generates multiple-choice quizzes (MCQs, Options, Correct Answer, Explanation).
    Uses gemini-1.5-pro.
    """
    if not settings.GEMINI_API_KEY:
        return get_simulated_quiz(topic, difficulty, count)
        
    prompt = f"""
    You are an educational assessment expert. Generate a multiple-choice quiz about the topic: "{topic}".
    Difficulty Level: {difficulty}
    Number of Questions: {count}

    Return the response strictly in JSON format with a single key "Quizzes", which is a list of quiz objects.
    Each quiz object MUST have the following keys:
    - "QuestionText": The quiz question.
    - "OptionA": First option.
    - "OptionB": Second option.
    - "OptionC": Third option.
    - "OptionD": Fourth option.
    - "CorrectOption": The letter of the correct option ('A', 'B', 'C', or 'D').
    - "Explanation": A detailed explanation of why the correct option is right and others are incorrect.

    Do not include any text outside the JSON structure.
    """
    try:
        response_text = _call_gemini_with_retry(prompt, model_name="gemini-2.5-flash", json_mode=True)
        return _parse_json_safely(response_text)
    except Exception as e:
        logger.error(f"Quiz Gemini call failed: {str(e)}. Falling back to simulation.")
        return get_simulated_quiz(topic, difficulty, count)

def summarize_gemini_content(text: str) -> Dict[str, Any]:
    """
    Summary Module: Summarizes study notes or PDF text.
    Uses gemini-1.5-pro.
    """
    if not settings.GEMINI_API_KEY:
        return get_simulated_summary(text)
        
    prompt = f"""
    You are an expert student assistant. Summarize the following educational material.
    Identify key takeaways, important formulas, terms, definitions, and construct exam-style study notes.

    Return the response strictly in JSON format with the following keys:
    - "Summary": A comprehensive, well-structured paragraph summarizing the entire text.
    - "ImportantPoints": A list of key points or bulleted takeaways.
    - "Formulas": A list of important equations, formulas, or rules mentioned (if none, return empty list).
    - "Definitions": A list of key terminology and definitions extracted from the text in the format "Term: Definition".
    - "ExamNotes": A list of exam tips, expected questions, or memory aids based on this text.

    Study Material Content:
    {text}
    """
    try:
        response_text = _call_gemini_with_retry(prompt, model_name="gemini-2.5-flash", json_mode=True)
        return _parse_json_safely(response_text)
    except Exception as e:
        logger.error(f"Summary Gemini call failed: {str(e)}. Falling back to simulation.")
        return get_simulated_summary(text)

def generate_gemini_learning_path(skill_name: str) -> Dict[str, Any]:
    """
    Learning Path Module: Generates roadmaps (Beginner, Intermediate, Advanced) and career recommendations.
    Uses gemini-1.5-pro.
    """
    if not settings.GEMINI_API_KEY:
        return get_simulated_learning_path(skill_name)
        
    prompt = f"""
    You are a career and academic advisor. Generate a personalized learning path/roadmap for learning: "{skill_name}".
    Provide three stages: Beginner, Intermediate, and Advanced.

    Return the response strictly in JSON format with the following keys:
    - "Topic": The name of the skill.
    - "Level": "All Stages"
    - "Beginner": An object containing:
        - "Topics": List of fundamental sub-topics to learn.
        - "Projects": List of beginner projects to build.
        - "Certifications": Recommended entry-level certifications or achievements.
        - "Resources": Useful free resources, websites, or books.
        - "Timeline": Estimated duration (e.g. "2-4 Weeks").
    - "Intermediate": An object containing:
        - "Topics": List of intermediate concepts.
        - "Projects": List of portfolio-worthy projects.
        - "Certifications": Industry recognized intermediate certifications.
        - "Resources": Advanced books, courses, or documentation.
        - "Timeline": Estimated duration (e.g. "4-6 Weeks").
    - "Advanced": An object containing:
        - "Topics": List of advanced, expert-level areas.
        - "Projects": Complex real-world systems to build.
        - "Certifications": Highly-regarded professional certifications.
        - "Resources": Masterclass resources, white papers, or advanced repos.
        - "Timeline": Estimated duration (e.g. "6-12 Weeks").
    - "CareerSuggestions": List of career paths, job roles, or industries where this skill is valuable.

    Make the timelines and details realistic, detailed, and highly motivational.
    """
    try:
        response_text = _call_gemini_with_retry(prompt, model_name="gemini-2.5-flash", json_mode=True)
        return _parse_json_safely(response_text)
    except Exception as e:
        logger.error(f"Learning Path Gemini call failed: {str(e)}. Falling back to simulation.")
        return get_simulated_learning_path(skill_name)


# =====================================================================
# SIMULATED RESPONSE FALLBACKS (For quick runs without API key)
# =====================================================================

def get_simulated_qa(question: str) -> Dict[str, Any]:
    return {
        "Answer": f"### Understanding '{question}'\n\nThis is a **simulated response** because no Google Gemini API Key is configured or the request timed out.\n\nTo answer your query: studying this concept requires understanding its foundational principles. It involves analyzing its primary inputs, processes, and outputs. In educational theory, mastering this is key to building advanced application skills.",
        "RelatedConcepts": [
            f"Foundations of {question}",
            "Practical applications in modern industries",
            "Advanced research and future trends"
        ],
        "AdditionalContext": "Note: To experience full AI generation, please obtain a Gemini API key from Google AI Studio and configure the GEMINI_API_KEY environment variable in your `.env` file."
    }

def get_simulated_quiz(topic: str, difficulty: str, count: int) -> Dict[str, Any]:
    quizzes = []
    for i in range(1, count + 1):
        quizzes.append({
            "QuestionText": f"Simulated Question {i}: Which of the following is true about '{topic}' at a {difficulty} level?",
            "OptionA": f"It is a core concept that defines basic functionality.",
            "OptionB": f"It is only applicable in specialized scientific fields.",
            "OptionC": f"It has no practical relevance in modern engineering.",
            "OptionD": f"It was completely replaced by AI algorithms in 2024.",
            "CorrectOption": "A",
            "Explanation": f"Option A is correct because '{topic}' forms the foundational block. The other options are either too restrictive or factually incorrect."
        })
    return {"Quizzes": quizzes}

def get_simulated_summary(text: str) -> Dict[str, Any]:
    preview = text[:60] + "..." if len(text) > 60 else text
    return {
        "Summary": f"This is a simulated summary of the content: '{preview}'. The study notes suggest that the content deals with important academic topics. Understanding these concepts requires close reading and note-taking.",
        "ImportantPoints": [
            "This summary is simulated due to the absence of a Gemini API key.",
            "The input content has been processed locally.",
            "Study materials are best broken down into key definitions and formulas."
        ],
        "Formulas": [
            "Learning = (Focus * Time)^Retention",
            "Recall_Rate = 1 / log(Time_Passed)"
        ],
        "Definitions": [
            "Retention: The ability to recall concepts over long periods.",
            "Active Recall: Testing yourself on concepts rather than passively reading them."
        ],
        "ExamNotes": "Review these points daily. Focus on the definitions and apply the retention formulas to schedule your review sessions."
    }

def get_simulated_learning_path(skill_name: str) -> Dict[str, Any]:
    return {
        "Topic": skill_name,
        "Level": "All Stages (Simulated)",
        "Beginner": {
            "Topics": [f"Introduction to {skill_name}", "Basic syntax and tools", "Understanding variables and structures"],
            "Projects": ["Simple Console Calculator", "Personal Todo List application"],
            "Certifications": [f"Basic {skill_name} Certificate (FreeCodeCamp/Coursera)"],
            "Resources": ["Official Documentation", "W3Schools beginner tutorials"],
            "Timeline": "2 Weeks"
        },
        "Intermediate": {
            "Topics": ["Object-Oriented programming in context", "Working with databases", "API design and consumption"],
            "Projects": ["E-commerce API backend", "Data scraper and visualizer dashboard"],
            "Certifications": [f"Certified Associate in {skill_name}"],
            "Resources": ["Medium Articles", "Developer roadmaps on roadmap.sh"],
            "Timeline": "4 Weeks"
        },
        "Advanced": {
            "Topics": ["Advanced design patterns", "Performance optimization and caching", "Asynchronous architectures"],
            "Projects": ["Real-time collaborative chat server", "Distributed microservices gateway"],
            "Certifications": [f"Professional {skill_name} Solution Architect"],
            "Resources": ["Advanced reference manuals", "GitHub open source repositories"],
            "Timeline": "6 Weeks"
        },
        "CareerSuggestions": ["Full-Stack Engineer", "Software Developer", "Technical Trainer"]
    }
