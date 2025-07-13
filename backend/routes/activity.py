"""
Activity CRUD API routes.

Provides REST endpoints for activity management.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from datetime import date
from ..dependencies import DatabaseSession
from ..models import Activity, TimeSlot, ActivityCategory, Priority
from ..schemas import ActivityCreate, ActivityUpdate, ActivityResponse, ActivitySummary
from ..services import trip_service

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate, db: DatabaseSession
) -> ActivityResponse:
    """
    Create a new activity.

    Args:
        activity_data: Activity creation data
        db: Database session

    Returns:
        Created activity object
    """
    try:
        # Create new activity instance
        db_activity = Activity(**activity_data.model_dump())
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)

        # Enrich with coordinates if address provided
        if db_activity.address:
            db_activity = await trip_service.enrich_activity_with_coordinates(
                db, db_activity
            )

        return ActivityResponse.model_validate(db_activity)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating activity: {str(e)}",
        )


@router.get("/", response_model=List[ActivitySummary])
def get_activities(
    db: DatabaseSession,
    trip_id: int = Query(None, description="Filter by trip ID"),
    activity_date: date = Query(None, description="Filter by activity date"),
    time_slot: TimeSlot = Query(None, description="Filter by time slot"),
    category: ActivityCategory = Query(None, description="Filter by category"),
    priority: Priority = Query(None, description="Filter by priority"),
    skip: int = 0,
    limit: int = 100,
) -> List[ActivitySummary]:
    """
    Get activities with optional filtering.

    Args:
        db: Database session
        trip_id: Optional trip ID filter
        activity_date: Optional date filter
        time_slot: Optional time slot filter
        category: Optional category filter
        priority: Optional priority filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of activity summaries
    """
    query = db.query(Activity)

    # Apply filters
    if trip_id:
        query = query.filter(Activity.trip_id == trip_id)
    if activity_date:
        query = query.filter(Activity.activity_date == activity_date)
    if time_slot:
        query = query.filter(Activity.time_slot == time_slot)
    if category:
        query = query.filter(Activity.category == category)
    if priority:
        query = query.filter(Activity.priority == priority)

    # Apply pagination and ordering
    activities = (
        query.order_by(Activity.activity_date, Activity.time_slot, Activity.priority)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [ActivitySummary.model_validate(activity) for activity in activities]


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: DatabaseSession) -> ActivityResponse:
    """
    Get a specific activity by ID.

    Args:
        activity_id: Activity identifier
        db: Database session

    Returns:
        Activity details
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found",
        )

    return ActivityResponse.model_validate(activity)


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int, activity_update: ActivityUpdate, db: DatabaseSession
) -> ActivityResponse:
    """
    Update an existing activity.

    Args:
        activity_id: Activity identifier
        activity_update: Updated activity data
        db: Database session

    Returns:
        Updated activity object
    """
    # Get existing activity
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found",
        )

    try:
        # Update only provided fields
        update_data = activity_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(activity, field, value)

        db.commit()
        db.refresh(activity)

        # Re-geocode if address changed
        if "address" in update_data:
            activity = await trip_service.enrich_activity_with_coordinates(db, activity)

        return ActivityResponse.model_validate(activity)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating activity: {str(e)}",
        )


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, db: DatabaseSession):
    """
    Delete an activity.

    Args:
        activity_id: Activity identifier
        db: Database session
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with id {activity_id} not found",
        )

    try:
        db.delete(activity)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting activity: {str(e)}",
        )


@router.get("/trip/{trip_id}/by-date/{activity_date}")
def get_activities_by_date(
    trip_id: int, activity_date: date, db: DatabaseSession
) -> dict:
    """
    Get activities for a specific trip and date, organized by time slot.

    Args:
        trip_id: Trip identifier
        activity_date: Date to get activities for
        db: Database session

    Returns:
        Activities organized by time slot
    """
    activities = (
        db.query(Activity)
        .filter(Activity.trip_id == trip_id, Activity.activity_date == activity_date)
        .order_by(Activity.time_slot)
        .all()
    )

    # Organize by time slot
    activities_by_slot = {"morning": [], "afternoon": [], "evening": []}

    for activity in activities:
        slot_key = activity.time_slot.value
        activities_by_slot[slot_key].append(ActivitySummary.model_validate(activity))

    return {
        "date": activity_date,
        "activities": activities_by_slot,
        "total_activities": len(activities),
        "total_estimated_cost": sum(a.estimated_cost or 0 for a in activities),
    }
