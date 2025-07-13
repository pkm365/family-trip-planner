"""
Pydantic schemas package.

Exports all request/response validation schemas for easy importing.
"""

from .trip import TripBase, TripCreate, TripUpdate, TripResponse, TripSummary

from .activity import (
    ActivityBase,
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivitySummary,
    # DailyActivities
)

from .family_member import (
    FamilyMemberBase,
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
    FamilyMemberSummary,
    WishlistItem,
    FamilyPreferences,
)

__all__ = [
    # Trip schemas
    "TripBase",
    "TripCreate",
    "TripUpdate",
    "TripResponse",
    "TripSummary",
    # Activity schemas
    "ActivityBase",
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    "ActivitySummary",
    # "DailyActivities",
    # Family member schemas
    "FamilyMemberBase",
    "FamilyMemberCreate",
    "FamilyMemberUpdate",
    "FamilyMemberResponse",
    "FamilyMemberSummary",
    "WishlistItem",
    "FamilyPreferences",
]
