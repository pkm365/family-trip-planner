"""
FastAPI dependencies for dependency injection.

Provides reusable dependencies for database sessions, authentication, etc.
"""

from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from .database import get_db
from .models import Trip


# Database session dependency
DatabaseSession = Annotated[Session, Depends(get_db)]


async def get_trip_by_id(trip_id: int, db: DatabaseSession) -> Trip:
    """
    Dependency to get a trip by ID with proper error handling.
    
    Args:
        trip_id: Trip identifier
        db: Database session
        
    Returns:
        Trip object
        
    Raises:
        HTTPException: If trip not found
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    return trip


# Trip dependency annotation
TripDependency = Annotated[Trip, Depends(get_trip_by_id)]