"""
Geocoding service using Nominatim API.

Provides address geocoding with rate limiting and error handling.
"""

import asyncio
import logging
from typing import Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding addresses using Nominatim API."""
    
    def __init__(self):
        """Initialize the geocoding service."""
        self.geolocator = Nominatim(
            user_agent="family-trip-planner",
            timeout=10
        )
        self._last_request_time = 0.0
    
    async def _rate_limit(self) -> None:
        """
        Enforce rate limiting for Nominatim API.
        
        Nominatim has strict rate limiting - 1 request per second maximum.
        """
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < 1.0:
            # Wait to ensure at least 1 second between requests
            await asyncio.sleep(1.0 - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    async def geocode_address(self, address: str) -> Tuple[float, float]:
        """
        Geocode an address to latitude and longitude coordinates.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or (0.0, 0.0) if geocoding fails
            
        Example:
            lat, lon = await geocoding_service.geocode_address("Osaka Castle, Japan")
        """
        if not address or not address.strip():
            logger.warning("Empty address provided for geocoding")
            return 0.0, 0.0
        
        # Apply rate limiting
        await self._rate_limit()
        
        try:
            # Run geocoding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            location = await loop.run_in_executor(
                None, 
                self.geolocator.geocode, 
                address.strip()
            )
            
            if location:
                lat, lon = location.latitude, location.longitude
                logger.info(f"Successfully geocoded '{address}' to ({lat}, {lon})")
                return lat, lon
            else:
                logger.warning(f"No geocoding results found for address: '{address}'")
                return 0.0, 0.0
                
        except GeocoderTimedOut:
            logger.error(f"Geocoding timed out for address: '{address}'")
            return 0.0, 0.0
            
        except GeocoderServiceError as e:
            logger.error(f"Geocoding service error for '{address}': {e}")
            return 0.0, 0.0
            
        except Exception as e:
            logger.error(f"Unexpected error geocoding '{address}': {e}")
            return 0.0, 0.0
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> str:
        """
        Reverse geocode coordinates to an address.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Address string or empty string if reverse geocoding fails
        """
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.warning(f"Invalid coordinates: ({latitude}, {longitude})")
            return ""
        
        # Apply rate limiting
        await self._rate_limit()
        
        try:
            # Run reverse geocoding in thread pool
            loop = asyncio.get_event_loop()
            location = await loop.run_in_executor(
                None,
                self.geolocator.reverse,
                f"{latitude}, {longitude}"
            )
            
            if location and location.address:
                address = location.address
                logger.info(f"Successfully reverse geocoded ({latitude}, {longitude}) to '{address}'")
                return address
            else:
                logger.warning(f"No reverse geocoding results for ({latitude}, {longitude})")
                return ""
                
        except GeocoderTimedOut:
            logger.error(f"Reverse geocoding timed out for ({latitude}, {longitude})")
            return ""
            
        except GeocoderServiceError as e:
            logger.error(f"Reverse geocoding service error for ({latitude}, {longitude}): {e}")
            return ""
            
        except Exception as e:
            logger.error(f"Unexpected error reverse geocoding ({latitude}, {longitude}): {e}")
            return ""
    
    async def get_place_details(self, place_name: str, city: str = None) -> dict:
        """
        Get detailed information about a place.
        
        Args:
            place_name: Name of the place to search for
            city: Optional city name to narrow search
            
        Returns:
            Dictionary with place details including coordinates, address, etc.
        """
        search_query = place_name
        if city:
            search_query = f"{place_name}, {city}"
        
        # Apply rate limiting
        await self._rate_limit()
        
        try:
            loop = asyncio.get_event_loop()
            location = await loop.run_in_executor(
                None,
                self.geolocator.geocode,
                search_query,
                True  # Return detailed info
            )
            
            if location:
                return {
                    "name": place_name,
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "raw_data": location.raw
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting place details for '{search_query}': {e}")
            return {}


# Global service instance
geocoding_service = GeocodingService()