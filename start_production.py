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
    
    # Check if database needs to be imported
    should_import = False
    
    if not db_path.exists():
        print("Database not found.")
        should_import = True
    else:
        # Check if database is empty (size < 100KB means likely empty/minimal)
        db_size = db_path.stat().st_size
        print(f"Database found at {db_path}, size: {db_size} bytes")
        if db_size < 100000:  # Less than 100KB, probably empty
            print("Database appears empty, will re-import.")
            should_import = True
    
    # Import database if needed and SQL export exists
    if should_import and sql_export_path.exists():
        print(f"Importing database from {sql_export_path}...")
        try:
            # Remove existing database if it exists
            if db_path.exists():
                db_path.unlink()
                
            conn = sqlite3.connect(str(db_path))
            with open(sql_export_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            conn.executescript(sql_content)
            conn.close()
            print("Database imported successfully!")
            
            # Verify import worked
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trips")
            trip_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM activity_recommendations") 
            activity_count = cursor.fetchone()[0]
            conn.close()
            print(f"Verified: {trip_count} trips and {activity_count} activities imported")
            
        except Exception as e:
            print(f"Error importing database: {e}")
            # Continue anyway - the app will create tables automatically
    elif not sql_export_path.exists():
        print("No SQL export file found. Will create new database.")


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