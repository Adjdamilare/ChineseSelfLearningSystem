#!/usr/bin/env python3
"""
Test script for Chinese Self Learning System
"""

import mysql.connector
import bcrypt
import secrets
from main import get_db_connection, create_tables

def test_database_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_user_creation():
    """Test user creation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test user creation
        username = "testuser"
        email = "test@example.com"
        password = "testpassword"
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✓ Test user already exists")
        else:
            # Insert test user
            cursor.execute(
                "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()
            print("✓ Test user created successfully")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        return False

def test_word_search():
    """Test word search functionality"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test if words table exists and has data
        cursor.execute("SHOW TABLES LIKE 'words'")
        words_table = cursor.fetchone()
        
        if not words_table:
            print("✗ Words table does not exist")
            return False
        
        # Test search query
        cursor.execute("""
            SELECT level, hanzi, pinyin, pinyin_tone, pinyin_num, english, pos, tts_url
            FROM words 
            WHERE (hanzi LIKE %s OR pinyin LIKE %s OR english LIKE %s)
            ORDER BY level, hanzi LIMIT 5
        """, ("%test%", "%test%", "%test%"))
        
        words = cursor.fetchall()
        print(f"✓ Word search test completed. Found {len(words)} results for 'test'")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Word search test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Chinese Self Learning System...")
    print("=" * 50)
    
    # Test database connection
    db_ok = test_database_connection()
    print()
    
    # Test user creation
    user_ok = test_user_creation()
    print()
    
    # Test word search
    search_ok = test_word_search()
    print()
    
    # Summary
    print("=" * 50)
    if db_ok and user_ok and search_ok:
        print("✓ All tests passed! The application should work correctly.")
        print("You can now access the application at: http://127.0.0.1:3000")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()