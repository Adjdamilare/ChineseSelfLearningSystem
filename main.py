from fastapi import FastAPI, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel  # Add this
from typing import Optional     # Add this
import mysql.connector
import bcrypt
import secrets
import logging
from flashcard_app import (
    get_user_mastery_stats,
    get_next_word_to_study,
    get_study_session,
    update_word_mastery,
    get_progress_by_level,
    get_current_level
)
from essay_routes import essay_router
from stroke_order_routes import stroke_order_router
from datetime import datetime, timedelta
from config import get_db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add lifespan event for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    create_tables()
    yield
    # Shutdown: Cleanup if needed

app = FastAPI(title="Chinese Self Learning System", lifespan=lifespan)

# Include essay routes
app.include_router(essay_router)

# Include stroke order routes
app.include_router(stroke_order_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Configure template environment
templates.env.auto_reload = True
templates.env.globals['enumerate'] = enumerate

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**get_db_config())
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# main.py

def create_tables():
    """Create necessary tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Only create tables if they don't exist (don't drop existing data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INT AUTO_INCREMENT PRIMARY KEY,
                level INT NOT NULL,
                hanzi VARCHAR(50) NOT NULL,
                pinyin VARCHAR(100) NOT NULL,
                pinyin_tone VARCHAR(100),
                pinyin_num VARCHAR(100),
                english TEXT NOT NULL,
                pos VARCHAR(50),
                tts_url VARCHAR(500)
            )
        """)
        
        # Flashcard tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_word_mastery (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                word_id INT NOT NULL,
                difficulty ENUM('new', 'easy', 'fair', 'hard') DEFAULT 'new',
                times_studied INT DEFAULT 0,
                times_correct INT DEFAULT 0,
                times_incorrect INT DEFAULT 0,
                current_streak INT DEFAULT 0,
                best_streak INT DEFAULT 0,
                next_review DATETIME DEFAULT NOW(),
                interval_hours INT DEFAULT 0,
                mastered BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_word (user_id, word_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                started_at DATETIME DEFAULT NOW(),
                completed_at DATETIME NULL,
                total_cards INT DEFAULT 0,
                correct_count INT DEFAULT 0,
                incorrect_count INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_study (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                word_id INT NOT NULL,
                user_answer TEXT,
                is_correct BOOLEAN,
                difficulty ENUM('new', 'easy', 'fair', 'hard') DEFAULT 'new',
                next_review DATETIME DEFAULT NOW(),
                interval_hours INT DEFAULT 0,
                studied_at DATETIME DEFAULT NOW(),
                FOREIGN KEY (session_id) REFERENCES flashcard_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class WordSearch(BaseModel):
    query: str
    level: Optional[int] = None

# Routes

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page with signup/login options"""
    return templates.TemplateResponse(request=request, name="landing.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse(request=request, name="register.html")

# In main.py, update the register and login functions

@app.post("/register")
async def register(request: Request, username: str = Form(...), email: str = Form(...), 
                   password: str = Form(...), confirm_password: str = Form(...)):
    """Register a new user"""
    try:
        # Validate password confirmation
        if password != confirm_password:
            return templates.TemplateResponse(request=request, name="register.html", 
                                            context={"error": "Passwords do not match"})
        
        # Validate password length
        if len(password) < 6:
            return templates.TemplateResponse(request=request, name="register.html",
                                            context={"error": "Password must be at least 6 characters"})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            return templates.TemplateResponse(request=request, name="register.html",
                                            context={"error": "Email already registered"})
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        # Create session token
        session_token = secrets.token_hex(32)
        
        # Store session
        cursor.execute(
            "INSERT INTO sessions (user_id, token, created_at) VALUES (%s, %s, NOW())",
            (user_id, session_token)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Set first_time cookie for new users
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=86400)
        response.set_cookie(key="is_first_time", value="true", max_age=86400)  # New user is always first time
        return response
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return templates.TemplateResponse(request=request, name="register.html",
                                        context={"error": "Registration failed"})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user
        cursor.execute("SELECT id, username, hashed_password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return templates.TemplateResponse(request=request, name="login.html",
                                            context={"error": "Invalid credentials"})
        
        # Verify password - handle both string and bytes
        stored_password = user[2]
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
            cursor.close()
            conn.close()
            return templates.TemplateResponse(request=request, name="login.html",
                                            context={"error": "Invalid credentials"})
        
        # Check if first time login by checking previous sessions
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_id = %s", (user[0],))
        previous_sessions = cursor.fetchone()[0]
        is_first_time = previous_sessions == 0
        
        # Create session token
        session_token = secrets.token_hex(32)
        
        # Store session
        cursor.execute(
            "INSERT INTO sessions (user_id, token, created_at) VALUES (%s, %s, NOW())",
            (user[0], session_token)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=86400)
        response.set_cookie(key="is_first_time", value="true" if is_first_time else "false", max_age=86400)
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse(request=request, name="login.html",
                                        context={"error": "Login failed"})
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse(request=request, name="login.html")



def get_current_user(request: Request):
    """Get current user from session"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            WHERE s.token = %s AND s.created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
        """, (session_token,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        return {"id": user[0], "username": user[1], "email": user[2]}
        
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        raise HTTPException(status_code=401, detail="Session validation failed")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """User dashboard"""
    try:
        user = get_current_user(request)
        is_first_time = request.cookies.get("is_first_time", "false") == "true"
        
        return templates.TemplateResponse(request=request, name="dashboard.html",
                                        context={"user": user, "is_first_time": is_first_time})
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Search words page"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse(request=request, name="search.html",
                                        context={"user": user})
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Search page error: {e}")
        return RedirectResponse(url="/login", status_code=302)

def searchword(query: str, level: Optional[int] = None, limit: int = 50):
    """
    Search for Chinese words in the database.
    
    Args:
        query: Search term (can be Chinese character, pinyin, or English)
        level: Optional HSK level filter (1-6)
        limit: Maximum number of results to return (default: 50)
    
    Returns:
        List of tuples containing word data:
        (id, level, hanzi, pinyin, pinyin_tone, pinyin_num, english, pos, tts_url)
    """
    if not query or len(query.strip()) < 1:
        return []
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query - search in hanzi, pinyin, pinyin_num, and english
        sql = """
            SELECT id, level, hanzi, pinyin, pinyin_tone, pinyin_num, english, pos, tts_url
            FROM words 
            WHERE (hanzi LIKE %s OR pinyin LIKE %s OR pinyin_tone LIKE %s OR pinyin_num LIKE %s OR english LIKE %s)
        """
        search_term = f"%{query}%"
        params = [search_term, search_term, search_term, search_term, search_term]
        
        if level is not None:
            sql += " AND level = %s"
            params.append(level)
        
        sql += " ORDER BY level ASC, hanzi ASC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, params)
        words = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return words
        
    except Exception as e:
        logger.error(f"Searchword error: {e}")
        if conn:
            try:
                cursor.close()
                conn.close()
            except:
                pass
        return []


@app.post("/search", response_class=HTMLResponse)
async def search_words(request: Request, query: str = Form(...), level: Optional[int] = Form(None)):
    """Search for words"""
    try:
        user = get_current_user(request)
        
        # Validate search query
        if not query or len(query.strip()) < 1:  # Allow single character search
            return templates.TemplateResponse(request=request, name="search.html",
                                            context={"user": user, "error": "Please enter a search term"})
        
        # Use the searchword function
        words = searchword(query, level)
        
        return templates.TemplateResponse(request=request, name="search_results.html",
                                        context={"user": user, "words": words, "query": query, "level": level})
        
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Search error: {e}")
        return templates.TemplateResponse(request=request, name="search.html",
                                        context={"user": user, "error": "Search failed"})


@app.get("/api/search", response_class=JSONResponse)
async def api_search_words(request: Request, query: str, level: Optional[int] = None):
    """API endpoint for searching words - returns JSON"""
    try:
        # Validate search query
        if not query or len(query.strip()) < 1:
            return JSONResponse(content={"error": "Please enter a search term", "words": []}, status_code=400)
        
        # Use the searchword function
        words = searchword(query, level)
        
        # Convert tuples to list of dictionaries for JSON response
        words_list = []
        for word in words:
            words_list.append({
                "id": word[0],
                "level": word[1],
                "hanzi": word[2],
                "pinyin": word[3],
                "pinyin_tone": word[4],
                "pinyin_num": word[5],
                "english": word[6],
                "pos": word[7],
                "tts_url": word[8]
            })
        
        return {"query": query, "count": len(words_list), "words": words_list}
        
    except Exception as e:
        logger.error(f"API Search error: {e}")
        return JSONResponse(content={"error": "Search failed", "words": []}, status_code=500)
# Legacy Flashcard Routes (kept for backward compatibility)

@app.get("/flashcards-old", response_class=HTMLResponse)
async def flashcards_page(request: Request):
    """Flashcard study page (legacy)"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse(request=request, name="flashcards.html",
                                        context={"user": user})
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Flashcards page error: {e}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/api/flashcards")
async def get_flashcards(request: Request, level: Optional[int] = None, difficulty: Optional[str] = None):
    """Get flashcards for review, optionally filtered by HSK level and difficulty"""
    try:
        user = get_current_user(request)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build query to get flashcards with word information
        sql = """
            SELECT 
                f.id as flashcard_id,
                f.difficulty,
                f.next_review,
                f.interval_days,
                w.id as word_id,
                w.level,
                w.hanzi,
                w.pinyin,
                w.pinyin_tone,
                w.pinyin_num,
                w.english,
                w.pos,
                w.tts_url
            FROM flashcards f
            JOIN words w ON f.word_id = w.id
            WHERE f.user_id = %s
        """
        params = [user['id']]
        
        if level:
            sql += " AND w.level = %s"
            params.append(level)
        
        if difficulty and difficulty != 'all':
            sql += " AND f.difficulty = %s"
            params.append(difficulty)
        
        sql += " ORDER BY f.next_review ASC, w.level ASC LIMIT 50"
        
        cursor.execute(sql, params)
        flashcards = cursor.fetchall()
        
        # Get summary stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN difficulty = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN difficulty = 'easy' THEN 1 ELSE 0 END) as easy_count,
                SUM(CASE WHEN difficulty = 'fair' THEN 1 ELSE 0 END) as fair_count,
                SUM(CASE WHEN difficulty = 'hard' THEN 1 ELSE 0 END) as hard_count
            FROM flashcards
            WHERE user_id = %s
        """, (user['id'],))
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "flashcards": flashcards,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get flashcards error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get flashcards")

@app.get("/api/flashcards/progress")
async def get_flashcard_progress(request: Request):
    """Get flashcard progress grouped by HSK level"""
    try:
        user = get_current_user(request)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get progress by HSK level
        sql = """
            SELECT 
                w.level,
                COUNT(*) as total_cards,
                SUM(CASE WHEN f.difficulty = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN f.difficulty = 'easy' THEN 1 ELSE 0 END) as easy_count,
                SUM(CASE WHEN f.difficulty = 'fair' THEN 1 ELSE 0 END) as fair_count,
                SUM(CASE WHEN f.difficulty = 'hard' THEN 1 ELSE 0 END) as hard_count,
                COUNT(fp.id) as total_reviews
            FROM flashcards f
            JOIN words w ON f.word_id = w.id
            LEFT JOIN flashcard_progress fp ON f.id = fp.flashcard_id
            WHERE f.user_id = %s
            GROUP BY w.level
            ORDER BY w.level ASC
        """
        
        cursor.execute(sql, (user['id'],))
        progress = cursor.fetchall()
        
        # Get total words available per level
        cursor.execute("""
            SELECT level, COUNT(*) as available_words
            FROM words
            GROUP BY level
            ORDER BY level ASC
        """)
        available = cursor.fetchall()
        
        # Create a map of available words
        available_map = {row['level']: row['available_words'] for row in available}
        
        cursor.close()
        conn.close()
        
        return {"progress": progress, "available_words": available_map}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get flashcard progress error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress")

@app.post("/api/flashcards/add")
async def add_flashcard(request: Request, word_id: int = Form(...)):
    """Add a word to flashcards"""
    try:
        user = get_current_user(request)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if flashcard already exists
        cursor.execute("""
            SELECT id FROM flashcards 
            WHERE user_id = %s AND word_id = %s
        """, (user['id'], word_id))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.close()
            conn.close()
            return {"message": "Flashcard already exists", "flashcard_id": existing[0]}
        
        # Insert new flashcard
        cursor.execute("""
            INSERT INTO flashcards (user_id, word_id, difficulty, next_review)
            VALUES (%s, %s, 'new', NOW())
        """, (user['id'], word_id))
        
        conn.commit()
        flashcard_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {"message": "Flashcard created", "flashcard_id": flashcard_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add flashcard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add flashcard")

@app.post("/api/flashcards/review")
async def review_flashcard(request: Request, flashcard_id: int = Form(...), difficulty: str = Form(...)):
    """Review a flashcard and update its difficulty"""
    try:
        user = get_current_user(request)
        
        if difficulty not in ['easy', 'fair', 'hard']:
            raise HTTPException(status_code=400, detail="Invalid difficulty")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify flashcard belongs to user
        cursor.execute("""
            SELECT id FROM flashcards 
            WHERE id = %s AND user_id = %s
        """, (flashcard_id, user['id']))
        
        flashcard = cursor.fetchone()
        
        if not flashcard:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        # Calculate next review interval based on difficulty
        interval_map = {
            'easy': 7,    # 7 days
            'fair': 3,    # 3 days
            'hard': 1     # 1 day
        }
        
        interval = interval_map[difficulty]
        
        # Update flashcard
        cursor.execute("""
            UPDATE flashcards 
            SET difficulty = %s, 
                interval_days = %s,
                next_review = DATE_ADD(NOW(), INTERVAL %s DAY)
            WHERE id = %s
        """, (difficulty, interval, interval, flashcard_id))
        
        # Record progress
        cursor.execute("""
            INSERT INTO flashcard_progress (flashcard_id, difficulty)
            VALUES (%s, %s)
        """, (flashcard_id, difficulty))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Flashcard reviewed", "next_review_days": interval}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Review flashcard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to review flashcard")

@app.delete("/api/flashcards/{flashcard_id}")
async def delete_flashcard(request: Request, flashcard_id: int):
    """Delete a flashcard"""
    try:
        user = get_current_user(request)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify flashcard belongs to user
        cursor.execute("""
            SELECT id FROM flashcards 
            WHERE id = %s AND user_id = %s
        """, (flashcard_id, user['id']))
        
        flashcard = cursor.fetchone()
        
        if not flashcard:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        # Delete flashcard
        cursor.execute("DELETE FROM flashcards WHERE id = %s", (flashcard_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Flashcard deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete flashcard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete flashcard")

@app.get("/api/flashcards/next")
async def get_next_flashcard(request: Request):
    """Get the next flashcard due for review"""
    try:
        user = get_current_user(request)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get next flashcard due for review
        sql = """
            SELECT 
                f.id as flashcard_id,
                f.difficulty,
                f.next_review,
                w.id as word_id,
                w.level,
                w.hanzi,
                w.pinyin,
                w.pinyin_tone,
                w.pinyin_num,
                w.english,
                w.pos,
                w.tts_url
            FROM flashcards f
            JOIN words w ON f.word_id = w.id
            WHERE f.user_id = %s AND f.next_review <= NOW()
            ORDER BY f.next_review ASC, w.level ASC
            LIMIT 1
        """
        
        cursor.execute(sql, (user['id'],))
        flashcard = cursor.fetchone()
        
        # Get count of remaining cards due
        cursor.execute("""
            SELECT COUNT(*) as remaining
            FROM flashcards
            WHERE user_id = %s AND next_review <= NOW()
        """, (user['id'],))
        remaining = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {"flashcard": flashcard, "remaining": remaining['remaining'] if remaining else 0}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get next flashcard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get next flashcard")

# New Flashcard Study Routes

@app.get("/study-flashcards", response_class=HTMLResponse)
async def study_flashcards_page(request: Request):
    """Main flashcard study page - interactive testing"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse(request=request, name="study_flashcards.html",
                                        context={"user": user})
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Study flashcards page error: {e}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/flashcards", response_class=HTMLResponse)
async def flashcard_progress_page(request: Request):
    """Flashcard progress overview page"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse(request=request, name="flashcard_progress.html",
                                        context={"user": user})
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Flashcard progress page error: {e}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/flashcard-study", response_class=HTMLResponse)
async def flashcard_study_page(request: Request):
    """Interactive flashcard study page"""
    try:
        user = get_current_user(request)
        return templates.TemplateResponse(request=request, name="flashcards.html",
                                        context={"user": user})
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Flashcard study page error: {e}")
        return RedirectResponse(url="/login", status_code=302)

def get_user_profile_stats(user_id: int):
    """Get comprehensive user statistics for profile page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get mastery stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_words,
                SUM(CASE WHEN difficulty = 'easy' THEN 1 ELSE 0 END) as easy_count,
                SUM(CASE WHEN difficulty = 'fair' THEN 1 ELSE 0 END) as fair_count,
                SUM(CASE WHEN difficulty = 'hard' THEN 1 ELSE 0 END) as hard_count,
                SUM(CASE WHEN mastered = TRUE THEN 1 ELSE 0 END) as mastered_count,
                SUM(CASE WHEN difficulty = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(times_correct) as total_correct,
                SUM(times_incorrect) as total_incorrect
            FROM user_word_mastery
            WHERE user_id = %s
        """, (user_id,))
        
        stats = cursor.fetchone()
        
        # Get total study sessions
        cursor.execute("""
            SELECT COUNT(*) as total_sessions
            FROM flashcard_sessions
            WHERE user_id = %s
        """, (user_id,))
        
        session_stats = cursor.fetchone()
        
        # Get current level
        current_level = get_current_level(user_id)
        
        cursor.close()
        conn.close()
        
        if not stats:
            stats = {
                'total_words': 0,
                'easy_count': 0,
                'fair_count': 0,
                'hard_count': 0,
                'mastered_count': 0,
                'new_count': 0,
                'total_correct': 0,
                'total_incorrect': 0
            }
        
        # Add session count to stats
        stats['total_sessions'] = session_stats['total_sessions'] if session_stats else 0
        stats['current_level'] = current_level
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting user profile stats: {e}")
        return {
            'total_words': 0,
            'easy_count': 0,
            'fair_count': 0,
            'hard_count': 0,
            'mastered_count': 0,
            'new_count': 0,
            'total_correct': 0,
            'total_incorrect': 0,
            'total_sessions': 0,
            'current_level': 1
        }

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page with statistics"""
    try:
        user = get_current_user(request)
        
        # Get user statistics
        stats = get_user_profile_stats(user['id'])
        
        # Get progress by level
        level_progress = get_progress_by_level(user['id'])
        
        # Calculate accuracy rate (convert Decimal to float to avoid type errors)
        total_correct = float(stats['total_correct'] or 0)
        total_incorrect = float(stats['total_incorrect'] or 0)
        total_answers = total_correct + total_incorrect
        accuracy_rate = round((total_correct / total_answers * 100), 1) if total_answers > 0 else 0
        
        # Calculate progress ring values
        circumference = 2 * 3.14159 * 36  # ~226
        accuracy_offset = circumference - (accuracy_rate / 100 * circumference)
        
        # Convert stats values to float for template rendering
        for key in stats:
            if stats[key] is not None:
                try:
                    stats[key] = float(stats[key])
                except (TypeError, ValueError):
                    pass
        
        # Convert level_progress values to float as well
        if level_progress:
            for level in level_progress:
                for key in level:
                    if level[key] is not None:
                        try:
                            level[key] = float(level[key])
                        except (TypeError, ValueError):
                            pass
        
        return templates.TemplateResponse(request=request, name="profile.html",
                                        context={
                                            "user": user,
                                            "stats": stats,
                                            "level_progress": level_progress,
                                            "accuracy_rate": accuracy_rate,
                                            "accuracy_circumference": circumference,
                                            "accuracy_offset": accuracy_offset
                                        })
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        logger.error(f"Profile page error: {e}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/api/study/next-word")
async def get_next_study_word(request: Request):
    """Get the next word for the user to study"""
    try:
        user = get_current_user(request)
        word = get_next_word_to_study(user['id'])
        
        if word:
            return {
                "word": {
                    "id": word['id'],
                    "level": word['level'],
                    "hanzi": word['hanzi'],
                    "pinyin": word['pinyin'],
                    "pinyin_tone": word['pinyin_tone'],
                    "pinyin_num": word['pinyin_num'],
                    "english": word['english'],
                    "pos": word['pos'],
                    "tts_url": word['tts_url'],
                    "difficulty": word['difficulty'],
                    "times_studied": word['times_studied'],
                    "current_streak": word['current_streak']
                }
            }
        else:
            return {"word": None}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get next study word error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get next word")

@app.get("/api/study/word/{word_id}")
async def get_specific_word(request: Request, word_id: int):
    """Get a specific word by ID for review"""
    try:
        user = get_current_user(request)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT w.id, w.level, w.hanzi, w.pinyin, w.pinyin_tone, w.pinyin_num,
                   w.english, w.pos, w.tts_url,
                   COALESCE(uwm.difficulty, 'new') as difficulty,
                   COALESCE(uwm.times_studied, 0) as times_studied,
                   COALESCE(uwm.current_streak, 0) as current_streak
            FROM words w
            LEFT JOIN user_word_mastery uwm ON w.id = uwm.word_id AND uwm.user_id = %s
            WHERE w.id = %s
        """, (user['id'], word_id))
        
        word = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if word:
            return {"word": word}
        else:
            return {"word": None}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get specific word error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get word")

@app.post("/api/study/record")
async def record_study_answer(request: Request, word_id: int = Form(...), 
                               user_answer: str = Form(None), is_correct: str = Form(...),
                               difficulty: str = Form(None)):
    """Record a study answer and update mastery"""
    try:
        user = get_current_user(request)
        
        # Convert is_correct to boolean
        is_correct_bool = is_correct.lower() == 'true'
        
        # Update word mastery
        update_word_mastery(user['id'], word_id, is_correct_bool, difficulty)
        
        # Record in flashcard_study if we have an active session
        session = get_study_session(user['id'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if session:
            # Record the study entry
            cursor.execute("""
                INSERT INTO flashcard_study (session_id, word_id, user_answer, is_correct, difficulty)
                VALUES (%s, %s, %s, %s, %s)
            """, (session['id'], word_id, user_answer, is_correct_bool, difficulty))
            
            # Update session stats
            cursor.execute("""
                UPDATE flashcard_sessions 
                SET total_cards = total_cards + 1,
                    correct_count = correct_count + %s,
                    incorrect_count = incorrect_count + %s
                WHERE id = %s
            """, (1 if is_correct_bool else 0, 0 if is_correct_bool else 1, session['id']))
        else:
            # Create new session
            cursor.execute("""
                INSERT INTO flashcard_sessions (user_id, total_cards, correct_count, incorrect_count)
                VALUES (%s, 1, %s, %s)
            """, (user['id'], 1 if is_correct_bool else 0, 0 if is_correct_bool else 1))
            
            session_id = cursor.lastrowid
            
            # Record the study entry
            cursor.execute("""
                INSERT INTO flashcard_study (session_id, word_id, user_answer, is_correct, difficulty)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, word_id, user_answer, is_correct_bool, difficulty))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Answer recorded", "is_correct": is_correct_bool}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record study answer error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record answer")

@app.get("/api/study/progress")
async def get_study_progress(request: Request):
    """Get user's overall study progress"""
    try:
        user = get_current_user(request)
        
        # Get mastery stats
        stats = get_user_mastery_stats(user['id'])
        
        # Get progress by level
        levels = get_progress_by_level(user['id'])
        
        # Get current level
        current_level = get_current_level(user['id'])
        
        return {
            "stats": stats,
            "levels": levels,
            "current_level": current_level
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get study progress error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    response.delete_cookie("is_first_time")
    return response

if __name__ == "__main__":
    # Create tables on startup
    create_tables()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)