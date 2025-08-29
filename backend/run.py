#!/usr/bin/env python3
"""
Run script for the Veteran Referral Portal FastAPI application
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def main():
    """Start the FastAPI application"""
    
    # Set environment variables for development
    os.environ.setdefault("DEBUG", "true")
    
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Use the RDS endpoint from our infrastructure
        database_url = "postgresql://vrp_admin:DHs3638AVE_0k<b+ax!ATom+dLYhPh8I@vrp-dev-postgres.cfweqeqc2w2k.us-east-1.rds.amazonaws.com:5432/veteran_referral_portal"
        os.environ["DATABASE_URL"] = database_url
    
    print("🚀 Starting Veteran Referral Portal FastAPI Application")
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print(f"🔧 Debug mode: {os.getenv('DEBUG', 'false')}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"❤️  Health: http://localhost:8000/health")
    print()
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
