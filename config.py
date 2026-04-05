"""
Configuration Management Module for Chinese Self Learning System

This module handles loading configuration from environment variables (.env file).
All database and API configurations are centralized here.

Usage:
    from config import get_db_config, get_groq_api_key
    
    db_config = get_db_config()
    api_key = get_groq_api_key()
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_db_config() -> Dict[str, str]:
    """
    Get database configuration from environment variables
    
    Returns:
        Dictionary with database connection parameters:
        - host: Database host
        - user: Database username
        - password: Database password
        - database: Database name
    """
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_DATABASE', 'cls')
    }


def get_groq_api_key() -> str:
    """
    Get Groq API key from environment variables
    
    Returns:
        Groq API key as string, or empty string if not configured
    """
    return os.getenv('GROQ_API_KEY', '')


def get_app_config() -> Dict[str, any]:
    """
    Get application configuration from environment variables
    
    Returns:
        Dictionary with application settings:
        - host: Application host
        - port: Application port
        - is_production: Whether running in production mode
    """
    return {
        'host': os.getenv('APP_HOST', '127.0.0.1'),
        'port': int(os.getenv('APP_PORT', '3000')),
        'is_production': os.getenv('IS_PRODUCTION', 'False').lower() == 'true'
    }


# Convenience variables (for backward compatibility during migration)
DB_CONFIG = get_db_config()
GROQ_API_KEY = get_groq_api_key()
APP_CONFIG = get_app_config()
