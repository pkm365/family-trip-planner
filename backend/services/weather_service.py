"""
Weather service using OpenWeatherMap API.

Provides weather forecasts with caching and error handling.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List
import httpx
from ..config import settings

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Exception raised for weather API errors."""

    pass


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    def __init__(self):
        """Initialize the weather service."""
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = settings.openweather_api_key
        self._cache = {}
        self._cache_duration = timedelta(minutes=10)

    def _get_cache_key(self, lat: float, lon: float, endpoint: str) -> str:
        """Generate cache key for weather data."""
        return f"{endpoint}_{lat}_{lon}"

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:
            return False

        cached_time = cache_entry.get("timestamp")
        if not cached_time:
            return False

        return datetime.now() - cached_time < self._cache_duration

    async def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """
        Get current weather for given coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary with current weather data or empty dict if failed
        """
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return {}

        # Check cache first
        cache_key = self._get_cache_key(latitude, longitude, "current")
        if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
            logger.info(
                f"Returning cached current weather for ({latitude}, {longitude})"
            )
            return self._cache[cache_key]["data"]

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                    "units": "metric",  # Celsius, m/s, etc.
                }

                response = await client.get(
                    f"{self.base_url}/weather", params=params, timeout=10.0
                )

                if response.status_code != 200:
                    raise WeatherAPIError(f"API returned status {response.status_code}")

                data = response.json()

                # Cache the result
                self._cache[cache_key] = {"data": data, "timestamp": datetime.now()}

                logger.info(
                    f"Successfully fetched current weather for ({latitude}, {longitude})"
                )
                return data

        except httpx.TimeoutException:
            logger.error(f"Weather API timeout for ({latitude}, {longitude})")
            return {}
        except httpx.RequestError as e:
            logger.error(f"Weather API request error: {e}")
            return {}
        except WeatherAPIError as e:
            logger.error(f"Weather API error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching current weather: {e}")
            return {}

    async def get_weather_forecast(
        self, latitude: float, longitude: float, days: int = 5
    ) -> Dict:
        """
        Get weather forecast for given coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days to forecast (max 5 for free tier)

        Returns:
            Dictionary with forecast data or empty dict if failed
        """
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return {}

        # Limit days to API constraints
        days = min(days, 5)

        # Check cache first
        cache_key = self._get_cache_key(latitude, longitude, f"forecast_{days}")
        if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
            logger.info(f"Returning cached forecast for ({latitude}, {longitude})")
            return self._cache[cache_key]["data"]

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8,  # 8 forecasts per day (every 3 hours)
                }

                response = await client.get(
                    f"{self.base_url}/forecast", params=params, timeout=10.0
                )

                if response.status_code != 200:
                    raise WeatherAPIError(f"API returned status {response.status_code}")

                data = response.json()

                # Cache the result
                self._cache[cache_key] = {"data": data, "timestamp": datetime.now()}

                logger.info(
                    f"Successfully fetched {days}-day forecast for ({latitude}, {longitude})"
                )
                return data

        except httpx.TimeoutException:
            logger.error(f"Weather forecast API timeout for ({latitude}, {longitude})")
            return {}
        except httpx.RequestError as e:
            logger.error(f"Weather forecast API request error: {e}")
            return {}
        except WeatherAPIError as e:
            logger.error(f"Weather forecast API error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching weather forecast: {e}")
            return {}

    def format_weather_summary(self, weather_data: Dict) -> Dict:
        """
        Format weather data into a user-friendly summary.

        Args:
            weather_data: Raw weather data from API

        Returns:
            Formatted weather summary
        """
        if not weather_data:
            return {}

        try:
            main = weather_data.get("main", {})
            weather = weather_data.get("weather", [{}])[0]

            return {
                "temperature": round(main.get("temp", 0)),
                "feels_like": round(main.get("feels_like", 0)),
                "humidity": main.get("humidity", 0),
                "description": weather.get("description", "").title(),
                "icon": weather.get("icon", ""),
                "condition": weather.get("main", ""),
                "city": weather_data.get("name", ""),
            }
        except Exception as e:
            logger.error(f"Error formatting weather summary: {e}")
            return {}

    def get_daily_forecasts(self, forecast_data: Dict) -> List[Dict]:
        """
        Extract daily weather summaries from forecast data.

        Args:
            forecast_data: Raw forecast data from API

        Returns:
            List of daily weather summaries
        """
        if not forecast_data or "list" not in forecast_data:
            return []

        daily_forecasts = []
        current_date = None
        daily_temps = []
        daily_conditions = []

        try:
            for item in forecast_data["list"]:
                # Parse the forecast timestamp
                dt = datetime.fromtimestamp(item["dt"])
                date_str = dt.strftime("%Y-%m-%d")

                # If we've moved to a new day, save the previous day's summary
                if current_date and current_date != date_str:
                    if daily_temps:
                        daily_forecasts.append(
                            {
                                "date": current_date,
                                "min_temp": round(min(daily_temps)),
                                "max_temp": round(max(daily_temps)),
                                "condition": max(
                                    set(daily_conditions), key=daily_conditions.count
                                ),
                                "description": f"{min(daily_temps):.0f}°-{max(daily_temps):.0f}°C",
                            }
                        )
                    daily_temps = []
                    daily_conditions = []

                current_date = date_str
                daily_temps.extend([item["main"]["temp_min"], item["main"]["temp_max"]])
                daily_conditions.append(item["weather"][0]["main"])

            # Don't forget the last day
            if current_date and daily_temps:
                daily_forecasts.append(
                    {
                        "date": current_date,
                        "min_temp": round(min(daily_temps)),
                        "max_temp": round(max(daily_temps)),
                        "condition": max(
                            set(daily_conditions), key=daily_conditions.count
                        ),
                        "description": f"{min(daily_temps):.0f}°-{max(daily_temps):.0f}°C",
                    }
                )

        except Exception as e:
            logger.error(f"Error extracting daily forecasts: {e}")
            return []

        return daily_forecasts


# Global service instance
weather_service = WeatherService()
