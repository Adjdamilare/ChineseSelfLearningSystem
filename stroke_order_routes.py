"""
Stroke Order Search Feature Module
Provides stroke order search with English meanings for Chinese characters
Uses Hanzi Writer CDN for accurate stroke order animations
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
import logging

logger = logging.getLogger(__name__)

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
        raise HTTPException(status_code=500, detail="Database connection failed")

def search_words_with_meaning(query, limit=20):
    """
    Search for Chinese words and return characters + English meaning
    Hanzi Writer CDN will handle stroke order data
    """
    results = []
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Search in words table for matching Chinese characters
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT id, hanzi, pinyin, english, pos
            FROM words 
            WHERE hanzi LIKE %s
            LIMIT %s
        """, (search_term, limit))
        
        words = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # For each word, extract Chinese characters
        for word in words:
            hanzi = word['hanzi']
            # Extract only Chinese characters
            chinese_chars = [char for char in hanzi if '\u4e00' <= char <= '\u9fff']
            
            if chinese_chars:
                results.append({
                    "word": hanzi,
                    "pinyin": word['pinyin'] or "N/A",
                    "english": word['english'] or "N/A",
                    "pos": word['pos'] or "N/A",
                    "characters": [{"character": char} for char in chinese_chars]
                })
        
        # If no results from database, use the query characters directly
        if not results:
            chinese_chars = [char for char in query if '\u4e00' <= char <= '\u9fff']
            if chinese_chars:
                results.append({
                    "word": query,
                    "pinyin": "N/A",
                    "english": "Character lookup",
                    "pos": "character",
                    "characters": [{"character": char} for char in chinese_chars]
                })
        
        return results[:limit]
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        if conn:
            try:
                cursor.close()
                conn.close()
            except:
                pass
        # Fallback: use query characters directly
        chinese_chars = [char for char in query if '\u4e00' <= char <= '\u9fff']
        if chinese_chars:
            return [{
                "word": query,
                "pinyin": "N/A",
                "english": "Character lookup",
                "pos": "character",
                "characters": [{"character": char} for char in chinese_chars]
            }]
        return []

# Create the router
stroke_order_router = APIRouter()
stroke_order_templates = Jinja2Templates(directory="templates")

@stroke_order_router.get("/stroke-order", response_class=HTMLResponse)
async def stroke_order_page(request: Request):
    """Stroke order search page"""
    try:
        session_token = request.cookies.get("session_token")
        if not session_token:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/login", status_code=302)
        
        return stroke_order_templates.TemplateResponse(
            request=request, 
            name="stroke_order.html"
        )
    except Exception as e:
        logger.error(f"Stroke order page error: {e}")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login", status_code=302)

@stroke_order_router.get("/api/stroke-order/search")
async def api_search_stroke_order(q: str, limit: int = 20):
    """API endpoint for searching Chinese words with stroke order"""
    try:
        if not q or len(q.strip()) < 1:
            return JSONResponse(
                content={"error": "Please enter a search term", "results": []}, 
                status_code=400
            )
        
        results = search_words_with_meaning(q.strip(), limit)
        
        return {
            "query": q,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Stroke order search error: {e}")
        return JSONResponse(
            content={"error": "Search failed", "results": []}, 
            status_code=500
        )