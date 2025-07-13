"""
Trip database model.

Represents a family trip with destination, dates, and accommodation details.
"""

from sqlalchemy import Column, String, Date, Text, Float
from sqlalchemy.orm import relationship
from .base import BaseModel


class Trip(BaseModel):
    """Database model for family trips."""
    
    # Trip identification
    name = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Trip name or title"
    )
    
    destination = Column(
        String(100),
        nullable=False,
        doc="Trip destination (city, country)"
    )
    
    # Trip dates
    start_date = Column(
        Date,
        nullable=False,
        index=True,
        doc="Trip start date"
    )
    
    end_date = Column(
        Date,
        nullable=False,
        index=True,
        doc="Trip end date"
    )
    
    # Accommodation details
    accommodation_address = Column(
        Text,
        nullable=False,
        doc="Full accommodation address"
    )
    
    accommodation_lat = Column(
        Float,
        nullable=True,
        doc="Accommodation latitude coordinate"
    )
    
    accommodation_lon = Column(
        Float,
        nullable=True,
        doc="Accommodation longitude coordinate"
    )
    
    # Budget information
    total_budget = Column(
        Float,
        default=0.0,
        nullable=False,
        doc="Total trip budget in local currency"
    )
    
    # Relationships
    activities = relationship(
        "Activity",
        back_populates="trip",
        cascade="all, delete-orphan",
        doc="Activities planned for this trip"
    )
    
    family_members = relationship(
        "FamilyMember",
        back_populates="trip",
        cascade="all, delete-orphan",
        doc="Family members participating in this trip"
    )
    
    activity_recommendations = relationship(
        "ActivityRecommendation",
        back_populates="trip",
        cascade="all, delete-orphan",
        doc="Activity recommendations for this trip"
    )
    
    def __repr__(self) -> str:
        """String representation of the trip."""
        return f"<Trip(id={self.id}, name='{self.name}', destination='{self.destination}')>"