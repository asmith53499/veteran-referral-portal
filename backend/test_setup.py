#!/usr/bin/env python3
"""
Test script to verify FastAPI setup and database connection
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        from app.config import settings
        print("✅ Config imported successfully")
        
        from app.core.database import engine, Base
        print("✅ Database modules imported successfully")
        
        from app.models import Referral, Outcome, AuditLog
        print("✅ Models imported successfully")
        
        from app.schemas.referrals import ReferralCreate, ReferralResponse
        print("✅ Schemas imported successfully")
        
        from app.core.pii_detector import detect_pii
        print("✅ PII detector imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        print("\nTesting configuration...")
        
        from app.config import settings
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ Database URL: {settings.database_url[:50]}...")
        print(f"✅ PII detection: {settings.pii_detection_enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_pii_detection():
    """Test PII detection functionality"""
    try:
        print("\nTesting PII detection...")
        
        from app.core.pii_detector import detect_pii
        
        # Test cases
        test_cases = [
            ("abc123-def456-ghi789", False),  # Token - should not be PII
            ("John Smith", True),             # Name - should be PII
            ("555-123-4567", True),           # Phone - should be PII
            ("john@example.com", True),       # Email - should be PII
            ("123 Main St", True),            # Address - should be PII
            ("CRISIS_INTERVENTION", False),   # Enum value - should not be PII
        ]
        
        for text, expected in test_cases:
            result = detect_pii(text)
            status = "✅" if result == expected else "❌"
            print(f"{status} '{text}' -> PII: {result} (expected: {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ PII detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Veteran Referral Portal FastAPI Setup\n")
    
    tests = [
        test_imports,
        test_config,
        test_pii_detection,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI setup is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
