"""
Tests for trip API routes.

Tests CRUD operations and API endpoints for trips.
"""

import pytest
from datetime import date


class TestTripRoutes:
    """Test cases for trip API routes."""

    def test_create_trip_success(self, client, sample_trip_data):
        """Test successful trip creation."""
        response = client.post("/api/trips/", json=sample_trip_data)

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == sample_trip_data["name"]
        assert data["destination"] == sample_trip_data["destination"]
        assert data["start_date"] == sample_trip_data["start_date"]
        assert data["end_date"] == sample_trip_data["end_date"]
        assert (
            data["accommodation_address"] == sample_trip_data["accommodation_address"]
        )
        assert data["total_budget"] == sample_trip_data["total_budget"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_trip_invalid_data(self, client):
        """Test trip creation with invalid data."""
        # Missing required fields
        invalid_data = {
            "name": "Test Trip"
            # Missing other required fields
        }

        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_trip_invalid_dates(self, client):
        """Test trip creation with invalid date range."""
        invalid_data = {
            "name": "Test Trip",
            "destination": "Tokyo, Japan",
            "start_date": "2025-09-22",  # End date before start date
            "end_date": "2025-09-15",
            "accommodation_address": "Tokyo Station",
            "total_budget": 5000.0,
        }

        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_trips_empty(self, client):
        """Test getting trips when none exist."""
        response = client.get("/api/trips/")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_trips_with_data(self, client, sample_trip):
        """Test getting trips when data exists."""
        response = client.get("/api/trips/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_trip.id
        assert data[0]["name"] == sample_trip.name

    def test_get_trips_pagination(self, client, db_session):
        """Test trips pagination."""
        # Create multiple trips
        from backend.models import Trip

        trips = []
        for i in range(15):
            trip = Trip(
                name=f"Trip {i}",
                destination=f"Destination {i}",
                start_date=date(2025, 7, 27),
                end_date=date(2025, 8, 2),
                accommodation_address=f"Address {i}",
                total_budget=1000.0 * i,
            )
            db_session.add(trip)
            trips.append(trip)

        db_session.commit()

        # Test default pagination
        response = client.get("/api/trips/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 15  # All trips (within default limit)

        # Test custom pagination
        response = client.get("/api/trips/?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_get_trip_by_id_success(self, client, sample_trip):
        """Test getting a specific trip by ID."""
        response = client.get(f"/api/trips/{sample_trip.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["name"] == sample_trip.name
        assert data["destination"] == sample_trip.destination

    def test_get_trip_by_id_not_found(self, client):
        """Test getting a trip that doesn't exist."""
        response = client.get("/api/trips/999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_trip_success(self, client, sample_trip):
        """Test successful trip update."""
        update_data = {"name": "Updated Trip Name", "total_budget": 8000.0}

        response = client.put(f"/api/trips/{sample_trip.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Trip Name"
        assert data["total_budget"] == 8000.0
        assert data["destination"] == sample_trip.destination  # Unchanged

    def test_update_trip_not_found(self, client):
        """Test updating a trip that doesn't exist."""
        update_data = {"name": "Updated Name"}

        response = client.put("/api/trips/999", json=update_data)

        assert response.status_code == 404

    def test_update_trip_invalid_data(self, client, sample_trip):
        """Test updating trip with invalid data."""
        update_data = {
            "total_budget": -100.0  # Negative budget should be invalid
        }

        response = client.put(f"/api/trips/{sample_trip.id}", json=update_data)

        assert response.status_code == 422  # Validation error

    def test_delete_trip_success(self, client, sample_trip):
        """Test successful trip deletion."""
        response = client.delete(f"/api/trips/{sample_trip.id}")

        assert response.status_code == 204

        # Verify trip is deleted
        get_response = client.get(f"/api/trips/{sample_trip.id}")
        assert get_response.status_code == 404

    def test_delete_trip_not_found(self, client):
        """Test deleting a trip that doesn't exist."""
        response = client.delete("/api/trips/999")

        assert response.status_code == 404

    def test_get_trip_daily_activities(self, client, sample_trip, sample_activity):
        """Test getting daily activities for a trip."""
        response = client.get(f"/api/trips/{sample_trip.id}/daily-activities")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Should have activities for all trip days
        trip_days = (sample_trip.end_date - sample_trip.start_date).days + 1
        assert len(data) == trip_days

        # Find the day with our sample activity
        activity_day = None
        for day in data:
            if day["date"] == str(sample_activity.activity_date):
                activity_day = day
                break

        assert activity_day is not None
        assert activity_day["total_estimated_cost"] == sample_activity.estimated_cost

        # Check that activity is in the correct time slot
        time_slot = sample_activity.time_slot.value
        assert len(activity_day[time_slot]) == 1
        assert activity_day[time_slot][0]["name"] == sample_activity.name

    def test_get_trip_weather_success(self, client, sample_trip, mock_weather_service):
        """Test getting weather for a trip."""
        with pytest.mock.patch(
            "backend.services.trip_service.weather_service", mock_weather_service
        ):
            response = client.get(f"/api/trips/{sample_trip.id}/weather")

            assert response.status_code == 200
            data = response.json()
            assert "current" in data
            assert "daily_forecasts" in data
            assert "location" in data

    def test_get_trip_weather_no_coordinates(self, client, db_session):
        """Test getting weather for a trip without coordinates."""
        from backend.models import Trip

        # Create trip without coordinates
        trip = Trip(
            name="No Coords Trip",
            destination="Unknown",
            start_date=date(2025, 7, 27),
            end_date=date(2025, 8, 2),
            accommodation_address="Unknown Address",
            total_budget=1000.0,
        )
        db_session.add(trip)
        db_session.commit()
        db_session.refresh(trip)

        response = client.get(f"/api/trips/{trip.id}/weather")

        assert response.status_code == 503  # Service unavailable

    def test_get_trip_family_preferences(
        self, client, sample_trip, sample_family_member
    ):
        """Test getting family preferences for a trip."""
        response = client.get(f"/api/trips/{sample_trip.id}/family-preferences")

        assert response.status_code == 200
        data = response.json()

        assert data["total_members"] == 1
        assert "age_groups" in data
        assert "dietary_restrictions" in data
        assert "common_interests" in data

    def test_get_trip_family_preferences_no_members(self, client, sample_trip):
        """Test getting family preferences when no members exist."""
        response = client.get(f"/api/trips/{sample_trip.id}/family-preferences")

        assert response.status_code == 200
        data = response.json()
        assert data["total_members"] == 0


class TestTripValidation:
    """Test cases for trip data validation."""

    def test_trip_date_validation(self, client):
        """Test various date validation scenarios."""
        base_data = {
            "name": "Test Trip",
            "destination": "Tokyo, Japan",
            "accommodation_address": "Tokyo Station",
            "total_budget": 5000.0,
        }

        # Test end date before start date
        invalid_data = {
            **base_data,
            "start_date": "2025-08-02",
            "end_date": "2025-07-27",
        }
        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422

        # Test same start and end date (should be invalid)
        invalid_data = {
            **base_data,
            "start_date": "2025-07-27",
            "end_date": "2025-07-27",
        }
        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422

        # Test valid date range
        valid_data = {**base_data, "start_date": "2025-07-27", "end_date": "2025-08-02"}
        response = client.post("/api/trips/", json=valid_data)
        assert response.status_code == 201

    def test_trip_budget_validation(self, client):
        """Test budget validation."""
        base_data = {
            "name": "Test Trip",
            "destination": "Tokyo, Japan",
            "start_date": "2025-07-27",
            "end_date": "2025-08-02",
            "accommodation_address": "Tokyo Station",
        }

        # Test negative budget
        invalid_data = {**base_data, "total_budget": -100.0}
        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422

        # Test zero budget (should be valid)
        valid_data = {**base_data, "total_budget": 0.0}
        response = client.post("/api/trips/", json=valid_data)
        assert response.status_code == 201

        # Test positive budget
        valid_data = {**base_data, "total_budget": 5000.0}
        response = client.post("/api/trips/", json=valid_data)
        assert response.status_code == 201

    def test_trip_string_length_validation(self, client):
        """Test string field length validation."""
        base_data = {
            "destination": "Tokyo, Japan",
            "start_date": "2025-07-27",
            "end_date": "2025-08-02",
            "accommodation_address": "Tokyo Station",
            "total_budget": 5000.0,
        }

        # Test empty name
        invalid_data = {**base_data, "name": ""}
        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422

        # Test very long name (over 100 characters)
        invalid_data = {**base_data, "name": "x" * 101}
        response = client.post("/api/trips/", json=invalid_data)
        assert response.status_code == 422

        # Test valid name
        valid_data = {**base_data, "name": "Valid Trip Name"}
        response = client.post("/api/trips/", json=valid_data)
        assert response.status_code == 201
