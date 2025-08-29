#!/usr/bin/env python3
"""
Test database connection
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_db_connection():
    """Test database connection"""
    try:
        print("Testing database connection...")
        
        from app.core.database import engine
        print("✅ Engine created successfully")
        
        from sqlalchemy import text
        print("✅ SQLAlchemy text imported")
        
        with engine.connect() as conn:
            print("✅ Database connection established")
            result = conn.execute(text("SELECT 1"))
            print("✅ Query executed successfully:", result.fetchone())
            
        print("🎉 Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_db_connection()
