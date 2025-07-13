"""
Tests for activity API routes.

Tests CRUD operations and API endpoints for activities.
"""

import pytest
from datetime import date


class TestActivityRoutes:
    """Test cases for activity API routes."""
    
    def test_create_activity_success(self, client, sample_activity_data):
        """Test successful activity creation."""
        response = client.post("/api/activities/", json=sample_activity_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == sample_activity_data["name"]
        assert data["category"] == sample_activity_data["category"]
        assert data["time_slot"] == sample_activity_data["time_slot"]
        assert "id" in data
    
    def test_create_activity_invalid_data(self, client):
        """Test activity creation with invalid data."""
        invalid_data = {"name": "Test Activity"}  # Missing required fields
        
        response = client.post("/api/activities/", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_activities_empty(self, client):
        """Test getting activities when none exist."""
        response = client.get("/api/activities/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_activities_with_filters(self, client, sample_activity):
        """Test getting activities with filters."""
        # Test trip_id filter
        response = client.get(f"/api/activities/?trip_id={sample_activity.trip_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_activity.id
        
        # Test category filter
        response = client.get(f"/api/activities/?category={sample_activity.category.value}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_activity_by_id_success(self, client, sample_activity):
        """Test getting specific activity by ID."""
        response = client.get(f"/api/activities/{sample_activity.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_activity.id
        assert data["name"] == sample_activity.name
    
    def test_get_activity_by_id_not_found(self, client):
        """Test getting activity that doesn't exist."""
        response = client.get("/api/activities/999")
        assert response.status_code == 404
    
    def test_update_activity_success(self, client, sample_activity):
        """Test successful activity update."""
        update_data = {"name": "Updated Activity", "estimated_cost": 1000.0}
        
        response = client.put(f"/api/activities/{sample_activity.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Activity"
        assert data["estimated_cost"] == 1000.0
    
    def test_delete_activity_success(self, client, sample_activity):
        """Test successful activity deletion."""
        response = client.delete(f"/api/activities/{sample_activity.id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/activities/{sample_activity.id}")
        assert get_response.status_code == 404
    
    def test_get_activities_by_date(self, client, sample_activity):
        """Test getting activities by date and trip."""
        trip_id = sample_activity.trip_id
        activity_date = sample_activity.activity_date
        
        response = client.get(f"/api/activities/trip/{trip_id}/by-date/{activity_date}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == str(activity_date)
        assert "activities" in data
        assert "total_activities" in data
        assert data["total_activities"] == 1