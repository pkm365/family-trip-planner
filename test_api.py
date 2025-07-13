#!/usr/bin/env python3
"""
Test script to verify API endpoints are working.
"""

import requests
import json

def test_api_endpoints():
    """Test the API endpoints to ensure they return the correct data."""
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test trips endpoint
        print("Testing /api/trips/...")
        response = requests.get(f"{base_url}/api/trips/")
        if response.status_code == 200:
            trips = response.json()
            print(f"✓ Found {len(trips)} trips")
            for trip in trips:
                print(f"  - Trip {trip['id']}: {trip['name']}")
        else:
            print(f"✗ Trips API failed: {response.status_code}")
            return
        
        # Test activities endpoint for trip 1
        print("\nTesting /api/activities/?trip_id=1...")
        response = requests.get(f"{base_url}/api/activities/?trip_id=1")
        if response.status_code == 200:
            activities = response.json()
            print(f"✓ Found {len(activities)} activities for trip 1")
            for activity in activities:
                print(f"  - Activity {activity['id']}: {activity['name']}")
        else:
            print(f"✗ Activities API failed: {response.status_code} - {response.text}")
        
        # Test family members endpoint for trip 1
        print("\nTesting /api/family-members/?trip_id=1...")
        response = requests.get(f"{base_url}/api/family-members/?trip_id=1")
        if response.status_code == 200:
            members = response.json()
            print(f"✓ Found {len(members)} family members for trip 1")
            for member in members:
                print(f"  - Member {member['id']}: {member['name']} ({member['role']})")
        else:
            print(f"✗ Family members API failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"✗ Error testing APIs: {e}")

if __name__ == "__main__":
    test_api_endpoints()