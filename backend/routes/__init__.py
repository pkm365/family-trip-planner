"""
API routes package.

Exports all route routers for easy importing.
"""

from .trip import router as trip_router
from .activity import router as activity_router
from .family_member import router as family_member_router
from .weather import router as weather_router
from .geocoding import router as geocoding_router

__all__ = [
    "trip_router",
    "activity_router",
    "family_member_router",
    "weather_router",
    "geocoding_router",
]
