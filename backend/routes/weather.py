"""
Weather API routes.

Provides endpoints for weather data access.
"""

from fastapi import APIRouter, HTTPException, status, Query, Path
from ..services import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current/{latitude}/{longitude}")
async def get_current_weather(
    latitude: float = Path(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Path(..., ge=-180, le=180, description="Longitude coordinate"),
) -> dict:
    """
    Get current weather for specific coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Current weather data
    """
    weather_data = await weather_service.get_current_weather(latitude, longitude)

    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather data temporarily unavailable",
        )

    # Format for frontend consumption
    formatted_data = weather_service.format_weather_summary(weather_data)

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "current": formatted_data,
        "raw_data": weather_data,
    }


@router.get("/forecast/{latitude}/{longitude}")
async def get_weather_forecast(
    latitude: float = Path(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Path(..., ge=-180, le=180, description="Longitude coordinate"),
    days: int = Query(5, ge=1, le=5, description="Number of days to forecast"),
) -> dict:
    """
    Get weather forecast for specific coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        days: Number of days to forecast (1-5)

    Returns:
        Weather forecast data
    """
    forecast_data = await weather_service.get_weather_forecast(
        latitude, longitude, days
    )

    if not forecast_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather forecast temporarily unavailable",
        )

    # Extract daily forecasts
    daily_forecasts = weather_service.get_daily_forecasts(forecast_data)

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "forecast_days": days,
        "daily_forecasts": daily_forecasts,
        "raw_data": forecast_data,
    }


@router.get("/combined/{latitude}/{longitude}")
async def get_combined_weather(
    latitude: float = Path(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Path(..., ge=-180, le=180, description="Longitude coordinate"),
    days: int = Query(5, ge=1, le=5, description="Number of days to forecast"),
) -> dict:
    """
    Get both current weather and forecast in a single response.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        days: Number of days to forecast

    Returns:
        Combined weather data
    """
    # Get both current and forecast data concurrently
    import asyncio

    current_task = weather_service.get_current_weather(latitude, longitude)
    forecast_task = weather_service.get_weather_forecast(latitude, longitude, days)

    current_data, forecast_data = await asyncio.gather(
        current_task, forecast_task, return_exceptions=True
    )

    # Handle any exceptions
    if isinstance(current_data, Exception):
        current_data = {}
    if isinstance(forecast_data, Exception):
        forecast_data = {}

    # Format current weather
    current_formatted = (
        weather_service.format_weather_summary(current_data) if current_data else {}
    )

    # Extract daily forecasts
    daily_forecasts = (
        weather_service.get_daily_forecasts(forecast_data) if forecast_data else []
    )

    return {
        "location": {"latitude": latitude, "longitude": longitude},
        "current": current_formatted,
        "daily_forecasts": daily_forecasts,
        "status": {
            "current_available": bool(current_data),
            "forecast_available": bool(forecast_data),
            "forecast_days": len(daily_forecasts),
        },
    }
