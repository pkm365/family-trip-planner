"""
Activity Recommendation Pydantic schemas.

Schemas for activity recommendations including voting and search functionality.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class ActivityRecommendationBase(BaseModel):
    """Base schema for activity recommendations."""
    name: str = Field(..., description="Activity name", max_length=200)
    description: Optional[str] = Field(None, description="Activity description")
    category: str = Field(..., description="Activity category")
    location_name: Optional[str] = Field(None, description="Location name", max_length=200)
    address: Optional[str] = Field(None, description="Full address", max_length=500)
    latitude: Optional[float] = Field(None, description="Latitude coordinate", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude coordinate", ge=-180, le=180)
    external_id: Optional[str] = Field(None, description="External service ID", max_length=100)
    external_source: Optional[str] = Field(None, description="External service name", max_length=50)
    external_rating: Optional[float] = Field(None, description="External rating", ge=0, le=5)
    external_review_count: Optional[int] = Field(None, description="Number of external reviews", ge=0)
    estimated_cost: float = Field(0.0, description="Estimated cost", ge=0)
    estimated_duration_hours: Optional[float] = Field(None, description="Estimated duration in hours", ge=0)
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    age_appropriate: Optional[str] = Field(None, description="Age appropriateness")
    primary_image_url: Optional[str] = Field(None, description="Primary image URL")
    image_urls: Optional[str] = Field(None, description="Additional image URLs as JSON")
    search_query: Optional[str] = Field(None, description="Search query that found this recommendation")


class ActivityRecommendationCreate(ActivityRecommendationBase):
    """Schema for creating activity recommendations."""
    trip_id: int = Field(..., description="Trip ID")


class ActivityRecommendationUpdate(BaseModel):
    """Schema for updating activity recommendations."""
    name: Optional[str] = Field(None, description="Activity name", max_length=200)
    description: Optional[str] = Field(None, description="Activity description")
    category: Optional[str] = Field(None, description="Activity category")
    location_name: Optional[str] = Field(None, description="Location name", max_length=200)
    address: Optional[str] = Field(None, description="Full address", max_length=500)
    latitude: Optional[float] = Field(None, description="Latitude coordinate", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Longitude coordinate", ge=-180, le=180)
    estimated_cost: Optional[float] = Field(None, description="Estimated cost", ge=0)
    estimated_duration_hours: Optional[float] = Field(None, description="Estimated duration in hours", ge=0)
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    age_appropriate: Optional[str] = Field(None, description="Age appropriateness")
    primary_image_url: Optional[str] = Field(None, description="Primary image URL")
    image_urls: Optional[str] = Field(None, description="Additional image URLs as JSON")
    is_active: Optional[bool] = Field(None, description="Whether recommendation is active")


class VoteSummary(BaseModel):
    """Vote summary for a recommendation."""
    total: int = Field(..., description="Total number of votes")
    positive: int = Field(..., description="Number of positive votes")
    negative: int = Field(..., description="Number of negative votes")
    score: int = Field(..., description="Vote score (positive - negative)")


class ActivityRecommendationResponse(ActivityRecommendationBase):
    """Schema for activity recommendation responses."""
    id: int = Field(..., description="Recommendation ID")
    trip_id: int = Field(..., description="Trip ID")
    discovery_date: datetime = Field(..., description="When recommendation was discovered")
    is_active: bool = Field(..., description="Whether recommendation is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    vote_summary: VoteSummary = Field(..., description="Vote summary")
    popularity_score: float = Field(..., description="Popularity score")
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Schema for activity search requests."""
    query: str = Field(..., description="Search query", max_length=200)
    trip_id: int = Field(..., description="Trip ID for context")
    category: Optional[str] = Field(None, description="Filter by category")
    budget_min: Optional[float] = Field(None, description="Minimum budget", ge=0)
    budget_max: Optional[float] = Field(None, description="Maximum budget", ge=0)
    radius_km: Optional[float] = Field(5.0, description="Search radius in kilometers", ge=0.1, le=50)
    limit: Optional[int] = Field(20, description="Maximum number of results", ge=1, le=50)


class SearchResponse(BaseModel):
    """Schema for search responses."""
    recommendations: List[ActivityRecommendationResponse] = Field(..., description="Found recommendations")
    total_count: int = Field(..., description="Total number of results")
    search_metadata: Dict[str, Any] = Field(..., description="Search metadata")


class ActivityRecommendationListResponse(BaseModel):
    """Schema for paginated activity recommendation lists."""
    recommendations: List[ActivityRecommendationResponse] = Field(..., description="List of recommendations")
    total_count: int = Field(..., description="Total number of recommendations")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")