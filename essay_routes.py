"""
Essay Routes Module for Chinese Self Learning System
This module contains all API routes for the AI essay feature.
It is designed to be included in the main FastAPI application.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import logging
from config import get_db_config, get_groq_api_key

from ai_essay import (
    generate_daily_essay,
    explain_word,
    chat_about_essay,
    get_sample_essay
)
from flashcard_app import get_current_level

logger = logging.getLogger(__name__)

# Router for essay endpoints
essay_router = APIRouter()

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models for request validation
class WordExplanationRequest(BaseModel):
    word: str
    context: Optional[str] = ""

class EssayChatRequest(BaseModel):
    essay_content: str
    question: str

class SetApiKeyRequest(BaseModel):
    api_key: str

# In-memory storage for essays (in production, use database or cache)
_generated_essays = {}

def get_db_connection():
    """Get database connection"""
    import mysql.connector
    try:
        conn = mysql.connector.connect(**get_db_config())
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise Exception(f"Database connection failed: {e}")

def get_user_session(request: Request):
    """Get user from session cookie"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT u.id, u.username, u.email 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            WHERE s.token = %s AND s.created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
        """, (session_token,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return user
        
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return None

# Routes

@essay_router.get("/api/essay/daily")
async def get_daily_essay(request: Request, use_sample: bool = False):
    """
    Get the daily AI-generated Chinese essay
    
    Args:
        use_sample: If True, use sample essay instead of generating new one
    
    Returns:
        JSON with essay data including Chinese text, pinyin, translation, and vocabulary
    """
    user = get_user_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Get user's current HSK level
        current_level = get_current_level(user['id'])
        
        # Check if we have a generated essay for today
        from datetime import date
        today = date.today().isoformat()
        cache_key = f"{user['id']}_{today}"
        
        if cache_key in _generated_essays and not use_sample:
            return {"essay": _generated_essays[cache_key], "cached": True}
        
        # Check if API key is configured
        if not get_groq_api_key() and not use_sample:
            # Return sample essay if no API key configured
            essay = get_sample_essay(current_level)
            essay['requires_api_key'] = True
            essay['message'] = "Please set your Groq API key in .env file to generate fresh essays."
            return {"essay": essay, "cached": False}
        
        if use_sample:
            essay = get_sample_essay(current_level)
            essay['is_sample'] = True
        else:
            # Generate new essay using AI
            essay = generate_daily_essay(current_level)
            
            if not essay:
                # Fallback to sample if generation fails
                essay = get_sample_essay(current_level)
                essay['generation_failed'] = True
                essay['message'] = "Failed to generate essay. Here's a sample instead."
        
        # Cache the essay
        _generated_essays[cache_key] = essay
        
        return {"essay": essay, "cached": False, "hsk_level": current_level}
        
    except Exception as e:
        logger.error(f"Error getting daily essay: {e}")
        # Return sample essay as fallback
        user_id = user['id'] if user else 1
        essay = get_sample_essay(1)
        essay['error'] = str(e)
        return {"essay": essay, "cached": False, "error": True}


@essay_router.post("/api/essay/word-explain")
async def explain_word_endpoint(request: Request, data: WordExplanationRequest):
    """
    Explain a Chinese word from the essay
    
    Args:
        word: The Chinese word to explain
        context: Optional context from the essay
    
    Returns:
        JSON with detailed word explanation
    """
    user = get_user_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Check if API key is configured
        if not get_groq_api_key():
            return JSONResponse(
                content={
                    "error": "API key required",
                    "message": "Please set your Groq API key in .env file to use this feature."
                },
                status_code=400
            )
        
        explanation = explain_word(data.word, data.context)
        
        if not explanation:
            return JSONResponse(
                content={"error": "Failed to explain word", "word": data.word},
                status_code=500
            )
        
        return {"explanation": explanation}
        
    except Exception as e:
        logger.error(f"Error explaining word: {e}")
        return JSONResponse(
            content={"error": str(e), "word": data.word},
            status_code=500
        )


@essay_router.post("/api/essay/chat")
async def chat_about_essay_endpoint(request: Request, data: EssayChatRequest):
    """
    Chat about the essay content - ask questions about meaning
    
    Args:
        essay_content: The Chinese essay content
        question: User's question about the essay
    
    Returns:
        JSON with AI response
    """
    user = get_user_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Check if API key is configured
        if not get_groq_api_key():
            return JSONResponse(
                content={
                    "error": "API key required",
                    "message": "Please set your Groq API key in .env file to use this feature."
                },
                status_code=400
            )
        
        response = chat_about_essay(data.essay_content, data.question)
        
        if not response:
            return JSONResponse(
                content={"error": "Failed to get response"},
                status_code=500
            )
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error in essay chat: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@essay_router.post("/api/essay/set-api-key")
async def set_api_key_endpoint(request: Request, data: SetApiKeyRequest):
    """
    Set the Groq API key for the session
    Note: API key should be set in ai_essay.py for production use
    """
    # For now, we'll just validate the key format
    if not data.api_key or len(data.api_key) < 10:
        return JSONResponse(
            content={"error": "Invalid API key format"},
            status_code=400
        )
    
    # Set the API key in the ai_essay module
    from ai_essay import set_api_key
    set_api_key(data.api_key)
    
    return {
        "message": "API key set successfully for this session",
        "hint": "For permanent setup, set your API key in ai_essay.py"
    }


@essay_router.get("/essay/modal")
async def essay_modal(request: Request):
    """
    Get the essay modal HTML component
    This is an alternative to embedding the modal directly in the dashboard
    """
    user = get_user_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        current_level = get_current_level(user['id'])
        
        return templates.TemplateResponse(
            request=request,
            name="essay_modal.html",
            context={
                "user": user,
                "current_level": current_level
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading essay modal: {e}")
        raise HTTPException(status_code=500, detail="Failed to load essay modal")