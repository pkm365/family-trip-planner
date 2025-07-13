"""
Activity Favorite Model

This model stores family member favorites for activity recommendations.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class ActivityFavorite(BaseModel):
    """
    Family member favorites for activity recommendations.
    
    Each family member can favorite multiple activity recommendations.
    Each recommendation can be favorited by multiple family members.
    """
    __tablename__ = "activity_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Favorite metadata
    favorite_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String(200), nullable=True)  # Optional personal notes about why they favorited it
    
    # Associations
    recommendation_id = Column(Integer, ForeignKey("activity_recommendations.id"), nullable=False, index=True)
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("ActivityRecommendation", back_populates="favorites")
    family_member = relationship("FamilyMember", back_populates="activity_favorites")
    
    # Constraints - each family member can only favorite a recommendation once
    __table_args__ = (
        UniqueConstraint('recommendation_id', 'family_member_id', name='unique_favorite_per_member'),
    )
    
    def __repr__(self):
        return f"<ActivityFavorite(id={self.id}, recommendation_id={self.recommendation_id}, family_member_id={self.family_member_id})>"