#!/usr/bin/env python3
"""
Development server for Family Trip Planner.

This script provides a convenient way to run the application in development mode
with hot reloading and debug features enabled.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """
    Run the development server with appropriate settings.
    
    The server will:
    - Enable hot reloading for development
    - Use debug mode for detailed error messages
    - Listen on all interfaces (0.0.0.0) for container compatibility
    - Use port 8000 by default
    """
    # Set development environment
    os.environ.setdefault("DEBUG", "True")
    
    # Configure uvicorn for development
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "backend")],
        log_level="info"
    )

if __name__ == "__main__":
    main()