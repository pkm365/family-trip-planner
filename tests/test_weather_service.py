"""
Tests for weather service.

Following patterns from existing test_imaging.py for HTTP client testing.
"""

import pytest
from unittest.mock import patch, Mock, AsyncMock
import httpx
from datetime import datetime, timedelta

from backend.services.weather_service import WeatherService, WeatherAPIError, weather_service
from backend.config import settings


class TestWeatherService:
    """Test cases for WeatherService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = WeatherService()
        # Set a test API key
        self.service.api_key = "test_api_key"
    
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self):
        """Test successful current weather API call."""
        # PATTERN: Mock HTTP client like test_imaging.py
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get = AsyncMock(return_value=mock_response)
            
            weather = await self.service.get_current_weather(34.6937, 135.5023)
            
            assert weather["main"]["temp"] == 25.5
            assert weather["weather"][0]["description"] == "clear sky"
            assert weather["name"] == "Osaka"
    
    @pytest.mark.asyncio
    async def test_get_current_weather_no_api_key(self):
        """Test current weather with no API key configured."""
        self.service.api_key = ""
        
        weather = await self.service.get_current_weather(34.6937, 135.5023)
        
        assert weather == {}
    
    @pytest.mark.asyncio
    async def test_get_current_weather_api_error(self):
        """Test current weather with API error response."""
        mock_response = Mock()
        mock_response.status_code = 401
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get = AsyncMock(return_value=mock_response)
            
            weather = await self.service.get_current_weather(34.6937, 135.5023)
            
            assert weather == {}
    
    @pytest.mark.asyncio
    async def test_get_current_weather_timeout(self):
        """Test current weather with timeout."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            
            weather = await self.service.get_current_weather(34.6937, 135.5023)
            
            assert weather == {}
    
    @pytest.mark.asyncio
    async def test_get_current_weather_request_error(self):
        """Test current weather with request error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get = AsyncMock(side_effect=httpx.RequestError("Connection failed"))
            
            weather = await self.service.get_current_weather(34.6937, 135.5023)
            
            assert weather == {}
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_success(self):
        """Test successful weather forecast API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
                },
                {
                    "dt": 1627862400,
                    "main": {
                        "temp_min": 20.0,
                        "temp_max": 26.0
                    },
                    "weather": [{
                        "main": "Clouds",
                        "description": "partly cloudy"
                    }]
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get = AsyncMock(return_value=mock_response)
            
            forecast = await self.service.get_weather_forecast(34.6937, 135.5023, 3)
            
            assert "list" in forecast
            assert len(forecast["list"]) == 2
            assert forecast["list"][0]["main"]["temp_max"] == 28.0
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_days_limit(self):
        """Test weather forecast with days limit enforced."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"list": []}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_client.return_value.__aenter__.return_value = mock_context
            mock_context.get = AsyncMock(return_value=mock_response)
            
            # Request more than 5 days, should be limited to 5
            await self.service.get_weather_forecast(34.6937, 135.5023, 10)
            
            # Check that the API was called with max 5 days (5 * 8 = 40 forecasts)
            call_args = mock_context.get.call_args
            assert call_args[1]["params"]["cnt"] == 40  # 5 days * 8 forecasts per day
    
    def test_format_weather_summary_success(self):
        """Test successful weather data formatting."""
        weather_data = {
            "main": {
                "temp": 25.7,
                "feels_like": 27.3,
                "humidity": 65
            },
            "weather": [{
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d"
            }],
            "name": "Osaka"
        }
        
        summary = self.service.format_weather_summary(weather_data)
        
        assert summary["temperature"] == 26  # Rounded
        assert summary["feels_like"] == 27  # Rounded
        assert summary["humidity"] == 65
        assert summary["description"] == "Clear Sky"  # Title case
        assert summary["condition"] == "Clear"
        assert summary["city"] == "Osaka"
    
    def test_format_weather_summary_empty_data(self):
        """Test weather formatting with empty data."""
        summary = self.service.format_weather_summary({})
        assert summary == {}
        
        summary = self.service.format_weather_summary(None)
        assert summary == {}
    
    def test_format_weather_summary_missing_fields(self):
        """Test weather formatting with missing fields."""
        weather_data = {
            "main": {"temp": 25.0},
            "weather": [{}]
        }
        
        summary = self.service.format_weather_summary(weather_data)
        
        assert summary["temperature"] == 25
        assert summary["feels_like"] == 0  # Default
        assert summary["humidity"] == 0  # Default
        assert summary["description"] == ""  # Default
    
    def test_get_daily_forecasts_success(self):
        """Test extracting daily forecasts from forecast data."""
        forecast_data = {
            "list": [
                {
                    "dt": 1627776000,  # 2021-08-01 00:00:00
                    "main": {"temp_min": 20.0, "temp_max": 25.0},
                    "weather": [{"main": "Clear"}]
                },
                {
                    "dt": 1627786800,  # 2021-08-01 03:00:00
                    "main": {"temp_min": 18.0, "temp_max": 27.0},
                    "weather": [{"main": "Clear"}]
                },
                {
                    "dt": 1627862400,  # 2021-08-02 00:00:00
                    "main": {"temp_min": 22.0, "temp_max": 28.0},
                    "weather": [{"main": "Clouds"}]
                }
            ]
        }
        
        daily_forecasts = self.service.get_daily_forecasts(forecast_data)
        
        assert len(daily_forecasts) == 2  # Two different dates
        
        # First day
        day1 = daily_forecasts[0]
        assert day1["date"] == "2021-08-01"
        assert day1["min_temp"] == 18  # Minimum of all temp_min values for the day
        assert day1["max_temp"] == 27  # Maximum of all temp_max values for the day
        assert day1["condition"] == "Clear"
        
        # Second day
        day2 = daily_forecasts[1]
        assert day2["date"] == "2021-08-02"
        assert day2["condition"] == "Clouds"
    
    def test_get_daily_forecasts_empty_data(self):
        """Test daily forecasts with empty data."""
        forecasts = self.service.get_daily_forecasts({})
        assert forecasts == []
        
        forecasts = self.service.get_daily_forecasts(None)
        assert forecasts == []
        
        forecasts = self.service.get_daily_forecasts({"list": []})
        assert forecasts == []
    
    def test_cache_functionality(self):
        """Test weather data caching."""
        # Clear cache first
        self.service._cache.clear()
        
        # Create test data
        weather_data = {"main": {"temp": 25.0}}
        cache_key = self.service._get_cache_key(34.6937, 135.5023, "current")
        
        # Manually add to cache
        self.service._cache[cache_key] = {
            "data": weather_data,
            "timestamp": datetime.now()
        }
        
        # Check cache validity
        cache_entry = self.service._cache[cache_key]
        assert self.service._is_cache_valid(cache_entry) is True
        
        # Test expired cache
        cache_entry["timestamp"] = datetime.now() - timedelta(minutes=15)
        assert self.service._is_cache_valid(cache_entry) is False
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.service._get_cache_key(34.6937, 135.5023, "current")
        key2 = self.service._get_cache_key(34.6937, 135.5023, "current")
        key3 = self.service._get_cache_key(34.6937, 135.5023, "forecast")
        
        assert key1 == key2  # Same parameters should generate same key
        assert key1 != key3  # Different endpoint should generate different key


class TestGlobalWeatherService:
    """Test cases for global weather service instance."""
    
    def test_global_service_exists(self):
        """Test that global service instance exists."""
        assert weather_service is not None
        assert isinstance(weather_service, WeatherService)
    
    def test_global_service_api_key_from_settings(self):
        """Test that global service uses API key from settings."""
        assert weather_service.api_key == settings.openweather_api_key
    
    @pytest.mark.asyncio
    async def test_global_service_no_api_key(self):
        """Test global service behavior with no API key."""
        original_key = weather_service.api_key
        weather_service.api_key = ""
        
        try:
            weather = await weather_service.get_current_weather(34.6937, 135.5023)
            assert weather == {}
        finally:
            # Restore original key
            weather_service.api_key = original_key


class TestWeatherAPIError:
    """Test cases for WeatherAPIError exception."""
    
    def test_weather_api_error_creation(self):
        """Test WeatherAPIError exception creation."""
        error = WeatherAPIError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)