"""
Geocoding API routes.

Provides endpoints for address geocoding services.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict
from ..services import geocoding_service

router = APIRouter(prefix="/api/geocoding", tags=["geocoding"])


@router.get("/geocode")
async def geocode_address(
    address: str = Query(..., min_length=1, description="Address to geocode")
) -> Dict:
    """
    Geocode an address to coordinates.
    
    Args:
        address: Address string to geocode
        
    Returns:
        Geocoding results with coordinates
    """
    if not address.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address parameter cannot be empty"
        )
    
    latitude, longitude = await geocoding_service.geocode_address(address)
    
    # Check if geocoding was successful
    if latitude == 0.0 and longitude == 0.0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not geocode address: {address}"
        )
    
    return {
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "coordinates": [longitude, latitude]  # GeoJSON format [lon, lat]
    }


@router.get("/reverse-geocode")
async def reverse_geocode_coordinates(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude coordinate")
) -> Dict:
    """
    Reverse geocode coordinates to an address.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Reverse geocoding results with address
    """
    address = await geocoding_service.reverse_geocode(latitude, longitude)
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not reverse geocode coordinates: ({latitude}, {longitude})"
        )
    
    return {
        "latitude": latitude,
        "longitude": longitude,
        "address": address,
        "coordinates": [longitude, latitude]  # GeoJSON format [lon, lat]
    }


@router.get("/place-details")
async def get_place_details(
    place_name: str = Query(..., min_length=1, description="Name of the place"),
    city: str = Query(None, description="City to narrow down search (optional)")
) -> Dict:
    """
    Get detailed information about a place.
    
    Args:
        place_name: Name of the place to search for
        city: Optional city name to narrow search
        
    Returns:
        Detailed place information
    """
    if not place_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Place name parameter cannot be empty"
        )
    
    place_details = await geocoding_service.get_place_details(place_name, city)
    
    if not place_details:
        search_query = f"{place_name}, {city}" if city else place_name
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find details for place: {search_query}"
        )
    
    return place_details


@router.post("/batch-geocode")
async def batch_geocode_addresses(addresses: list[str]) -> Dict:
    """
    Geocode multiple addresses in batch.
    
    Note: This endpoint respects rate limiting by processing addresses sequentially.
    
    Args:
        addresses: List of addresses to geocode
        
    Returns:
        Batch geocoding results
    """
    if not addresses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one address must be provided"
        )
    
    if len(addresses) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 addresses allowed per batch request"
        )
    
    results = []
    failed_addresses = []
    
    for address in addresses:
        if not address.strip():
            failed_addresses.append({
                "address": address,
                "error": "Empty address"
            })
            continue
        
        try:
            latitude, longitude = await geocoding_service.geocode_address(address)
            
            if latitude == 0.0 and longitude == 0.0:
                failed_addresses.append({
                    "address": address,
                    "error": "Geocoding failed"
                })
            else:
                results.append({
                    "address": address,
                    "latitude": latitude,
                    "longitude": longitude,
                    "coordinates": [longitude, latitude]
                })
        except Exception as e:
            failed_addresses.append({
                "address": address,
                "error": str(e)
            })
    
    return {
        "total_requested": len(addresses),
        "successful": len(results),
        "failed": len(failed_addresses),
        "results": results,
        "failed_addresses": failed_addresses
    }