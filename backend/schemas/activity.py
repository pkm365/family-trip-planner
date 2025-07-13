"""
Activity Pydantic schemas for request/response validation.

Defines data models for activity API input validation and response serialization.
"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from ..models.activity import TimeSlot, ActivityCategory, Priority


class ActivityBase(BaseModel):
    """Base activity schema with common fields."""

    name: str = Field(
        ..., min_length=1, max_length=200, description="Activity name or title"
    )

    description: Optional[str] = Field(
        None, description="Detailed activity description"
    )

    activity_date: date = Field(..., description="Date when activity is planned")

    time_slot: TimeSlot = Field(..., description="Time slot for the activity")

    category: ActivityCategory = Field(..., description="Activity category")

    priority: Priority = Field(
        default=Priority.WOULD_LIKE, description="Activity priority level"
    )

    location_name: Optional[str] = Field(
        None, max_length=200, description="Location or venue name"
    )

    address: Optional[str] = Field(None, description="Activity location address")

    estimated_cost: Optional[float] = Field(
        default=0.0, ge=0, description="Estimated cost for this activity"
    )

    actual_cost: Optional[float] = Field(
        None, ge=0, description="Actual cost spent on this activity"
    )

    notes: Optional[str] = Field(None, description="Additional notes or requirements")

    primary_image_url: Optional[str] = Field(
        None, max_length=1000, description="Primary image URL for the activity"
    )


class ActivityCreate(ActivityBase):
    """Schema for creating a new activity."""

    trip_id: int = Field(..., description="ID of the trip this activity belongs to")


class ActivityUpdate(BaseModel):
    """Schema for updating an existing activity."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Activity name"
    )

    description: Optional[str] = Field(None, description="Activity description")

    activity_date: Optional[date] = Field(None, description="Activity date")

    time_slot: Optional[TimeSlot] = Field(None, description="Time slot")

    category: Optional[ActivityCategory] = Field(None, description="Activity category")

    priority: Optional[Priority] = Field(None, description="Priority level")

    location_name: Optional[str] = Field(
        None, max_length=200, description="Location name"
    )

    address: Optional[str] = Field(None, description="Location address")

    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost")

    actual_cost: Optional[float] = Field(None, ge=0, description="Actual cost")

    notes: Optional[str] = Field(None, description="Notes")

    primary_image_url: Optional[str] = Field(
        None, max_length=1000, description="Primary image URL"
    )


class ActivityResponse(ActivityBase):
    """Schema for activity API responses."""

    id: int = Field(..., description="Activity unique identifier")

    trip_id: int = Field(..., description="Trip ID this activity belongs to")

    latitude: Optional[float] = Field(
        None, ge=-90, le=90, description="Activity location latitude"
    )

    longitude: Optional[float] = Field(
        None, ge=-180, le=180, description="Activity location longitude"
    )

    created_at: datetime = Field(..., description="Activity creation timestamp")

    updated_at: datetime = Field(..., description="Activity last update timestamp")

    class Config:
        from_attributes = True


class ActivitySummary(BaseModel):
    """Minimal activity information for lists and summaries."""

    id: int
    name: str
    activity_date: date
    time_slot: TimeSlot
    category: ActivityCategory
    priority: Priority
    estimated_cost: float

    class Config:
        from_attributes = True


# class DailyActivities(BaseModel):
#     """Activities grouped by date for daily planning view."""
#
#     date: date = Field(
#         ...,
#         description="Date for these activities"
#     )
#
#     morning: list["ActivitySummary"] = Field(
#         default_factory=list,
#         description="Morning activities"
#     )
#
#     afternoon: list["ActivitySummary"] = Field(
#         default_factory=list,
#         description="Afternoon activities"
#     )
#
#     evening: list["ActivitySummary"] = Field(
#         default_factory=list,
#         description="Evening activities"
#     )
#
#     total_estimated_cost: float = Field(
#         default=0.0,
#         description="Total estimated cost for the day"
#     )
