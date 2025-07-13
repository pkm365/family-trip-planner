"""
Trip CRUD API routes.

Provides REST endpoints for trip management.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import DatabaseSession, TripDependency
from ..models import Trip
from ..schemas import TripCreate, TripUpdate, TripResponse, TripSummary
from ..services import trip_service

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(trip_data: TripCreate, db: DatabaseSession) -> TripResponse:
    """
    Create a new trip.
    
    Args:
        trip_data: Trip creation data
        db: Database session
        
    Returns:
        Created trip object
    """
    try:
        # Create new trip instance
        db_trip = Trip(**trip_data.model_dump())
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        
        # Enrich with coordinates if address provided
        if db_trip.accommodation_address:
            db_trip = await trip_service.enrich_trip_with_coordinates(db, db_trip)
        
        return TripResponse.model_validate(db_trip)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating trip: {str(e)}"
        )


@router.get("/", response_model=List[TripSummary])
def get_trips(db: DatabaseSession, skip: int = 0, limit: int = 100) -> List[TripSummary]:
    """
    Get all trips with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of trip summaries
    """
    trips = db.query(Trip).offset(skip).limit(limit).all()
    return [TripSummary.model_validate(trip) for trip in trips]


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip: TripDependency) -> TripResponse:
    """
    Get a specific trip by ID.
    
    Args:
        trip: Trip object from dependency
        
    Returns:
        Trip details
    """
    return TripResponse.model_validate(trip)


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: int,
    trip_update: TripUpdate,
    trip: TripDependency,
    db: DatabaseSession
) -> TripResponse:
    """
    Update an existing trip.
    
    Args:
        trip_id: Trip identifier
        trip_update: Updated trip data
        trip: Current trip object
        db: Database session
        
    Returns:
        Updated trip object
    """
    try:
        # Update only provided fields
        update_data = trip_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(trip, field, value)
        
        db.commit()
        db.refresh(trip)
        
        # Re-geocode if accommodation address changed
        if "accommodation_address" in update_data:
            trip = await trip_service.enrich_trip_with_coordinates(db, trip)
        
        return TripResponse.model_validate(trip)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating trip: {str(e)}"
        )


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, trip: TripDependency, db: DatabaseSession):
    """
    Delete a trip.
    
    Args:
        trip_id: Trip identifier
        trip: Trip object from dependency
        db: Database session
    """
    try:
        db.delete(trip)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting trip: {str(e)}"
        )


@router.get("/{trip_id}/daily-activities")
def get_trip_daily_activities(trip_id: int, db: DatabaseSession):
    """
    Get daily activities for a trip.
    
    Args:
        trip_id: Trip identifier
        db: Database session
        
    Returns:
        Daily activities organized by date and time slot
    """
    return trip_service.get_daily_activities(db, trip_id)


@router.get("/{trip_id}/weather")
async def get_trip_weather(trip: TripDependency):
    """
    Get weather forecast for trip location.
    
    Args:
        trip: Trip object from dependency
        
    Returns:
        Weather forecast data
    """
    weather_data = await trip_service.get_trip_weather_forecast(trip)
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather data temporarily unavailable"
        )
    
    return weather_data


@router.get("/{trip_id}/daily-activities")
def get_trip_daily_activities(trip_id: int, db: DatabaseSession):
    """
    Get activities organized by date for daily planning view.
    
    Args:
        trip_id: Trip identifier
        db: Database session
        
    Returns:
        Activities organized by date and time slot
    """
    from ..models import Activity
    from sqlalchemy import and_
    from collections import defaultdict
    
    # Get all activities for this trip, ordered by date and time slot
    activities = db.query(Activity).filter(
        Activity.trip_id == trip_id
    ).order_by(
        Activity.activity_date,
        Activity.time_slot
    ).all()
    
    # Group activities by date
    daily_activities = defaultdict(lambda: {
        'morning': [],
        'afternoon': [],
        'evening': [],
        'total_estimated_cost': 0
    })
    
    for activity in activities:
        date_str = activity.activity_date.isoformat()
        slot = activity.time_slot.value if hasattr(activity.time_slot, 'value') else activity.time_slot
        
        activity_data = {
            'id': activity.id,
            'name': activity.name,
            'category': activity.category.value if hasattr(activity.category, 'value') else activity.category,
            'priority': activity.priority.value if hasattr(activity.priority, 'value') else activity.priority,
            'estimated_cost': activity.estimated_cost or 0,
            'activity_date': date_str,
            'time_slot': slot
        }
        
        daily_activities[date_str][slot].append(activity_data)
        daily_activities[date_str]['total_estimated_cost'] += activity.estimated_cost or 0
    
    # Convert to list format expected by frontend
    result = []
    for date_str, day_data in daily_activities.items():
        result.append({
            'date': date_str,
            'morning': day_data['morning'],
            'afternoon': day_data['afternoon'],
            'evening': day_data['evening'],
            'total_estimated_cost': day_data['total_estimated_cost']
        })
    
    # Sort by date
    result.sort(key=lambda x: x['date'])
    
    return result


@router.get("/{trip_id}/family-preferences")
def get_trip_family_preferences(trip_id: int, db: DatabaseSession):
    """
    Get aggregated family preferences for trip planning.
    
    Args:
        trip_id: Trip identifier
        db: Database session
        
    Returns:
        Family preferences summary
    """
    return trip_service.get_family_preferences(db, trip_id)