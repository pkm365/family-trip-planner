"""
Database configuration and session management.

Sets up SQLAlchemy engine, session factory, and dependency injection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings
from .models.base import Base


# Create SQLAlchemy engine
# CRITICAL: check_same_thread=False required for SQLite with FastAPI
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database_url
    else {},
    echo=settings.debug,  # Enable SQL logging in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """
    Create all database tables.

    Should be called once during application startup.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/trips/")
        def get_trips(db: Session = Depends(get_db)):
            return db.query(Trip).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database with tables and optional sample data.

    Call this function during application startup.
    """
    create_tables()

    # Optionally add sample data in development mode
    if settings.debug:
        _create_sample_data()


def _create_sample_data() -> None:
    """Create sample data for development and testing."""
    from .models import (
        Trip,
        Activity,
        FamilyMember,
        TimeSlot,
        ActivityCategory,
        Priority,
        MemberRole,
    )
    from datetime import date

    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(Trip).first():
            return

        # Create sample trip
        sample_trip = Trip(
            name="Osaka Family Trip",
            destination="Osaka, Japan",
            start_date=date(2025, 7, 27),
            end_date=date(2025, 8, 2),
            accommodation_address="大阪市浪速区幸町1丁目2-24",
            accommodation_lat=34.6937,
            accommodation_lon=135.5023,
            total_budget=5000.0,
        )
        db.add(sample_trip)
        db.flush()  # Get the trip ID

        # Create sample family members
        family_members = [
            FamilyMember(
                name="Dad",
                role=MemberRole.PARENT,
                age=35,
                trip_id=sample_trip.id,
                interests="History, Technology, Food",
            ),
            FamilyMember(
                name="Mom",
                role=MemberRole.PARENT,
                age=33,
                trip_id=sample_trip.id,
                interests="Shopping, Culture, Photography",
            ),
            FamilyMember(
                name="Daughter",
                role=MemberRole.CHILD,
                age=8,
                trip_id=sample_trip.id,
                interests="Animals, Parks, Sweet treats",
                dietary_restrictions="No spicy food",
            ),
        ]

        for member in family_members:
            db.add(member)

        # Create sample activities
        sample_activities = [
            Activity(
                name="Visit Osaka Castle",
                description="Explore the historic Osaka Castle and gardens",
                trip_id=sample_trip.id,
                activity_date=date(2025, 7, 27),
                time_slot=TimeSlot.AFTERNOON,
                category=ActivityCategory.SIGHTSEEING,
                priority=Priority.MUST_DO,
                location_name="Osaka Castle",
                estimated_cost=600.0,
            ),
            Activity(
                name="Dotonbori Food Tour",
                description="Try local street food and restaurants",
                trip_id=sample_trip.id,
                activity_date=date(2025, 7, 27),
                time_slot=TimeSlot.EVENING,
                category=ActivityCategory.FOOD,
                priority=Priority.MUST_DO,
                location_name="Dotonbori District",
                estimated_cost=3000.0,
            ),
        ]

        for activity in sample_activities:
            db.add(activity)

        db.commit()
        print("Sample data created successfully!")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()
