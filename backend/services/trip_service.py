"""
Trip business logic service.

Provides high-level business operations for trip management.
"""

import logging
from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from ..models import Trip, Activity, FamilyMember, TimeSlot
from ..schemas import ActivitySummary, FamilyPreferences
from .geocoding_service import geocoding_service
from .weather_service import weather_service

logger = logging.getLogger(__name__)


class TripService:
    """Service for trip-related business logic."""

    @staticmethod
    async def enrich_trip_with_coordinates(db: Session, trip: Trip) -> Trip:
        """
        Geocode trip accommodation address and update coordinates.

        Args:
            db: Database session
            trip: Trip object to enrich

        Returns:
            Updated trip object with coordinates
        """
        if not trip.accommodation_lat or not trip.accommodation_lon:
            if trip.accommodation_address:
                lat, lon = await geocoding_service.geocode_address(
                    trip.accommodation_address
                )

                if lat != 0.0 and lon != 0.0:
                    trip.accommodation_lat = lat
                    trip.accommodation_lon = lon
                    db.commit()
                    logger.info(
                        f"Updated trip {trip.id} with coordinates ({lat}, {lon})"
                    )

        return trip

    @staticmethod
    async def enrich_activity_with_coordinates(
        db: Session, activity: Activity
    ) -> Activity:
        """
        Geocode activity address and update coordinates.
        Falls back to location_name if address is not provided.

        Args:
            db: Database session
            activity: Activity object to enrich

        Returns:
            Updated activity object with coordinates
        """
        if not activity.latitude or not activity.longitude:
            # Try geocoding with address first, then fall back to location_name
            geocoded = False
            
            # First try address if available
            if activity.address and activity.address.strip():
                lat, lon = await geocoding_service.geocode_address(activity.address)
                if lat != 0.0 and lon != 0.0:
                    activity.latitude = lat
                    activity.longitude = lon
                    geocoded = True
                    logger.info(
                        f"Updated activity {activity.id} with coordinates ({lat}, {lon}) from address: '{activity.address}'"
                    )
            
            # If address failed, try location_name BUT KEEP the original address
            if not geocoded and activity.location_name and activity.location_name.strip():
                lat, lon = await geocoding_service.geocode_address(activity.location_name)
                if lat != 0.0 and lon != 0.0:
                    activity.latitude = lat
                    activity.longitude = lon
                    geocoded = True
                    # KEEP the original address for display - don't clear it
                    logger.info(
                        f"Updated activity {activity.id} with coordinates ({lat}, {lon}) from location_name: '{activity.location_name}' (kept original address for display)"
                    )
            
            if geocoded:
                db.commit()
            else:
                logger.warning(
                    f"Failed to geocode activity {activity.id}. Address: '{activity.address}', Location: '{activity.location_name}'"
                )

        return activity

    @staticmethod
    def get_trip_dates(trip: Trip) -> List[date]:
        """
        Get all dates in the trip duration.

        Args:
            trip: Trip object

        Returns:
            List of dates from start to end of trip
        """
        dates = []
        current_date = trip.start_date

        while current_date <= trip.end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        return dates

    @staticmethod
    def get_daily_activities(db: Session, trip_id: int) -> List[Dict]:
        """
        Get activities organized by date and time slot.

        Args:
            db: Database session
            trip_id: Trip identifier

        Returns:
            List of daily activities dictionaries
        """
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            return []

        # Get all activities for the trip
        activities = (
            db.query(Activity)
            .filter(Activity.trip_id == trip_id)
            .order_by(Activity.activity_date, Activity.time_slot)
            .all()
        )

        # Organize by date
        activities_by_date = {}
        for activity in activities:
            date_key = activity.activity_date
            if date_key not in activities_by_date:
                activities_by_date[date_key] = {
                    TimeSlot.MORNING: [],
                    TimeSlot.AFTERNOON: [],
                    TimeSlot.EVENING: [],
                }

            activities_by_date[date_key][activity.time_slot].append(
                ActivitySummary.from_orm(activity)
            )

        # Create daily activities dictionaries for all trip dates
        daily_activities = []
        for trip_date in TripService.get_trip_dates(trip):
            date_activities = activities_by_date.get(
                trip_date,
                {TimeSlot.MORNING: [], TimeSlot.AFTERNOON: [], TimeSlot.EVENING: []},
            )

            # Calculate total estimated cost for the day
            total_cost = 0.0
            for time_slot_activities in date_activities.values():
                for activity in time_slot_activities:
                    total_cost += activity.estimated_cost or 0.0

            daily_activities.append(
                {
                    "date": trip_date,
                    "morning": date_activities.get(TimeSlot.MORNING, []),
                    "afternoon": date_activities.get(TimeSlot.AFTERNOON, []),
                    "evening": date_activities.get(TimeSlot.EVENING, []),
                    "total_estimated_cost": total_cost,
                }
            )

        return daily_activities

    @staticmethod
    def get_family_preferences(db: Session, trip_id: int) -> FamilyPreferences:
        """
        Aggregate family preferences for trip planning.

        Args:
            db: Database session
            trip_id: Trip identifier

        Returns:
            FamilyPreferences object with aggregated data
        """
        family_members = (
            db.query(FamilyMember).filter(FamilyMember.trip_id == trip_id).all()
        )

        if not family_members:
            return FamilyPreferences(total_members=0)

        # Analyze age groups
        age_groups = {"children": 0, "adults": 0, "seniors": 0}
        dietary_restrictions = []
        mobility_needs = []
        all_interests = []

        for member in family_members:
            # Categorize by age
            if member.age:
                if member.age < 18:
                    age_groups["children"] += 1
                elif member.age < 65:
                    age_groups["adults"] += 1
                else:
                    age_groups["seniors"] += 1

            # Collect dietary restrictions
            if member.dietary_restrictions:
                dietary_restrictions.extend(
                    [
                        restriction.strip()
                        for restriction in member.dietary_restrictions.split(",")
                        if restriction.strip()
                    ]
                )

            # Collect mobility needs
            if member.mobility_needs:
                mobility_needs.extend(
                    [
                        need.strip()
                        for need in member.mobility_needs.split(",")
                        if need.strip()
                    ]
                )

            # Collect interests
            if member.interests:
                all_interests.extend(
                    [
                        interest.strip()
                        for interest in member.interests.split(",")
                        if interest.strip()
                    ]
                )

        # Find common interests (mentioned by more than one person)
        interest_counts = {}
        for interest in all_interests:
            interest_counts[interest] = interest_counts.get(interest, 0) + 1

        common_interests = [
            interest for interest, count in interest_counts.items() if count > 1
        ]

        return FamilyPreferences(
            total_members=len(family_members),
            age_groups=age_groups,
            dietary_restrictions=list(set(dietary_restrictions)),
            mobility_needs=list(set(mobility_needs)),
            common_interests=common_interests,
        )

    @staticmethod
    async def get_trip_weather_forecast(trip: Trip) -> Dict:
        """
        Get weather forecast for trip location and duration.

        Args:
            trip: Trip object with coordinates

        Returns:
            Dictionary with weather forecast data
        """
        if not trip.accommodation_lat or not trip.accommodation_lon:
            logger.warning(f"No coordinates available for trip {trip.id}")
            return {}

        try:
            # Get current weather
            current_weather = await weather_service.get_current_weather(
                trip.accommodation_lat, trip.accommodation_lon
            )

            # Get forecast
            forecast_data = await weather_service.get_weather_forecast(
                trip.accommodation_lat,
                trip.accommodation_lon,
                days=min(7, (trip.end_date - trip.start_date).days + 1),
            )

            # Format daily forecasts
            daily_forecasts = weather_service.get_daily_forecasts(forecast_data)

            return {
                "current": weather_service.format_weather_summary(current_weather),
                "daily_forecasts": daily_forecasts,
                "location": {
                    "latitude": trip.accommodation_lat,
                    "longitude": trip.accommodation_lon,
                    "city": trip.destination,
                },
            }

        except Exception as e:
            logger.error(f"Error getting weather forecast for trip {trip.id}: {e}")
            return {}


# Global service instance
trip_service = TripService()
