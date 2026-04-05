# Chinese Self Learning System - Configuration Guide

## Overview
The Chinese Self Learning System now uses environment variables for all sensitive configuration data (database credentials, API keys). This makes it easy to deploy and keeps sensitive information secure.

## Quick Start

### 1. Install Dependencies
```bash
pip install python-dotenv
```

Or if you're using the project's dependency management:
```bash
pip install -e .
```

### 2. Create `.env` File
Copy the example configuration file:
```bash
cp .env.example .env
```

### 3. Configure Your Settings
Edit the `.env` file with your actual values:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_database_password
DB_DATABASE=cls

# Groq API Key for AI Essay Features
# Get your API key from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Application Configuration
APP_HOST=127.0.0.1
APP_PORT=3000
IS_PRODUCTION=False
```

## Configuration Options

### Database Configuration
- **DB_HOST**: Database server hostname (default: `localhost`)
- **DB_USER**: Database username (default: `root`)
- **DB_PASSWORD**: Database password (required)
- **DB_DATABASE**: Database name (default: `cls`)

### API Configuration
- **GROQ_API_KEY**: Your Groq API key for AI essay generation features
  - Required for: AI-generated essays, word explanations, essay chat
  - Get your key at: https://console.groq.com/
  - Without this key, AI features will fall back to sample essays

### Application Configuration
- **APP_HOST**: Host address to run the application on (default: `127.0.0.1`)
- **APP_PORT**: Port number for the application (default: `3000`)
- **IS_PRODUCTION**: Set to `True` for production deployment (default: `False`)

## For Production Deployment (Render, etc.)

When deploying to production platforms like Render:

1. **Set Environment Variables in Platform Dashboard**
   - Add all the above variables in your Render dashboard
   - Do NOT commit the `.env` file to git

2. **Configure for Production**
   ```env
   IS_PRODUCTION=True
   APP_HOST=0.0.0.0
   # Use your Aiven MySQL credentials
   DB_HOST=mysql-xxxx.aivencloud.com
   DB_USER=avnadmin
   DB_PASSWORD=your_aiven_password
   DB_DATABASE=cls
   GROQ_API_KEY=your_groq_api_key
   ```

3. **Database SSL/TLS**
   - The application automatically supports Aiven MySQL SSL/TLS connections when in production mode

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit the `.env` file to version control
- The `.env` file is already listed in `.gitignore`
- For production, always use environment variables provided by your hosting platform
- Rotate your API keys regularly

## Troubleshooting

### Database Connection Errors
- Verify your database credentials in `.env`
- Ensure MySQL server is running
- Check that the database `cls` exists

### API Key Errors
- Verify your Groq API key is correct
- Check that the key has not expired
- Ensure you have sufficient API credits

### Module Import Errors
- Make sure `python-dotenv` is installed: `pip install python-dotenv`
- Verify you're running Python 3.8 or higher

## Development Workflow

1. **Clone the repository**
2. **Copy `.env.example` to `.env`**
3. **Fill in your credentials**
4. **Install dependencies**: `pip install -e .`
5. **Run the application**: `python main.py`

## Files Modified

The following files now use the centralized configuration:
- `main.py` - Main application
- `flashcard_app.py` - Flashcard functionality
- `essay_routes.py` - AI essay routes
- `stroke_order_routes.py` - Stroke order feature
- `ai_essay.py` - AI essay generation
- `populate_db.py` - Database population script

All these files import configuration from `config.py`, which reads from the `.env` file.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the error logs
3. Verify your `.env` configuration matches the requirements
