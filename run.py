#!/usr/bin/env python3
"""
Development server for Family Trip Planner.

This script provides a convenient way to run the application in development mode
with hot reloading and debug features enabled.
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
    Run the development server with appropriate settings.

    The server will:
    - Enable hot reloading for development
    - Use debug mode for detailed error messages
    - Listen on all interfaces (0.0.0.0) for container compatibility
    - Use port 8000 by default
    """
    # Import database if needed (for production deployment)
    import_database_if_needed()
    
    # Set development environment
    os.environ.setdefault("DEBUG", "True")

    # Configure uvicorn for development
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "backend")],
        log_level="info",
    )


if __name__ == "__main__":
    main()
