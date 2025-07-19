#!/usr/bin/env python3
"""
Production server for Family Trip Planner.

This script provides a production-ready way to run the application
without development features like hot reloading.
"""

import os
import sys
import uvicorn
import sqlite3
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def import_database_if_needed():
    """Import database from SQL export if database doesn't exist."""
    db_path = Path("./data/trip_planner.db")
    sql_export_path = Path("./database_export.sql")
    
    # Create data directory if it doesn't exist
    db_path.parent.mkdir(exist_ok=True)
    
    # If database doesn't exist but SQL export does, import it
    if not db_path.exists() and sql_export_path.exists():
        print(f"Database not found. Importing from {sql_export_path}...")
        try:
            conn = sqlite3.connect(str(db_path))
            with open(sql_export_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            conn.executescript(sql_content)
            conn.close()
            print("Database imported successfully!")
        except Exception as e:
            print(f"Error importing database: {e}")
            # Continue anyway - the app will create tables automatically
    elif db_path.exists():
        print(f"Database found at {db_path}")
    else:
        print("No existing database or export found. Will create new database.")


def main():
    """
    Run the production server.

    The server will:
    - Run in production mode (no reload)
    - Use optimized settings for production
    - Listen on all interfaces (0.0.0.0) for container compatibility
    - Use port 8000
    """
    # Import database if needed (for production deployment)
    import_database_if_needed()
    
    # Force production environment
    os.environ["DEBUG"] = "False"
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    # Get port from environment or default to 8000
    # Try multiple port environment variables that different platforms use
    port = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", 8000)))
    
    print(f"Starting production server on port {port}...")
    
    # Configure uvicorn for production
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # No reload in production
        log_level="info",
        access_log=True,
        workers=1,  # Single worker for SQLite compatibility
        loop="asyncio",  # Explicit event loop
    )


if __name__ == "__main__":
    main()