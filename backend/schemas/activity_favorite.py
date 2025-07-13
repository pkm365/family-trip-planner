"""
Activity Favorite Pydantic schemas.

Schemas for favoriting activity recommendations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ActivityFavoriteBase(BaseModel):
    """Base schema for activity favorites."""
    notes: Optional[str] = Field(None, description="Personal notes about the favorite", max_length=200)


class ActivityFavoriteCreate(ActivityFavoriteBase):
    """Schema for creating activity favorites."""
    recommendation_id: int = Field(..., description="Activity recommendation ID")
    family_member_id: int = Field(..., description="Family member ID")


class ActivityFavoriteUpdate(BaseModel):
    """Schema for updating activity favorites."""
    notes: Optional[str] = Field(None, description="Personal notes about the favorite", max_length=200)


class ActivityFavoriteResponse(ActivityFavoriteBase):
    """Schema for activity favorite responses."""
    id: int = Field(..., description="Favorite ID")
    recommendation_id: int = Field(..., description="Activity recommendation ID")
    family_member_id: int = Field(..., description="Family member ID")
    favorite_date: datetime = Field(..., description="When the activity was favorited")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class FamilyMemberFavoriteInfo(BaseModel):
    """Schema for family member favorite information."""
    family_member_id: int = Field(..., description="Family member ID")
    family_member_name: str = Field(..., description="Family member name")
    has_favorited: bool = Field(..., description="Whether family member has favorited this")
    favorite_date: Optional[datetime] = Field(None, description="When they favorited it")
    notes: Optional[str] = Field(None, description="Their personal notes")


class RecommendationWithFavorites(BaseModel):
    """Schema for recommendation with detailed favorite information."""
    recommendation_id: int = Field(..., description="Recommendation ID")
    recommendation_name: str = Field(..., description="Recommendation name")
    total_favorites: int = Field(..., description="Total number of favorites")
    family_favorites: List[FamilyMemberFavoriteInfo] = Field(..., description="Individual family member favorites")


class FavoritesDashboardResponse(BaseModel):
    """Schema for favorites dashboard response."""
    trip_id: int = Field(..., description="Trip ID")
    trip_name: str = Field(..., description="Trip name")
    family_members: List[dict] = Field(..., description="Family members")
    recommendations_with_favorites: List[RecommendationWithFavorites] = Field(..., description="Recommendations with favorite details")
    favorite_statistics: dict = Field(..., description="Overall favorite statistics")


class FavoritesListResponse(BaseModel):
    """Schema for user's favorites list."""
    favorites: List[ActivityFavoriteResponse] = Field(..., description="List of favorites")
    recommendations: List[dict] = Field(..., description="Full recommendation details for favorited items")
    total_count: int = Field(..., description="Total number of favorites")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")