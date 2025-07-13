"""
Tests for geocoding service.

Following patterns from existing test_geocoding.py.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from backend.services.geocoding_service import GeocodingService, geocoding_service


class TestGeocodingService:
    """Test cases for GeocodingService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = GeocodingService()
    
    @pytest.mark.asyncio
    async def test_geocode_address_success(self):
        """Test successful address geocoding."""
        # PATTERN: Mock external API like existing test_geocoding.py
        with patch.object(self.service.geolocator, 'geocode') as mock_geocode:
            mock_location = Mock()
            mock_location.latitude = 34.6937
            mock_location.longitude = 135.5023
            
            # Mock the executor call
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(return_value=mock_location)
                mock_event_loop.time.side_effect = [0, 1.1]  # For rate limiting
                
                lat, lon = await self.service.geocode_address("Osaka, Japan")
                
                assert lat == 34.6937
                assert lon == 135.5023
    
    @pytest.mark.asyncio
    async def test_geocode_address_failure(self):
        """Test geocoding failure handling."""
        # PATTERN: Test failure case like existing test_geocoding.py
        with patch.object(self.service.geolocator, 'geocode') as mock_geocode:
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(side_effect=GeocoderTimedOut("Timeout"))
                mock_event_loop.time.side_effect = [0, 1.1]
                
                lat, lon = await self.service.geocode_address("Invalid Address")
                
                assert lat == 0.0
                assert lon == 0.0
    
    @pytest.mark.asyncio
    async def test_geocode_address_no_results(self):
        """Test geocoding when no results found."""
        with patch.object(self.service.geolocator, 'geocode') as mock_geocode:
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(return_value=None)
                mock_event_loop.time.side_effect = [0, 1.1]
                
                lat, lon = await self.service.geocode_address("Nonexistent Place")
                
                assert lat == 0.0
                assert lon == 0.0
    
    @pytest.mark.asyncio
    async def test_geocode_address_empty_input(self):
        """Test geocoding with empty address."""
        lat, lon = await self.service.geocode_address("")
        assert lat == 0.0
        assert lon == 0.0
        
        lat, lon = await self.service.geocode_address("   ")
        assert lat == 0.0
        assert lon == 0.0
        
        lat, lon = await self.service.geocode_address(None)
        assert lat == 0.0
        assert lon == 0.0
    
    @pytest.mark.asyncio
    async def test_geocode_address_service_error(self):
        """Test geocoding with service error."""
        with patch.object(self.service.geolocator, 'geocode') as mock_geocode:
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(
                    side_effect=GeocoderServiceError("Service unavailable")
                )
                mock_event_loop.time.side_effect = [0, 1.1]
                
                lat, lon = await self.service.geocode_address("Test Address")
                
                assert lat == 0.0
                assert lon == 0.0
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_success(self):
        """Test successful reverse geocoding."""
        with patch.object(self.service.geolocator, 'reverse') as mock_reverse:
            mock_location = Mock()
            mock_location.address = "Osaka Castle, Osaka, Japan"
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(return_value=mock_location)
                mock_event_loop.time.side_effect = [0, 1.1]
                
                address = await self.service.reverse_geocode(34.6937, 135.5023)
                
                assert address == "Osaka Castle, Osaka, Japan"
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_invalid_coordinates(self):
        """Test reverse geocoding with invalid coordinates."""
        # Invalid latitude
        address = await self.service.reverse_geocode(91.0, 135.5023)
        assert address == ""
        
        # Invalid longitude
        address = await self.service.reverse_geocode(34.6937, 181.0)
        assert address == ""
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_failure(self):
        """Test reverse geocoding failure."""
        with patch.object(self.service.geolocator, 'reverse') as mock_reverse:
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(return_value=None)
                mock_event_loop.time.side_effect = [0, 1.1]
                
                address = await self.service.reverse_geocode(34.6937, 135.5023)
                
                assert address == ""
    
    @pytest.mark.asyncio
    async def test_get_place_details_success(self):
        """Test successful place details retrieval."""
        with patch.object(self.service.geolocator, 'geocode') as mock_geocode:
            mock_location = Mock()
            mock_location.address = "Osaka Castle, Osaka, Japan"
            mock_location.latitude = 34.6873
            mock_location.longitude = 135.5262
            mock_location.raw = {"place_id": "12345", "type": "castle"}
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(return_value=mock_location)
                mock_event_loop.time.side_effect = [0, 1.1]
                
                details = await self.service.get_place_details("Osaka Castle", "Osaka")
                
                assert details["name"] == "Osaka Castle"
                assert details["address"] == "Osaka Castle, Osaka, Japan"
                assert details["latitude"] == 34.6873
                assert details["longitude"] == 135.5262
                assert "raw_data" in details
    
    @pytest.mark.asyncio
    async def test_get_place_details_failure(self):
        """Test place details retrieval failure."""
        with patch.object(self.service.geolocator, 'geocode') as mock_geocode:
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_event_loop = Mock()
                mock_loop.return_value = mock_event_loop
                mock_event_loop.run_in_executor = AsyncMock(return_value=None)
                mock_event_loop.time.side_effect = [0, 1.1]
                
                details = await self.service.get_place_details("Nonexistent Place")
                
                assert details == {}
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting works correctly."""
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_event_loop = Mock()
            mock_loop.return_value = mock_event_loop
            
            # Mock time to simulate rapid requests
            mock_event_loop.time.side_effect = [0, 0.5, 1.5]  # Second call too soon, third call OK
            
            with patch('asyncio.sleep') as mock_sleep:
                # This should trigger rate limiting
                await self.service._rate_limit()
                
                # Should have slept to enforce rate limit
                mock_sleep.assert_called_once_with(0.5)
    
    @pytest.mark.asyncio 
    async def test_rate_limiting_no_delay_needed(self):
        """Test rate limiting when no delay is needed."""
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_event_loop = Mock()
            mock_loop.return_value = mock_event_loop
            
            # Mock time to simulate sufficient delay between requests
            mock_event_loop.time.side_effect = [0, 1.5]  # More than 1 second apart
            
            with patch('asyncio.sleep') as mock_sleep:
                await self.service._rate_limit()
                
                # Should not have slept
                mock_sleep.assert_not_called()


class TestGlobalGeocodingService:
    """Test cases for global geocoding service instance."""
    
    @pytest.mark.asyncio
    async def test_global_service_exists(self):
        """Test that global service instance exists and works."""
        assert geocoding_service is not None
        assert isinstance(geocoding_service, GeocodingService)
    
    @pytest.mark.asyncio
    async def test_global_service_geocode_empty_address(self):
        """Test global service with empty address."""
        lat, lon = await geocoding_service.geocode_address("")
        assert lat == 0.0
        assert lon == 0.0