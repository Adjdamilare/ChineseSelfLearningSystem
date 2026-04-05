# Quick Setup Guide - Chinese Self Learning System

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install python-dotenv
```

### Step 2: Create Configuration File
```bash
# On Windows (PowerShell):
Copy-Item .env.example .env

# On Windows (Command Prompt):
copy .env.example .env

# On Mac/Linux:
cp .env.example .env
```

### Step 3: Edit `.env` File
Open the `.env` file and update these values:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_DATABASE_PASSWORD
DB_DATABASE=cls

# Groq API Key (Get from https://console.groq.com/)
GROQ_API_KEY=your_api_key_here

# Application Settings (optional)
APP_HOST=127.0.0.1
APP_PORT=3000
IS_PRODUCTION=False
```

## ✅ That's It!

Run your application:
```bash
python main.py
```

## 📝 What Changed?

- ❌ No more hardcoded passwords in the code
- ✅ All configuration in one secure `.env` file
- ✅ Easy to deploy to production
- ✅ Different configs for different environments

## 🔧 Need Help?

See [CONFIGURATION.md](CONFIGURATION.md) for detailed documentation.

## 📦 Files Overview

```
.env                 # Your private configuration (DO NOT COMMIT)
.env.example         # Template for .env (safe to share)
config.py            # Configuration loader (auto-imports .env)
.gitignore           # Excludes .env from git
CONFIGURATION.md     # Detailed setup guide
REFACTORING_SUMMARY.md  # Complete list of changes
```

## ⚠️ Important Notes

1. **Never share your `.env` file** - it contains sensitive credentials
2. The `.env` file is already excluded from git via `.gitignore`
3. For production deployment, set environment variables in your hosting platform
4. Without `GROQ_API_KEY`, AI essay features will use sample essays instead

---

**Need more details?** Check out the full [CONFIGURATION.md](CONFIGURATION.md) guide.
