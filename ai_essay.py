"""
AI Essay Generation Module for Chinese Self Learning System
This module handles AI-generated Chinese essays using Groq API.
Features:
- Generate daily Chinese essays based on user's HSK level
- Include Chinese characters, pinyin with tones, and English translation
- Chat function for word meaning inquiries
"""

from groq import Groq
import logging
import json
from typing import Optional, Dict, List
from datetime import datetime, date
from config import get_groq_api_key

logger = logging.getLogger(__name__)

# ============================================
# GROQ API KEY CONFIGURATION
# ============================================
# API key is now loaded from .env file via config module
# You can set it in the .env file:
# GROQ_API_KEY=your_api_key_here
# ============================================

# Get Groq API key from config (loaded from .env)
GROQ_API_KEY = get_groq_api_key()

# Groq API client
_client = None

def get_groq_client() -> Groq:
    """Get or create Groq client with the configured API key"""
    global _client
    if _client is None and GROQ_API_KEY:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client

def set_api_key(api_key: str):
    """Set the Groq API key"""
    global _client, GROQ_API_KEY
    GROQ_API_KEY = api_key
    _client = Groq(api_key=api_key)
    return _client

# HSK level vocabulary expectations
HSK_LEVEL_INFO = {
    1: {"name": "HSK 1", "vocab_count": "150 words", "description": "Basic beginner level with simple daily expressions"},
    2: {"name": "HSK 2", "vocab_count": "300 words", "description": "Elementary level for simple communication"},
    3: {"name": "HSK 3", "vocab_count": "600 words", "description": "Intermediate level for daily conversations"},
    4: {"name": "HSK 4", "vocab_count": "1200 words", "description": "Upper intermediate for discussing various topics"},
    5: {"name": "HSK 5", "vocab_count": "2500 words", "description": "Advanced level for reading newspapers and giving speeches"},
    6: {"name": "HSK 6", "vocab_count": "5000+ words", "description": "Proficient level for comprehensive understanding"}
}

def generate_essay_prompt(hsk_level: int, date_str: str) -> str:
    """Generate the prompt for the AI to create an essay"""
    level_info = HSK_LEVEL_INFO.get(hsk_level, HSK_LEVEL_INFO[1])
    
    prompt = f"""You are a Chinese language teaching assistant. Generate a short Chinese essay (approximately 80-120 Chinese characters) for a student at {level_info['name']} level.

Requirements:
1. The essay should be appropriate for {level_info['description']}
2. Topic: Daily life, hobbies, family, food, or culture - something engaging and educational
3. Use vocabulary appropriate for HSK {hsk_level} level
4. The essay should be coherent and meaningful
5. ALL Chinese text MUST include the actual Chinese characters (simplified Chinese)

Date context: {date_str} (you can reference the season or time of year if relevant)

IMPORTANT: The response MUST be valid JSON. Do not include any markdown formatting or code blocks. Return ONLY the JSON object.

Please provide the response in the following JSON format:
{{
    "chinese": "The Chinese essay text here with Chinese characters (e.g., 今天天气很好。)",
    "title": "A short title for the essay in Chinese characters (e.g., 在公园)",
    "english_translation": "Complete English translation of the essay",
    "vocabulary": [
        {{
            "word": "Chinese word with characters (e.g., 天气)",
            "pinyin": "pinyin with tone marks (e.g., tiānqì)",
            "meaning": "English meaning",
            "pos": "part of speech"
        }}
    ],
    "cultural_notes": "Brief cultural context or learning tips"
}}

Make sure the vocabulary list includes 5-8 key words from the essay that are important for learning. All Chinese text must include the actual simplified Chinese characters."""

    return prompt

def generate_daily_essay(hsk_level: int) -> Optional[Dict]:
    """
    Generate a daily Chinese essay using Groq API
    
    Args:
        hsk_level: User's current HSK level (1-6)
    
    Returns:
        Dictionary containing essay data or None if generation fails
    """
    try:
        client = get_groq_client()
        if not client:
            logger.error("Groq client not initialized. Please set API key in ai_essay.py")
            return None
        
        date_str = date.today().strftime("%B %d, %Y")
        prompt = generate_essay_prompt(hsk_level, date_str)
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful Chinese language teaching assistant. Always respond in valid JSON format as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        response_content = completion.choices[0].message.content
        
        # Parse the JSON response
        # Sometimes the response might have markdown code blocks
        if "```json" in response_content:
            response_content = response_content.split("```json")[1].split("```")[0].strip()
        elif "```" in response_content:
            response_content = response_content.split("```")[1].split("```")[0].strip()
        
        essay_data = json.loads(response_content)
        
        # Add metadata
        essay_data['date'] = date_str
        essay_data['hsk_level'] = hsk_level
        essay_data['word_count'] = len(essay_data.get('chinese', ''))
        
        return essay_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        logger.error(f"Raw response: {response_content if 'response_content' in locals() else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"Error generating essay: {e}")
        return None

def explain_word(word: str, context: str = "") -> Optional[Dict]:
    """
    Explain the meaning of a Chinese word using Groq API
    
    Args:
        word: The Chinese word to explain
        context: Optional context (e.g., the essay it appeared in)
    
    Returns:
        Dictionary containing word explanation or None if failed
    """
    try:
        client = get_groq_client()
        if not client:
            logger.error("Groq client not initialized. Please set API key in ai_essay.py")
            return None
        
        context_prompt = f"\nContext: This word appeared in an essay about: {context}" if context else ""
        
        prompt = f"""Your job is to explain the Chinese word "{word}" and generate example sentences for it.

{context_prompt}

For this word, please provide:
1. Pinyin with tone marks
2. Part of speech
3. English meanings
4. Example sentences - generate sentences using this word with:
   - Chinese sentence in simplified Chinese characters
   - Pinyin with tone marks
   - English translation
5. Usage notes or common collocations
6. Related words or synonyms (with Chinese characters)

IMPORTANT: 
- ALL Chinese text MUST include the actual simplified Chinese characters
- Do not use only pinyin - always include the Chinese characters
- Generate correct, natural sentences

Respond in JSON format:
{{
    "word": "{word}",
    "pinyin": "pinyin with tone marks (e.g., tiānqì)",
    "pos": "part of speech",
    "meanings": ["meaning 1", "meaning 2"],
    "example_sentences": [
        {{
            "chinese": "Example sentence with Chinese characters (e.g., 今天天气很好。)",
            "pinyin": "Jīntiān tiānqì hěn hǎo.",
            "english": "The weather is very good today."
        }}
    ],
    "usage_notes": "Usage tips and common collocations",
    "related_words": ["related word with characters (pinyin)", "another related word (pinyin)"]
}}"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Chinese language expert. Always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        
        response_content = completion.choices[0].message.content
        
        # Parse JSON response
        if "```json" in response_content:
            response_content = response_content.split("```json")[1].split("```")[0].strip()
        elif "```" in response_content:
            response_content = response_content.split("```")[1].split("```")[0].strip()
        
        explanation = json.loads(response_content)
        return explanation
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse word explanation as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error explaining word: {e}")
        return None

def chat_about_essay(essay_content: str, user_question: str) -> Optional[str]:
    """
    Have a conversation about the essay content
    
    Args:
        essay_content: The Chinese essay content
        user_question: User's question about the essay
    
    Returns:
        AI response as string or None if failed
    """
    try:
        client = get_groq_client()
        if not client:
            logger.error("Groq client not initialized. Please set API key in ai_essay.py")
            return None
        
        prompt = f"""You are a Chinese language teaching assistant. Your job is to help users learn Chinese by generating sentences for words they ask about.

Essay context (in Chinese):
{essay_content}

User's question: {user_question}

Your task:
1. If the user asks about a Chinese word or phrase, generate example sentences using that word
2. Each sentence must include:
   - Chinese sentence in simplified Chinese characters
   - Pinyin with tone marks
   - English translation
3. If the user asks about an English word, provide the Chinese translation and generate sentences

IMPORTANT RULES:
- ALWAYS include Chinese characters (simplified Chinese) in your response
- ALWAYS include pinyin with tone marks
- ALWAYS include English translation
- Only answer questions related to Chinese language and vocabulary
- If the question is not about Chinese language, politely redirect: "I'm here to help with Chinese language learning. Please ask me about Chinese vocabulary, characters, or sentences!"
- Do NOT generate sentences for words that don't exist
- Do NOT provide incorrect information

Example response format:
"For the word 天气 (tiānqì, weather):
- 今天天气很好。 (Jīntiān tiānqì hěn hǎo.) - The weather is very good today.
- 你喜欢什么样的天气？ (Nǐ xǐhuan shénme yàng de tiānqì?) - What kind of weather do you like?"

Keep responses educational and focused on Chinese language learning."""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly and knowledgeable Chinese language tutor. Help students understand Chinese texts clearly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=512,
            top_p=1,
            stream=False,
            stop=None
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in essay chat: {e}")
        return None

# Sample essay for testing or when API is not available
SAMPLE_ESSAYS = {
    1: {
        "chinese": "今天天气很好。我和妈妈去公园。公园里有很多花。花很漂亮。我们玩得很开心。",
        "title": "在公园",
        "english_translation": "Today the weather is very good. Mom and I went to the park. There are many flowers in the park. The flowers are very beautiful. We had a great time.",
        "vocabulary": [
            {"word": "天气", "pinyin": "tiānqì", "meaning": "weather", "pos": "noun"},
            {"word": "妈妈", "pinyin": "māma", "meaning": "mom", "pos": "noun"},
            {"word": "公园", "pinyin": "gōngyuán", "meaning": "park", "pos": "noun"},
            {"word": "花", "pinyin": "huā", "meaning": "flower", "pos": "noun"},
            {"word": "漂亮", "pinyin": "piàoliang", "meaning": "beautiful", "pos": "adjective"}
        ],
        "cultural_notes": "Going to parks is a popular family activity in China. Many Chinese parks feature beautiful gardens with seasonal flowers."
    },
    2: {
        "chinese": "我的好朋友叫小明。他今年十二岁。他喜欢踢足球和看书。我们经常一起做作业。他是一个很聪明的人。",
        "title": "我的好朋友",
        "english_translation": "My good friend is called Xiaoming. He is twelve years old this year. He likes playing soccer and reading books. We often do homework together. He is a very smart person.",
        "vocabulary": [
            {"word": "朋友", "pinyin": "péngyou", "meaning": "friend", "pos": "noun"},
            {"word": "喜欢", "pinyin": "xǐhuan", "meaning": "to like", "pos": "verb"},
            {"word": "踢足球", "pinyin": "tī zúqiú", "meaning": "to play soccer", "pos": "verb phrase"},
            {"word": "经常", "pinyin": "jīngcháng", "meaning": "often", "pos": "adverb"},
            {"word": "聪明", "pinyin": "cōngming", "meaning": "smart", "pos": "adjective"}
        ],
        "cultural_notes": "Chinese students often study together in groups. Friendship is highly valued in Chinese culture."
    }
}

def get_sample_essay(hsk_level: int) -> Optional[Dict]:
    """Get a sample essay for testing purposes"""
    # Return the closest available sample
    if hsk_level <= 1:
        return SAMPLE_ESSAYS[1]
    elif hsk_level <= 2:
        return SAMPLE_ESSAYS[2]
    else:
        # For higher levels, return HSK 2 essay as fallback
        return SAMPLE_ESSAYS[2]