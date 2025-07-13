"""
Activity database model.

Represents planned activities for trips with time slots and categories.
"""

from sqlalchemy import Column, String, Date, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseModel


class TimeSlot(PyEnum):
    """Enumeration for activity time slots."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class ActivityCategory(PyEnum):
    """Enumeration for activity categories."""
    SIGHTSEEING = "sightseeing"
    FOOD = "food"
    SHOPPING = "shopping"
    REST = "rest"
    TRANSPORTATION = "transportation"


class Priority(PyEnum):
    """Enumeration for activity priority levels."""
    MUST_DO = "must_do"
    WOULD_LIKE = "would_like"
    OPTIONAL = "optional"


class Activity(BaseModel):
    """Database model for trip activities."""
    
    __tablename__ = "activitys"
    
    # Activity identification
    name = Column(
        String(200),
        nullable=False,
        doc="Activity name or title"
    )
    
    description = Column(
        Text,
        nullable=True,
        doc="Detailed activity description"
    )
    
    # Trip relationship
    trip_id = Column(
        ForeignKey("trips.id"),
        nullable=False,
        index=True,
        doc="Reference to the trip this activity belongs to"
    )
    
    # Scheduling
    activity_date = Column(
        Date,
        nullable=False,
        index=True,
        doc="Date when activity is planned"
    )
    
    time_slot = Column(
        Enum(TimeSlot),
        nullable=False,
        doc="Time slot for the activity"
    )
    
    # Categorization
    category = Column(
        Enum(ActivityCategory),
        nullable=False,
        doc="Activity category"
    )
    
    priority = Column(
        Enum(Priority),
        default=Priority.WOULD_LIKE,
        nullable=False,
        doc="Activity priority level"
    )
    
    # Location details
    location_name = Column(
        String(200),
        nullable=True,
        doc="Location or venue name"
    )
    
    address = Column(
        Text,
        nullable=True,
        doc="Activity location address"
    )
    
    latitude = Column(
        Float,
        nullable=True,
        doc="Activity location latitude"
    )
    
    longitude = Column(
        Float,
        nullable=True,
        doc="Activity location longitude"
    )
    
    # Budget
    estimated_cost = Column(
        Float,
        default=0.0,
        nullable=False,
        doc="Estimated cost for this activity"
    )
    
    actual_cost = Column(
        Float,
        nullable=True,
        doc="Actual cost spent on this activity"
    )
    
    # Notes
    notes = Column(
        Text,
        nullable=True,
        doc="Additional notes or requirements"
    )
    
    # Relationships
    trip = relationship(
        "Trip",
        back_populates="activities",
        doc="Trip this activity belongs to"
    )
    
    def __repr__(self) -> str:
        """String representation of the activity."""
        return f"<Activity(id={self.id}, name='{self.name}', date={self.activity_date})>"