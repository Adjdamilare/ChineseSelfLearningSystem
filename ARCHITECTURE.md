# Configuration Architecture

## System Architecture After Refactoring

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   main.py    │  │flashcard_app.│  │essay_routes. │      │
│  │              │  │     py       │  │     py       │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │  config.py      │                        │
│                  │  (Centralized   │                        │
│                  │   Config Mgmt)  │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   python-dotenv│
                    │   (Library)    │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │     .env      │
                    │  (Your Config)│
                    └───────────────┘
                         │       │
                ┌────────┘       └────────┐
                │                         │
        ┌───────▼────────┐      ┌────────▼────────┐
        │   MySQL DB     │      │   Groq API      │
        │  - Host        │      │  - API Key      │
        │  - User        │      │  - AI Features  │
        │  - Password    │      │                 │
        │  - Database    │      │                 │
        └────────────────┘      └─────────────────┘
```

## Data Flow

### Database Connection Flow
```
Application Module (e.g., main.py)
    ↓
Calls get_db_connection()
    ↓
config.get_db_config() returns dict
    ↓
mysql.connector.connect(**config)
    ↓
Database Connection Established
```

### API Key Flow
```
AI Essay Module (ai_essay.py)
    ↓
Imports get_groq_api_key()
    ↓
config.get_groq_api_key() returns key
    ↓
GROQ_API_KEY = get_groq_api_key()
    ↓
Groq Client Initialized with Key
```

## Configuration Layers

```
┌─────────────────────────────────────────┐
│  Environment Variables (.env file)      │  ← Highest Priority
│  - DB_HOST                              │
│  - DB_USER                              │
│  - DB_PASSWORD                          │
│  - GROQ_API_KEY                         │
└─────────────────────────────────────────┘
              ↓ overrides
┌─────────────────────────────────────────┐
│  Default Values in config.py            │  ← Fallback
│  - host='localhost'                     │
│  - user='root'                          │
│  - database='cls'                       │
│  - port='3000'                          │
└─────────────────────────────────────────┘
```

## File Dependencies

```
.env ──┬────→ config.py ──┬────→ main.py
       │                 ├────→ flashcard_app.py
       │                 ├────→ essay_routes.py
       │                 ├────→ stroke_order_routes.py
       │                 ├────→ ai_essay.py
       │                 └────→ populate_db.py
       │
.gitignore ───────────────┘
(prevents .env commit)
```

## Security Model

```
┌────────────────────────────────────────────┐
│         Version Control (Git)              │
│                                            │
│  ✅ Safe Files:                            │
│  - config.py (logic only)                 │
│  - .env.example (template)                │
│  - All source code                        │
│                                            │
│  ❌ Excluded (.gitignore):                │
│  - .env (credentials)                     │
└────────────────────────────────────────────┘

Production Deployment:
┌────────────────────────────────────────────┐
│      Hosting Platform (Render, etc.)       │
│                                            │
│  Environment Variables Set in Dashboard:  │
│  - DB_HOST → Aiven MySQL endpoint         │
│  - DB_USER → avnadmin                     │
│  - DB_PASSWORD → Aiven password           │
│  - GROQ_API_KEY → Your API key           │
│  - IS_PRODUCTION → True                   │
└────────────────────────────────────────────┘
```

## Module Import Structure

```python
# Every module now imports configuration the same way:
from config import get_db_config, get_groq_api_key

# Database connections:
def get_db_connection():
    conn = mysql.connector.connect(**get_db_config())
    return conn

# API access:
GROQ_API_KEY = get_groq_api_key()
client = Groq(api_key=GROQ_API_KEY)
```

## Benefits of This Architecture

1. **Single Source of Truth**: All config in one place
2. **Separation of Concerns**: Config separate from logic
3. **Environment Flexibility**: Easy dev/staging/prod switching
4. **Security**: Credentials never in code
5. **Testability**: Mock config easily for testing
6. **Maintainability**: Change config without touching logic

---

**For detailed setup instructions**, see [CONFIGURATION.md](CONFIGURATION.md)  
**For quick start**, see [QUICK_START.md](QUICK_START.md)
