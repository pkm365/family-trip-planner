"""
Test configuration and fixtures for Family Trip Planner.

Provides common test fixtures and setup for pytest.
"""

import pytest
import asyncio
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock

# Import app components
from backend.main import app
from backend.database import get_db
from backend.models.base import Base
from backend.models import Trip, Activity, FamilyMember, TimeSlot, ActivityCategory, Priority, MemberRole


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_trip_planner.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    
    Yields:
        Session: SQLAlchemy database session
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database dependency override.
    
    Args:
        db_session: Database session fixture
        
    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_trip(db_session):
    """
    Create a sample trip for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Trip: Sample trip object
    """
    trip = Trip(
        name="Osaka Family Trip",
        destination="Osaka, Japan",
        start_date=date(2025, 7, 27),
        end_date=date(2025, 8, 2),
        accommodation_address="大阪市浪速区幸町1丁目2-24",
        accommodation_lat=34.6937,
        accommodation_lon=135.5023,
        total_budget=5000.0
    )
    
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)
    
    return trip


@pytest.fixture
def sample_activity(db_session, sample_trip):
    """
    Create a sample activity for testing.
    
    Args:
        db_session: Database session fixture
        sample_trip: Sample trip fixture
        
    Returns:
        Activity: Sample activity object
    """
    activity = Activity(
        name="Visit Osaka Castle",
        description="Explore the historic Osaka Castle and gardens",
        trip_id=sample_trip.id,
        activity_date=date(2025, 7, 27),
        time_slot=TimeSlot.AFTERNOON,
        category=ActivityCategory.SIGHTSEEING,
        priority=Priority.MUST_DO,
        location_name="Osaka Castle",
        address="1-1 Osakajo, Chuo Ward, Osaka",
        latitude=34.6873,
        longitude=135.5262,
        estimated_cost=600.0,
        notes="Don't forget the camera!"
    )
    
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    
    return activity


@pytest.fixture
def sample_family_member(db_session, sample_trip):
    """
    Create a sample family member for testing.
    
    Args:
        db_session: Database session fixture
        sample_trip: Sample trip fixture
        
    Returns:
        FamilyMember: Sample family member object
    """
    member = FamilyMember(
        name="Dad",
        role=MemberRole.PARENT,
        age=35,
        trip_id=sample_trip.id,
        dietary_restrictions="No allergies",
        interests="History, Technology, Food",
        wishlist_items="Osaka Castle, Dotonbori, Universal Studios"
    )
    
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    
    return member


@pytest.fixture
def sample_trip_data():
    """
    Sample trip data for API testing.
    
    Returns:
        dict: Trip creation data
    """
    return {
        "name": "Tokyo Adventure",
        "destination": "Tokyo, Japan",
        "start_date": "2025-09-15",
        "end_date": "2025-09-22",
        "accommodation_address": "Tokyo Station, Tokyo, Japan",
        "total_budget": 7500.0
    }


@pytest.fixture
def sample_activity_data(sample_trip):
    """
    Sample activity data for API testing.
    
    Args:
        sample_trip: Sample trip fixture
        
    Returns:
        dict: Activity creation data
    """
    return {
        "trip_id": sample_trip.id,
        "name": "Tokyo Skytree Visit",
        "description": "Visit the iconic Tokyo Skytree tower",
        "activity_date": "2025-09-15",
        "time_slot": "morning",
        "category": "sightseeing",
        "priority": "must_do",
        "location_name": "Tokyo Skytree",
        "address": "1 Chome-1-2 Oshiage, Sumida City, Tokyo",
        "estimated_cost": 2000.0,
        "notes": "Book tickets in advance"
    }


@pytest.fixture
def sample_family_member_data(sample_trip):
    """
    Sample family member data for API testing.
    
    Args:
        sample_trip: Sample trip fixture
        
    Returns:
        dict: Family member creation data
    """
    return {
        "trip_id": sample_trip.id,
        "name": "Mom",
        "role": "parent",
        "age": 33,
        "dietary_restrictions": "Vegetarian",
        "interests": "Culture, Shopping, Photography",
        "wishlist_items": "Meiji Shrine, Harajuku, Ginza"
    }


@pytest.fixture
def mock_geocoding_service():
    """
    Mock geocoding service for testing.
    
    Returns:
        Mock: Mocked geocoding service
    """
    mock_service = Mock()
    mock_service.geocode_address = AsyncMock(return_value=(34.6937, 135.5023))
    mock_service.reverse_geocode = AsyncMock(return_value="Osaka, Japan"))
    mock_service.get_place_details = AsyncMock(return_value={
        "name": "Osaka Castle",
        "address": "1-1 Osakajo, Chuo Ward, Osaka",
        "latitude": 34.6873,
        "longitude": 135.5262
    })
    
    return mock_service


@pytest.fixture
def mock_weather_service():
    """
    Mock weather service for testing.
    
    Returns:
        Mock: Mocked weather service
    """
    mock_service = Mock()
    mock_service.get_current_weather = AsyncMock(return_value={
        "main": {
            "temp": 25.5,
            "feels_like": 27.0,
            "humidity": 65
        },
        "weather": [{
            "main": "Clear",
            "description": "clear sky",
            "icon": "01d"
        }],
        "name": "Osaka"
    })
    
    mock_service.get_weather_forecast = AsyncMock(return_value={
        "list": [
            {
                "dt": 1627776000,
                "main": {
                    "temp_min": 22.0,
                    "temp_max": 28.0
                },
                "weather": [{
                    "main": "Clear",
                    "description": "clear sky"
                }]
            }
        ]
    })
    
    mock_service.format_weather_summary = Mock(return_value={
        "temperature": 26,
        "feels_like": 27,
        "humidity": 65,
        "description": "Clear Sky",
        "condition": "Clear"
    })
    
    mock_service.get_daily_forecasts = Mock(return_value=[
        {
            "date": "2025-07-27",
            "min_temp": 22,
            "max_temp": 28,
            "condition": "Clear",
            "description": "22°-28°C"
        }
    ])
    
    return mock_service


@pytest.fixture
def auth_headers():
    """
    Authentication headers for API testing.
    
    Returns:
        dict: Headers with authentication
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


# Utility functions for tests
def assert_datetime_close(dt1, dt2, delta_seconds=5):
    """
    Assert that two datetime objects are close to each other.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        delta_seconds: Maximum allowed difference in seconds
    """
    if isinstance(dt1, str):
        dt1 = datetime.fromisoformat(dt1.replace('Z', '+00:00'))
    if isinstance(dt2, str):
        dt2 = datetime.fromisoformat(dt2.replace('Z', '+00:00'))
    
    diff = abs((dt1 - dt2).total_seconds())
    assert diff <= delta_seconds, f"Datetimes differ by {diff} seconds (max: {delta_seconds})"


def assert_coordinates_close(coord1, coord2, delta=0.001):
    """
    Assert that two coordinate pairs are close to each other.
    
    Args:
        coord1: First coordinate tuple (lat, lon)
        coord2: Second coordinate tuple (lat, lon)
        delta: Maximum allowed difference
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    assert abs(lat1 - lat2) <= delta, f"Latitudes differ by {abs(lat1 - lat2)} (max: {delta})"
    assert abs(lon1 - lon2) <= delta, f"Longitudes differ by {abs(lon1 - lon2)} (max: {delta})"