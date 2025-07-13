"""
Activity Vote and Comment Pydantic schemas.

Schemas for voting and commenting on activity recommendations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ActivityVoteBase(BaseModel):
    """Base schema for activity votes."""

    vote_type: str = Field(..., description="Vote type: positive, negative, neutral")

    class Config:
        # Validation for vote_type
        schema_extra = {"example": {"vote_type": "positive"}}


class ActivityVoteCreate(ActivityVoteBase):
    """Schema for creating activity votes."""

    recommendation_id: int = Field(..., description="Activity recommendation ID")
    family_member_id: int = Field(..., description="Family member ID")


class ActivityVoteUpdate(BaseModel):
    """Schema for updating activity votes."""

    vote_type: str = Field(..., description="Vote type: positive, negative, neutral")


class ActivityVoteResponse(ActivityVoteBase):
    """Schema for activity vote responses."""

    id: int = Field(..., description="Vote ID")
    recommendation_id: int = Field(..., description="Activity recommendation ID")
    family_member_id: int = Field(..., description="Family member ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ActivityCommentBase(BaseModel):
    """Base schema for activity comments."""

    comment_text: str = Field(..., description="Comment text", max_length=500)


class ActivityCommentCreate(ActivityCommentBase):
    """Schema for creating activity comments."""

    recommendation_id: int = Field(..., description="Activity recommendation ID")
    family_member_id: int = Field(..., description="Family member ID")


class ActivityCommentUpdate(BaseModel):
    """Schema for updating activity comments."""

    comment_text: str = Field(..., description="Comment text", max_length=500)


class ActivityCommentResponse(ActivityCommentBase):
    """Schema for activity comment responses."""

    id: int = Field(..., description="Comment ID")
    recommendation_id: int = Field(..., description="Activity recommendation ID")
    family_member_id: int = Field(..., description="Family member ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class FamilyMemberVoteInfo(BaseModel):
    """Schema for family member vote information."""

    family_member_id: int = Field(..., description="Family member ID")
    family_member_name: str = Field(..., description="Family member name")
    vote_type: Optional[str] = Field(None, description="Vote type if voted")
    has_voted: bool = Field(..., description="Whether family member has voted")


class RecommendationWithVotes(BaseModel):
    """Schema for recommendation with detailed vote information."""

    recommendation_id: int = Field(..., description="Recommendation ID")
    recommendation_name: str = Field(..., description="Recommendation name")
    vote_summary: dict = Field(..., description="Vote summary")
    family_votes: List[FamilyMemberVoteInfo] = Field(
        ..., description="Individual family member votes"
    )
    comments: List[ActivityCommentResponse] = Field(
        ..., description="Comments on this recommendation"
    )


class VotingDashboardResponse(BaseModel):
    """Schema for voting dashboard response."""

    trip_id: int = Field(..., description="Trip ID")
    trip_name: str = Field(..., description="Trip name")
    family_members: List[dict] = Field(..., description="Family members")
    recommendations_with_votes: List[RecommendationWithVotes] = Field(
        ..., description="Recommendations with vote details"
    )
    voting_statistics: dict = Field(..., description="Overall voting statistics")
