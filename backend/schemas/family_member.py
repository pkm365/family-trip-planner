"""
Family Member Pydantic schemas for request/response validation.

Defines data models for family member API input validation and response serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from ..models.family_member import MemberRole


class FamilyMemberBase(BaseModel):
    """Base family member schema with common fields."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Family member name"
    )
    
    role: MemberRole = Field(
        ...,
        description="Family member role"
    )
    
    age: Optional[int] = Field(
        None,
        ge=0,
        le=120,
        description="Family member age"
    )
    
    dietary_restrictions: Optional[str] = Field(
        None,
        description="Dietary restrictions or allergies"
    )
    
    mobility_needs: Optional[str] = Field(
        None,
        description="Mobility requirements or accessibility needs"
    )
    
    interests: Optional[str] = Field(
        None,
        description="Personal interests and preferences"
    )
    
    wishlist_items: Optional[str] = Field(
        None,
        description="Must-see attractions or activities"
    )
    
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the family member"
    )


class FamilyMemberCreate(FamilyMemberBase):
    """Schema for creating a new family member."""
    
    trip_id: int = Field(
        ...,
        description="ID of the trip this family member is part of"
    )


class FamilyMemberUpdate(BaseModel):
    """Schema for updating an existing family member."""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Family member name"
    )
    
    role: Optional[MemberRole] = Field(
        None,
        description="Family member role"
    )
    
    age: Optional[int] = Field(
        None,
        ge=0,
        le=120,
        description="Age"
    )
    
    dietary_restrictions: Optional[str] = Field(
        None,
        description="Dietary restrictions"
    )
    
    mobility_needs: Optional[str] = Field(
        None,
        description="Mobility needs"
    )
    
    interests: Optional[str] = Field(
        None,
        description="Interests"
    )
    
    wishlist_items: Optional[str] = Field(
        None,
        description="Wishlist items"
    )
    
    notes: Optional[str] = Field(
        None,
        description="Notes"
    )


class FamilyMemberResponse(FamilyMemberBase):
    """Schema for family member API responses."""
    
    id: int = Field(
        ...,
        description="Family member unique identifier"
    )
    
    trip_id: int = Field(
        ...,
        description="Trip ID this family member is part of"
    )
    
    created_at: datetime = Field(
        ...,
        description="Family member creation timestamp"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Family member last update timestamp"
    )
    
    class Config:
        from_attributes = True


class FamilyMemberSummary(BaseModel):
    """Minimal family member information for lists and summaries."""
    
    id: int
    name: str
    role: MemberRole
    age: Optional[int]
    
    class Config:
        from_attributes = True


class WishlistItem(BaseModel):
    """Individual wishlist item for a family member."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Wishlist item name"
    )
    
    description: Optional[str] = Field(
        None,
        description="Item description"
    )
    
    priority: str = Field(
        default="would_like",
        description="Priority level (must_do, would_like, optional)"
    )
    
    category: Optional[str] = Field(
        None,
        description="Item category"
    )
    
    @validator("priority")
    def validate_priority(cls, v):
        """Validate priority value."""
        valid_priorities = ["must_do", "would_like", "optional"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return v


class FamilyPreferences(BaseModel):
    """Aggregated family preferences for trip planning."""
    
    total_members: int = Field(
        ...,
        description="Total number of family members"
    )
    
    age_groups: dict[str, int] = Field(
        default_factory=dict,
        description="Count of members in each age group"
    )
    
    dietary_restrictions: list[str] = Field(
        default_factory=list,
        description="All dietary restrictions across family"
    )
    
    mobility_needs: list[str] = Field(
        default_factory=list,
        description="All mobility needs across family"
    )
    
    common_interests: list[str] = Field(
        default_factory=list,
        description="Interests mentioned by multiple members"
    )
    
    all_wishlist_items: list[WishlistItem] = Field(
        default_factory=list,
        description="All wishlist items from all family members"
    )