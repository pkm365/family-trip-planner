"""
Family Member database model.

Represents family members participating in trips with preferences.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import BaseModel


class MemberRole(PyEnum):
    """Enumeration for family member roles."""
    PARENT = "parent"
    CHILD = "child"
    ADULT = "adult"


class FamilyMember(BaseModel):
    """Database model for family members."""
    
    # Member identification
    name = Column(
        String(100),
        nullable=False,
        doc="Family member name"
    )
    
    role = Column(
        Enum(MemberRole),
        nullable=False,
        doc="Family member role"
    )
    
    age = Column(
        Integer,
        nullable=True,
        doc="Family member age (optional)"
    )
    
    # Trip relationship
    trip_id = Column(
        ForeignKey("trips.id"),
        nullable=False,
        index=True,
        doc="Reference to the trip this member is part of"
    )
    
    # Preferences
    dietary_restrictions = Column(
        Text,
        nullable=True,
        doc="Dietary restrictions or allergies"
    )
    
    mobility_needs = Column(
        Text,
        nullable=True,
        doc="Mobility requirements or accessibility needs"
    )
    
    interests = Column(
        Text,
        nullable=True,
        doc="Personal interests and preferences"
    )
    
    wishlist_items = Column(
        Text,
        nullable=True,
        doc="Must-see attractions or activities (JSON format)"
    )
    
    # Notes
    notes = Column(
        Text,
        nullable=True,
        doc="Additional notes about the family member"
    )
    
    # Relationships
    trip = relationship(
        "Trip",
        back_populates="family_members",
        doc="Trip this family member is part of"
    )
    
    activity_votes = relationship(
        "ActivityVote",
        back_populates="family_member",
        cascade="all, delete-orphan",
        doc="Votes cast by this family member on activity recommendations"
    )
    
    activity_comments = relationship(
        "ActivityComment",
        back_populates="family_member",
        cascade="all, delete-orphan",
        doc="Comments made by this family member on activity recommendations"
    )
    
    activity_favorites = relationship(
        "ActivityFavorite",
        back_populates="family_member",
        cascade="all, delete-orphan",
        doc="Activities favorited by this family member"
    )
    
    def __repr__(self) -> str:
        """String representation of the family member."""
        return f"<FamilyMember(id={self.id}, name='{self.name}', role={self.role.value})>"