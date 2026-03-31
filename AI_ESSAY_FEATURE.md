# AI Essay Generation Feature

This document describes the AI-powered essay generation feature added to the Chinese Self Learning System.

## Overview

The AI Essay feature generates daily Chinese essays tailored to the user's HSK level using the Groq API. It includes:

- **Daily Essays**: AI-generated Chinese essays (80-120 characters) based on the user's current HSK level
- **Complete Learning Content**: Each essay includes Chinese text, pinyin with tone marks, English translation, and key vocabulary
- **Interactive Word Lookup**: Click any character in the essay to see detailed explanations
- **AI Chat Assistant**: Ask questions about the essay content and get instant explanations
- **Text-to-Speech**: Listen to the essay being read aloud

## Files Added

1. **`ai_essay.py`** - Core AI essay generation logic using Groq API
2. **`essay_routes.py`** - API endpoints for essay functionality
3. **`templates/essay_modal.html`** - The essay modal UI with chat functionality

## Setup

### 1. Install Dependencies

The Groq package has been added to `pyproject.toml`. Install dependencies:

```bash
uv sync
# or
pip install groq
```

### 2. Set Your Groq API Key

Set your Groq API key in the `ai_essay.py` file:

1. Open `ai_essay.py`
2. Find the line: `GROQ_API_KEY = ""`
3. Replace the empty string with your actual Groq API key:
   ```python
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```

### 3. Access the Feature

1. Restart your server if it's running
2. Log in to your account
3. On the dashboard, click the **"Essay of the Day"** button (orange gradient button in Quick Actions)
4. The essay modal will open with your personalized daily essay

## Features

### Essay Content

Each essay includes:
- **Chinese Text**: 80-120 characters appropriate for your HSK level
- **Title**: A descriptive title in Chinese
- **English Translation**: Complete translation of the essay
- **Key Vocabulary**: 5-8 important words with pinyin and meanings
- **Cultural Notes**: Context about Chinese culture related to the essay

### Interactive Word Lookup

- Click any character in the essay text to see its meaning
- The character will be highlighted and a popup will show:
  - Pinyin with tone marks
  - Part of speech
  - English meanings
  - Example sentences
  - Usage notes

### AI Chat Assistant

At the bottom of the essay modal, you'll find a chat interface where you can:
- Ask questions about specific words or phrases
- Request grammar explanations
- Get cultural context
- Ask for synonyms or related words

Example questions:
- "What does 天气 mean?"
- "Explain the grammar in the second sentence"
- "What's the difference between 漂亮 and 美丽?"

### Text-to-Speech

Click the "Listen" button below the Chinese text to hear the essay read aloud using your browser's built-in speech synthesis.

## API Reference

### Get Daily Essay
```
GET /api/essay/daily
Headers: X-Groq-API-Key: your-api-key
Response: { "essay": { ... }, "cached": false }
```

### Explain a Word
```
POST /api/essay/word-explain
Headers: Content-Type: application/json, X-Groq-API-Key: your-api-key
Body: { "word": "天气", "context": "optional context" }
Response: { "explanation": { ... } }
```

### Chat About Essay
```
POST /api/essay/chat
Headers: Content-Type: application/json, X-Groq-API-Key: your-api-key
Body: { "essay_content": "Chinese text", "question": "Your question" }
Response: { "response": "AI response text" }
```

## HSK Level Adaptation

The essay generation automatically adapts to your current HSK level:

| Level | Vocabulary | Description |
|-------|------------|-------------|
| HSK 1 | 150 words | Basic beginner level with simple daily expressions |
| HSK 2 | 300 words | Elementary level for simple communication |
| HSK 3 | 600 words | Intermediate level for daily conversations |
| HSK 4 | 1200 words | Upper intermediate for discussing various topics |
| HSK 5 | 2500 words | Advanced level for reading newspapers and giving speeches |
| HSK 6 | 5000+ words | Proficient level for comprehensive understanding |

## Sample Essays (Offline Mode)

If you don't have an API key set, the system will display sample essays for HSK 1-2 levels. These are pre-written essays that demonstrate the feature's capabilities.

## Troubleshooting

### Essay not loading
- Check your internet connection
- Verify your Groq API key is valid
- Try clicking "Retry" if you see an error

### Chat not responding
- Ensure your API key is set
- Check that you have API credits remaining on your Groq account
- Try refreshing the page

### Text-to-Speech not working
- Check your browser's speech synthesis settings
- Ensure your browser supports the SpeechSynthesis API
- Try using Chrome or Edge for best compatibility

## Privacy Note

- Your Groq API key is stored locally in your browser's localStorage
- Essay content is generated on-demand and cached for the day
- No personal data is sent to external servers beyond what's required for API calls

## Future Enhancements

Potential improvements for the future:
- Save favorite essays to a personal collection
- Generate essays on specific topics
- Add more language pairs for translation
- Export essays as PDF or Anki cards
- Voice recognition for pronunciation practice