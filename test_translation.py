#!/usr/bin/env python3
"""
Test script for translation functionality.

This script tests the translation API endpoints and verifies the
Chinese content generation is working correctly.
"""

import asyncio
import requests
import json
from backend.config import settings

BASE_URL = "http://127.0.0.1:8000"

def test_api_status():
    """Test if the API is running and translation service is available."""
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            translation_service = data.get("services", {}).get("translation", {})
            
            print("✅ API Status:")
            print(f"   Available: {translation_service.get('available', False)}")
            print(f"   OpenAI Key Configured: {translation_service.get('openai_key_configured', False)}")
            print(f"   Supported Languages: {translation_service.get('supported_languages', [])}")
            
            return translation_service.get('available', False)
        else:
            print(f"❌ API Status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking API status: {e}")
        return False

def test_translation_status():
    """Test translation status endpoint."""
    try:
        # Get list of trips first
        response = requests.get(f"{BASE_URL}/api/trips/")
        if response.status_code == 200:
            trips = response.json()
            if trips:
                trip_id = trips[0]["id"]
                
                # Check translation status
                status_response = requests.get(f"{BASE_URL}/api/translation/status/{trip_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"\n✅ Translation Status for Trip {trip_id}:")
                    print(f"   Trip Name: {status.get('trip_name')}")
                    print(f"   Total Activities: {status.get('total_activities')}")
                    print(f"   Translated: {status.get('translated_activities')}")
                    print(f"   Translation %: {status.get('translation_percentage')}%")
                    print(f"   Fully Translated: {status.get('fully_translated')}")
                    return status
                else:
                    print(f"❌ Translation status failed: {status_response.status_code}")
            else:
                print("❌ No trips found")
        else:
            print(f"❌ Failed to get trips: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking translation status: {e}")
    return None

def test_trigger_translation():
    """Test triggering translation for a trip."""
    try:
        # Get list of trips first
        response = requests.get(f"{BASE_URL}/api/trips/")
        if response.status_code == 200:
            trips = response.json()
            if trips:
                trip_id = trips[0]["id"]
                
                print(f"\n🚀 Triggering translation for Trip {trip_id}...")
                
                # Trigger translation
                trigger_response = requests.post(
                    f"{BASE_URL}/api/translation/trigger/{trip_id}",
                    headers={"Content-Type": "application/json"},
                    json={"force_retranslate": False}
                )
                
                if trigger_response.status_code == 200:
                    result = trigger_response.json()
                    print(f"✅ Translation Result:")
                    print(f"   Success: {result.get('success')}")
                    print(f"   Translated Count: {result.get('translated_count')}")
                    print(f"   Error Count: {result.get('error_count')}")
                    print(f"   Message: {result.get('message')}")
                    
                    if result.get('errors'):
                        print(f"   Errors: {result.get('errors')}")
                    
                    return result.get('success', False)
                else:
                    print(f"❌ Translation trigger failed: {trigger_response.status_code}")
                    print(f"   Response: {trigger_response.text}")
            else:
                print("❌ No trips found")
        else:
            print(f"❌ Failed to get trips: {response.status_code}")
    except Exception as e:
        print(f"❌ Error triggering translation: {e}")
    return False

def main():
    """Run translation tests."""
    print("🧪 Testing Translation Functionality\n")
    
    # Test 1: API Status
    if not test_api_status():
        print("\n❌ Translation service not available. Please check:")
        print("   1. FastAPI server is running")
        print("   2. OpenAI API key is configured in environment")
        return
    
    # Test 2: Translation Status
    status = test_translation_status()
    if not status:
        print("\n❌ Could not check translation status")
        return
    
    # Test 3: Trigger Translation (only if needed)
    if status.get('total_activities', 0) > 0:
        if not status.get('fully_translated', False):
            print(f"\n📝 Found {status.get('needs_translation', 0)} activities that need translation")
            
            # Ask user if they want to proceed
            try:
                proceed = input("\n🤔 Do you want to trigger translation? (y/n): ").lower().strip()
                if proceed in ['y', 'yes']:
                    success = test_trigger_translation()
                    if success:
                        # Check status again
                        print("\n🔄 Checking translation status after translation...")
                        test_translation_status()
                    else:
                        print("\n❌ Translation failed")
                else:
                    print("\n⏭️  Skipping translation trigger")
            except KeyboardInterrupt:
                print("\n\n⏭️  Skipping translation trigger")
        else:
            print(f"\n✅ All activities are already translated!")
    else:
        print(f"\n📝 No activities found to translate")
    
    print("\n🎉 Translation test completed!")

if __name__ == "__main__":
    main()