"""
Trip Pydantic schemas for request/response validation.

Defines data models for API input validation and response serialization.
"""

from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional


class TripBase(BaseModel):
    """Base trip schema with common fields."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Trip name or title"
    )

    destination: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Trip destination (city, country)",
    )

    start_date: date = Field(..., description="Trip start date")

    end_date: date = Field(..., description="Trip end date")

    accommodation_address: str = Field(
        ..., min_length=1, description="Full accommodation address"
    )

    total_budget: Optional[float] = Field(
        default=0.0, ge=0, description="Total trip budget in local currency"
    )

    @validator("end_date")
    def validate_end_date_after_start(cls, v, values):
        """Ensure end date is after start date."""
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class TripCreate(TripBase):
    """Schema for creating a new trip."""

    pass


class TripUpdate(BaseModel):
    """Schema for updating an existing trip."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Trip name or title"
    )

    destination: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Trip destination"
    )

    start_date: Optional[date] = Field(None, description="Trip start date")

    end_date: Optional[date] = Field(None, description="Trip end date")

    accommodation_address: Optional[str] = Field(
        None, min_length=1, description="Accommodation address"
    )

    total_budget: Optional[float] = Field(None, ge=0, description="Total trip budget")


class TripResponse(TripBase):
    """Schema for trip API responses."""

    id: int = Field(..., description="Trip unique identifier")

    accommodation_lat: Optional[float] = Field(
        None, ge=-90, le=90, description="Accommodation latitude coordinate"
    )

    accommodation_lon: Optional[float] = Field(
        None, ge=-180, le=180, description="Accommodation longitude coordinate"
    )

    created_at: datetime = Field(..., description="Trip creation timestamp")

    updated_at: datetime = Field(..., description="Trip last update timestamp")

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class TripSummary(BaseModel):
    """Minimal trip information for lists and summaries."""

    id: int
    name: str
    destination: str
    start_date: date
    end_date: date
    total_budget: float

    class Config:
        from_attributes = True
