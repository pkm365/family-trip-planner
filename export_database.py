#!/usr/bin/env python3
"""
Export database content to SQL for easy deployment.
This script creates a SQL dump that can be used to restore the database.
"""

import sqlite3
import sys
import os

def export_database():
    """Export the database to SQL format."""
    
    db_path = "trip_planner.db"
    export_path = "database_export.sql"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Create SQL dump
        with open(export_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        
        conn.close()
        
        print(f"Database exported to {export_path}")
        print(f"File size: {os.path.getsize(export_path)} bytes")
        return True
        
    except Exception as e:
        print(f"Error exporting database: {e}")
        return False

if __name__ == "__main__":
    export_database()