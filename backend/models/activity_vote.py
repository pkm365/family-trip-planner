"""
Activity Vote Model

This model stores family member votes on activity recommendations.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import BaseModel


class ActivityVote(BaseModel):
    """
    Family member votes on activity recommendations.

    Each family member can vote once per activity recommendation.
    Vote types: positive (like), negative (dislike), neutral (interested but not priority).
    """

    __tablename__ = "activity_votes"

    id = Column(Integer, primary_key=True, index=True)

    # Vote Information
    vote_type = Column(String(20), nullable=False)  # positive, negative, neutral

    # Associations
    recommendation_id = Column(
        Integer, ForeignKey("activity_recommendations.id"), nullable=False, index=True
    )
    family_member_id = Column(
        Integer, ForeignKey("family_members.id"), nullable=False, index=True
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recommendation = relationship("ActivityRecommendation", back_populates="votes")
    family_member = relationship("FamilyMember", back_populates="activity_votes")

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "recommendation_id", "family_member_id", name="unique_vote_per_member"
        ),
    )

    def __repr__(self):
        return f"<ActivityVote(id={self.id}, vote_type='{self.vote_type}', recommendation_id={self.recommendation_id}, family_member_id={self.family_member_id})>"


class ActivityComment(BaseModel):
    """
    Family member comments on activity recommendations.

    Multiple comments per family member per activity are allowed.
    """

    __tablename__ = "activity_comments"

    id = Column(Integer, primary_key=True, index=True)

    # Comment Information
    comment_text = Column(String(500), nullable=False)

    # Associations
    recommendation_id = Column(
        Integer, ForeignKey("activity_recommendations.id"), nullable=False, index=True
    )
    family_member_id = Column(
        Integer, ForeignKey("family_members.id"), nullable=False, index=True
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    recommendation = relationship("ActivityRecommendation", back_populates="comments")
    family_member = relationship("FamilyMember", back_populates="activity_comments")

    def __repr__(self):
        return f"<ActivityComment(id={self.id}, recommendation_id={self.recommendation_id}, family_member_id={self.family_member_id})>"
