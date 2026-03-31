"""
Flashcard Module for Chinese Self Learning System
This module handles all flashcard-related functionality including:
- Studying words from HSK 1-6
- Testing users on word meanings
- Spaced repetition scheduling (Anki-style)
- Progress tracking
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Router for flashcard endpoints
flashcard_router = APIRouter()

# Templates
templates = Jinja2Templates(directory="templates")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'joshua6775',
    'database': 'cls'
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise Exception(f"Database connection failed: {e}")


def create_flashcard_tables():
    """Create flashcard-specific tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Flashcard sessions table - tracks a study session
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                total_cards INT DEFAULT 0,
                correct_count INT DEFAULT 0,
                incorrect_count INT DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Flashcard study progress - tracks progress within a session
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_study (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                word_id INT NOT NULL,
                user_answer TEXT,
                is_correct BOOLEAN,
                difficulty ENUM('new', 'easy', 'fair', 'hard') DEFAULT 'new',
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                interval_hours INT DEFAULT 0,
                studied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES flashcard_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
            )
        """)
        
        # User word mastery - tracks overall mastery of each word
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
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                interval_hours INT DEFAULT 0,
                mastered BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_word (user_id, word_id)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Flashcard tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating flashcard tables: {e}")


def get_user_mastery_stats(user_id: int):
    """Get user's mastery statistics"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
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
    cursor.close()
    conn.close()
    
    return stats if stats else {
        'total_words': 0,
        'easy_count': 0,
        'fair_count': 0,
        'hard_count': 0,
        'mastered_count': 0,
        'new_count': 0,
        'total_correct': 0,
        'total_incorrect': 0
    }


def get_next_word_to_study(user_id: int, session_words: list = None):
    """Get the next word for the user to study based on spaced repetition"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # First, check for words due for review (next_review <= now)
    query = """
        SELECT w.id, w.level, w.hanzi, w.pinyin, w.pinyin_tone, w.pinyin_num, 
               w.english, w.pos, w.tts_url,
               uwm.difficulty, uwm.times_studied, uwm.current_streak
        FROM user_word_mastery uwm
        JOIN words w ON uwm.word_id = w.id
        WHERE uwm.user_id = %s 
            AND uwm.next_review <= NOW()
    """
    params = [user_id]
    
    if session_words:
        # Exclude words already studied in this session
        placeholders = ','.join(['%s'] * len(session_words))
        query += f" AND w.id NOT IN ({placeholders})"
        params.extend(session_words)
    
    query += " ORDER BY uwm.difficulty DESC, w.level ASC, uwm.next_review ASC LIMIT 1"
    
    cursor.execute(query, params)
    word = cursor.fetchone()
    
    # If no words due for review, get a new word the user hasn't studied yet
    if not word:
        new_query = """
            SELECT w.id, w.level, w.hanzi, w.pinyin, w.pinyin_tone, w.pinyin_num,
                   w.english, w.pos, w.tts_url,
                   'new' as difficulty, 0 as times_studied, 0 as current_streak
            FROM words w
            LEFT JOIN user_word_mastery uwm ON w.id = uwm.word_id AND uwm.user_id = %s
            WHERE uwm.id IS NULL
        """
        new_params = [user_id]
        
        if session_words:
            placeholders = ','.join(['%s'] * len(session_words))
            new_query += f" AND w.id NOT IN ({placeholders})"
            new_params.extend(session_words)
        
        new_query += " ORDER BY w.level ASC LIMIT 1"
        
        cursor.execute(new_query, new_params)
        word = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return word


def get_study_session(user_id: int):
    """Get or create a study session for the user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check for an active session (started less than 2 hours ago and not completed)
    cursor.execute("""
        SELECT id, started_at, total_cards, correct_count, incorrect_count
        FROM flashcard_sessions
        WHERE user_id = %s 
            AND started_at > DATE_SUB(NOW(), INTERVAL 2 HOUR)
            AND completed_at IS NULL
        ORDER BY started_at DESC
        LIMIT 1
    """, (user_id,))
    
    session = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return session


def update_word_mastery(user_id: int, word_id: int, is_correct: bool, difficulty: str = None):
    """Update user's mastery of a word based on their answer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if mastery record exists
    cursor.execute("""
        SELECT id, difficulty, times_studied, times_correct, times_incorrect, 
               current_streak, best_streak, interval_hours
        FROM user_word_mastery
        WHERE user_id = %s AND word_id = %s
    """, (user_id, word_id))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing record
        times_studied = existing[2] + 1
        times_correct = existing[3] + (1 if is_correct else 0)
        times_incorrect = existing[4] + (0 if is_correct else 1)
        
        if is_correct:
            current_streak = existing[5] + 1
            best_streak = max(existing[6], current_streak)
        else:
            current_streak = 0
            best_streak = existing[6]
        
        # Calculate new interval based on difficulty
        interval_map = {
            'new': 0,      # Review immediately
            'hard': 1,     # 1 hour
            'fair': 6,     # 6 hours
            'easy': 24     # 24 hours (1 day)
        }
        
        if difficulty is None:
            # Auto-determine difficulty based on streak
            if current_streak >= 5:
                difficulty = 'easy'
            elif current_streak >= 3:
                difficulty = 'fair'
            else:
                difficulty = 'hard'
        
        interval_hours = interval_map.get(difficulty, 1)
        next_review = datetime.now() + timedelta(hours=interval_hours)
        
        # Check if word is mastered (easy difficulty with 5+ streak)
        mastered = (difficulty == 'easy' and current_streak >= 5)
        
        cursor.execute("""
            UPDATE user_word_mastery 
            SET difficulty = %s, times_studied = %s, times_correct = %s,
                times_incorrect = %s, current_streak = %s, best_streak = %s,
                next_review = %s, interval_hours = %s, mastered = %s
            WHERE user_id = %s AND word_id = %s
        """, (difficulty, times_studied, times_correct, times_incorrect,
              current_streak, best_streak, next_review, interval_hours, mastered,
              user_id, word_id))
    else:
        # Create new mastery record
        difficulty = 'hard' if not is_correct else 'fair'
        interval_hours = 1 if not is_correct else 6
        next_review = datetime.now() + timedelta(hours=interval_hours)
        
        cursor.execute("""
            INSERT INTO user_word_mastery 
            (user_id, word_id, difficulty, times_studied, times_correct, 
             times_incorrect, current_streak, best_streak, next_review, interval_hours, mastered)
            VALUES (%s, %s, %s, 1, %s, %s, %s, %s, %s, %s, FALSE)
        """, (user_id, word_id, difficulty, 1 if is_correct else 0,
              0 if is_correct else 1, 1 if is_correct else 0,
              1 if is_correct else 0, next_review, interval_hours))
    
    conn.commit()
    cursor.close()
    conn.close()


def get_progress_by_level(user_id: int):
    """Get user's progress grouped by HSK level"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            w.level,
            COUNT(*) as total_words,
            SUM(CASE WHEN uwm.mastered = TRUE THEN 1 ELSE 0 END) as mastered,
            SUM(CASE WHEN uwm.difficulty = 'easy' THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN uwm.difficulty = 'fair' THEN 1 ELSE 0 END) as fair,
            SUM(CASE WHEN uwm.difficulty = 'hard' THEN 1 ELSE 0 END) as hard,
            SUM(CASE WHEN uwm.id IS NULL THEN 1 ELSE 0 END) as new_words
        FROM words w
        LEFT JOIN user_word_mastery uwm ON w.id = uwm.word_id AND uwm.user_id = %s
        GROUP BY w.level
        ORDER BY w.level ASC
    """, (user_id,))
    
    progress = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return progress


def get_current_level(user_id: int):
    """Determine user's current HSK level based on mastered words"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # A user advances to the next level when they've mastered 80% of current level
    cursor.execute("""
        SELECT 
            w.level,
            COUNT(*) as total_words,
            SUM(CASE WHEN uwm.mastered = TRUE THEN 1 ELSE 0 END) as mastered
        FROM words w
        LEFT JOIN user_word_mastery uwm ON w.id = uwm.word_id AND uwm.user_id = %s
        GROUP BY w.level
        ORDER BY w.level ASC
    """, (user_id,))
    
    levels = cursor.fetchall()
    cursor.close()
    conn.close()
    
    current_level = 1
    for level in levels:
        if level['total_words'] > 0:
            mastery_pct = level['mastered'] / level['total_words']
            if mastery_pct >= 0.8:
                current_level = level['level'] + 1
            else:
                break
    
    return min(current_level, 6)  # Cap at HSK 6

