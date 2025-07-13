"""
Activity Recommendation Model

This model stores activity suggestions discovered through search APIs,
along with their metadata for the family voting system.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class ActivityRecommendation(BaseModel):
    """
    Activity recommendations from search APIs for family voting.
    
    These are potential activities that haven't been scheduled yet,
    but are being considered by the family through the voting system.
    """
    __tablename__ = "activity_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)  # sightseeing, food, shopping, etc.
    
    # Location Information
    location_name = Column(String(200), nullable=True)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # External Data
    external_id = Column(String(100), nullable=True, index=True)  # Google Places ID, TripAdvisor ID, etc.
    external_source = Column(String(50), nullable=True)  # 'google_places', 'tripadvisor', etc.
    external_rating = Column(Float, nullable=True)  # Rating from external source
    external_review_count = Column(Integer, nullable=True)
    
    # Recommendation Metadata
    estimated_cost = Column(Float, default=0.0)
    estimated_duration_hours = Column(Float, nullable=True)
    difficulty_level = Column(String(20), nullable=True)  # easy, moderate, challenging
    age_appropriate = Column(String(50), nullable=True)  # all_ages, adults_only, families, etc.
    
    # Media
    primary_image_url = Column(String(500), nullable=True)
    image_urls = Column(Text, nullable=True)  # JSON array of additional image URLs
    
    # Trip Association
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    
    # Discovery Information
    search_query = Column(String(200), nullable=True)  # What search led to this recommendation
    discovery_date = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)  # Can be deactivated if no longer relevant
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trip = relationship("Trip", back_populates="activity_recommendations")
    votes = relationship("ActivityVote", back_populates="recommendation", cascade="all, delete-orphan")
    comments = relationship("ActivityComment", back_populates="recommendation", cascade="all, delete-orphan")
    favorites = relationship("ActivityFavorite", back_populates="recommendation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ActivityRecommendation(id={self.id}, name='{self.name}', trip_id={self.trip_id})>"
    
    @property
    def vote_summary(self):
        """Get vote summary for this recommendation."""
        if not self.votes:
            return {"total": 0, "positive": 0, "negative": 0, "score": 0}
        
        positive = sum(1 for vote in self.votes if vote.vote_type == "positive")
        negative = sum(1 for vote in self.votes if vote.vote_type == "negative")
        total = len(self.votes)
        score = positive - negative
        
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "score": score
        }
    
    @property
    def popularity_score(self):
        """Calculate popularity score based on votes and external rating."""
        vote_score = self.vote_summary["score"]
        external_score = (self.external_rating or 0) * 0.2  # Weight external rating less
        return vote_score + external_score