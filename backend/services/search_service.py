"""
Activity Search Service

Integrates with external APIs to discover activity recommendations.
Currently supports Google Places API with extensible architecture for additional services.
"""

import aiohttp
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import ActivityRecommendation, Trip
from ..config import settings
from ..services.geocoding_service import geocoding_service
from ..services.translation_service import translation_service

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for discovering activity recommendations from external APIs.

    Features:
    - Google Places API integration
    - Result caching and deduplication
    - Intelligent categorization
    - Family-friendly filtering
    """

    def __init__(self):
        # 读取配置中的 Google Places API Key（蛇形命名）
        self.google_places_api_key = settings.google_places_api_key
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def search_activities(
        self,
        query: str,
        trip_id: int,
        db: Session,
        category: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        radius_km: float = 5.0,
        limit: int = 20,
    ) -> Tuple[List[ActivityRecommendation], Dict[str, Any]]:
        """Legacy search method - use smart_search_activities for better results."""
        return await self.smart_search_activities(
            query, trip_id, db, category, budget_min, budget_max, radius_km, limit
        )

    async def smart_search_activities(
        self,
        query: str,
        trip_id: int,
        db: Session,
        category: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        radius_km: float = 5.0,
        limit: int = 15,
        min_quality_score: int = 60,
        include_chinese_content: bool = True,
    ) -> Tuple[List[ActivityRecommendation], Dict[str, Any]]:
        """
        Smart search for high-quality activity recommendations with Chinese content.

        This method implements intelligent filtering and translation:
        1. Searches external APIs for activities
        2. Scores activities for quality (rating, reviews, family-friendly)
        3. Filters to only high-quality results
        4. Translates to Chinese for better user experience
        5. Returns top results with cultural context

        Args:
            query: Search query (e.g., "restaurants in Tokyo", "family activities")
            trip_id: Trip ID for context and location
            db: Database session
            category: Optional category filter
            budget_min: Minimum budget filter
            budget_max: Maximum budget filter
            radius_km: Search radius in kilometers
            limit: Maximum number of quality results to return (default 15)
            min_quality_score: Minimum quality score threshold (default 60)
            include_chinese_content: Whether to include Chinese translations

        Returns:
            Tuple of (recommendations list, search metadata)
        """
        # Get trip for location context
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip with id {trip_id} not found")

        # Initialize session if not in context manager
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Search multiple sources with expanded results for filtering
        raw_limit = limit * 3  # Get 3x more results for quality filtering
        all_results = []
        search_metadata = {
            "query": query,
            "trip_destination": trip.destination,
            "sources_searched": [],
            "results_count_by_source": {},
            "search_timestamp": datetime.utcnow().isoformat(),
            "quality_filtering": {
                "min_score_threshold": min_quality_score,
                "requested_limit": limit
            }
        }

        # Google Places search with expanded limit
        if self.google_places_api_key:
            try:
                google_results = await self._search_google_places(
                    query, trip, radius_km, raw_limit
                )
                all_results.extend(google_results)
                search_metadata["sources_searched"].append("google_places")
                search_metadata["results_count_by_source"]["google_places"] = len(
                    google_results
                )
            except Exception as e:
                print(f"Google Places search failed: {e}")

        # Mock results for development with quality scoring
        if not all_results and not self.google_places_api_key:
            mock_results = self._generate_mock_results(query, trip_id, raw_limit)
            all_results.extend(mock_results)
            search_metadata["sources_searched"].append("mock_data")
            search_metadata["results_count_by_source"]["mock_data"] = len(mock_results)

        # 1. Score all results for quality
        scored_results = []
        for result in all_results:
            quality_score = translation_service.calculate_quality_score(
                result,
                result.get("external_rating"),
                result.get("external_review_count")
            )
            result["quality_score"] = quality_score
            scored_results.append(result)

        # 2. Filter by quality score
        quality_filtered = [r for r in scored_results if r["quality_score"] >= min_quality_score]
        
        # 3. Sort by quality score (highest first)
        quality_filtered.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # 4. Apply budget and category filters to quality results
        filtered_results = self._filter_results(
            quality_filtered, category, budget_min, budget_max
        )

        # 5. Take top quality results for translation
        top_quality_results = filtered_results[:limit]
        
        search_metadata["quality_filtering"]["raw_results"] = len(all_results)
        search_metadata["quality_filtering"]["quality_passed"] = len(quality_filtered)
        search_metadata["quality_filtering"]["final_selected"] = len(top_quality_results)

        # 6. Save to database with quality scores
        recommendations = await self._save_recommendations(
            top_quality_results, trip_id, query, db
        )

        # 7. Add Chinese content if requested
        if include_chinese_content and recommendations:
            try:
                # Convert to dict format for translation
                activities_for_translation = []
                for rec in recommendations:
                    activity_dict = {
                        "name": rec.name,
                        "description": rec.description,
                        "external_rating": rec.external_rating,
                        "external_review_count": rec.external_review_count,
                        "types": rec.category,
                        "category": rec.category
                    }
                    activities_for_translation.append(activity_dict)
                
                # Batch translate all activities
                translated_activities = await translation_service.batch_translate_activities(
                    db, activities_for_translation
                )
                
                # Update recommendations with Chinese content
                for i, rec in enumerate(recommendations):
                    if i < len(translated_activities):
                        translated = translated_activities[i]
                        if translated.get("description_zh"):
                            rec.description_zh = translated["description_zh"]
                        if translated.get("cultural_notes_zh"):
                            rec.cultural_notes_zh = translated["cultural_notes_zh"]
                        if translated.get("tips_for_chinese_travelers"):
                            rec.tips_for_chinese_travelers = translated["tips_for_chinese_travelers"]
                
                # Commit Chinese content updates
                db.commit()
                search_metadata["chinese_content_added"] = True
                
            except Exception as e:
                logger.error(f"Error adding Chinese content: {e}")
                search_metadata["chinese_content_error"] = str(e)

        search_metadata["final_count"] = len(recommendations)
        return recommendations, search_metadata

    async def _search_google_places(
        self, query: str, trip: Trip, radius_km: float, limit: int
    ) -> List[Dict[str, Any]]:
        """Search Google Places API for activities."""
        if not self.google_places_api_key:
            return []

        # Determine coordinates for radius filtering
        if trip.accommodation_lat is not None and trip.accommodation_lon is not None:
            location = f"{trip.accommodation_lat},{trip.accommodation_lon}"
        else:
            # Fallback: geocode trip.destination once to get lat/lon
            lat, lon = await geocoding_service.geocode_address(trip.destination)
            if lat and lon:
                location = f"{lat},{lon}"
            else:
                location = None  # No coordinate available

        # Text search API
        text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{query} in {trip.destination}",
            "key": self.google_places_api_key,
            "type": "tourist_attraction|restaurant|point_of_interest",
        }
        # 仅当有坐标时才附带 location+radius
        if location:
            params.update({"location": location, "radius": int(radius_km * 1000)})

        results = []

        try:
            async with self.session.get(text_search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    places = data.get("results", [])

                    for place in places[:limit]:
                        # Get additional details for each place
                        detailed_place = await self._get_place_details(
                            place.get("place_id")
                        )
                        if detailed_place:
                            results.append(detailed_place)

        except Exception as e:
            print(f"Google Places API error: {e}")

        return results

    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information and convert to internal format."""
        if not place_id or not self.google_places_api_key:
            return None

        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "place_id,name,formatted_address,geometry,rating,user_ratings_total,price_level,photos,types,editorial_summary",
            "key": self.google_places_api_key,
        }

        try:
            async with self.session.get(details_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    place = data.get("result", {})
                    if not place:
                        return None

                    # Photo handling
                    primary_image_url = None
                    image_urls = []
                    photos = place.get("photos", [])
                    for photo in photos[:5]:
                        photo_ref = photo.get("photo_reference")
                        if not photo_ref:
                            continue
                        url = (
                            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&"
                            f"photo_reference={photo_ref}&key={self.google_places_api_key}"
                        )
                        if not primary_image_url:
                            primary_image_url = url
                        image_urls.append(url)

                    # Description (editorial summary)
                    description = place.get("editorial_summary", {}).get("overview")

                    return {
                        "name": place.get("name"),
                        "description": description,
                        "category": place.get("types", ["general"])[0]
                        if place.get("types")
                        else "general",
                        "location_name": place.get("name"),
                        "address": place.get("formatted_address"),
                        "latitude": place.get("geometry", {})
                        .get("location", {})
                        .get("lat"),
                        "longitude": place.get("geometry", {})
                        .get("location", {})
                        .get("lng"),
                        "external_id": place_id,
                        "external_source": "google_places",
                        "external_rating": place.get("rating"),
                        "external_review_count": place.get("user_ratings_total"),
                        "estimated_cost": 0.0,
                        "estimated_duration_hours": None,
                        "difficulty_level": None,
                        "age_appropriate": None,
                        "primary_image_url": primary_image_url,
                        "image_urls": image_urls,
                    }
        except Exception as e:
            print(f"Place details API error: {e}")

        return None

    def _generate_mock_results(
        self, query: str, trip_id: int, limit: int
    ) -> List[Dict[str, Any]]:
        """Generate mock results for development/testing."""
        mock_activities = [
            {
                "name": "Osaka Castle",
                "description": "Historic Japanese castle with beautiful gardens and museum",
                "category": "sightseeing",
                "location_name": "Osaka Castle",
                "address": "1-1 Osakajo, Chuo Ward, Osaka",
                "latitude": 34.6873,
                "longitude": 135.5262,
                "external_rating": 4.3,
                "external_review_count": 15420,
                "estimated_cost": 600.0,
                "estimated_duration_hours": 2.5,
                "primary_image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "difficulty_level": "easy",
                "age_appropriate": "all_ages",
            },
            {
                "name": "Dotonbori Food Street",
                "description": "Famous entertainment district known for street food and neon signs",
                "category": "food",
                "location_name": "Dotonbori",
                "address": "Dotonbori, Chuo Ward, Osaka",
                "latitude": 34.6698,
                "longitude": 135.5023,
                "external_rating": 4.5,
                "external_review_count": 8930,
                "estimated_cost": 2500.0,
                "estimated_duration_hours": 3.0,
                "primary_image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "difficulty_level": "easy",
                "age_appropriate": "all_ages",
            },
            {
                "name": "Universal Studios Japan",
                "description": "Theme park with movie-themed attractions and rides",
                "category": "sightseeing",
                "location_name": "Universal Studios Japan",
                "address": "2-1-33 Sakurajima, Konohana Ward, Osaka",
                "latitude": 34.6658,
                "longitude": 135.4322,
                "external_rating": 4.4,
                "external_review_count": 25600,
                "estimated_cost": 8500.0,
                "estimated_duration_hours": 8.0,
                "primary_image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "difficulty_level": "moderate",
                "age_appropriate": "families",
            },
            {
                "name": "Shinsaibashi Shopping District",
                "description": "Major shopping area with department stores and boutiques",
                "category": "shopping",
                "location_name": "Shinsaibashi",
                "address": "Shinsaibashi, Chuo Ward, Osaka",
                "latitude": 34.6717,
                "longitude": 135.5019,
                "external_rating": 4.2,
                "external_review_count": 12400,
                "estimated_cost": 5000.0,
                "estimated_duration_hours": 4.0,
                "primary_image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "difficulty_level": "easy",
                "age_appropriate": "all_ages",
            },
            {
                "name": "Spa World",
                "description": "Large onsen and spa complex with international themed baths",
                "category": "rest",
                "location_name": "Spa World",
                "address": "3-4-24 Ebisuhigashi, Naniwa Ward, Osaka",
                "latitude": 34.6547,
                "longitude": 135.5065,
                "external_rating": 4.1,
                "external_review_count": 7800,
                "estimated_cost": 1500.0,
                "estimated_duration_hours": 3.0,
                "primary_image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "difficulty_level": "easy",
                "age_appropriate": "families",
            },
            {
                "name": "Kuromon Ichiba Market",
                "description": "Traditional market known as 'Osaka's Kitchen' with fresh food",
                "category": "food",
                "location_name": "Kuromon Ichiba Market",
                "address": "2-4-1 Nipponbashi, Chuo Ward, Osaka",
                "latitude": 34.6662,
                "longitude": 135.5069,
                "external_rating": 4.0,
                "external_review_count": 9200,
                "estimated_cost": 1200.0,
                "estimated_duration_hours": 2.0,
                "primary_image_url": "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
                "difficulty_level": "easy",
                "age_appropriate": "all_ages",
            },
        ]

        # Filter by query relevance (simple keyword matching)
        query_lower = query.lower()
        relevant_activities = []

        for activity in mock_activities:
            if (
                query_lower in activity["name"].lower()
                or query_lower in activity["description"].lower()
                or query_lower in activity["category"].lower()
            ):
                relevant_activities.append(activity)

        # If no specific matches, return all activities
        if not relevant_activities:
            relevant_activities = mock_activities

        return relevant_activities[:limit]

    def _filter_results(
        self,
        results: List[Dict[str, Any]],
        category: Optional[str],
        budget_min: Optional[float],
        budget_max: Optional[float],
    ) -> List[Dict[str, Any]]:
        """Filter search results based on criteria."""
        filtered = results

        if category:
            filtered = [r for r in filtered if r.get("category") == category]

        if budget_min is not None:
            filtered = [r for r in filtered if r.get("estimated_cost", 0) >= budget_min]

        if budget_max is not None:
            filtered = [r for r in filtered if r.get("estimated_cost", 0) <= budget_max]

        return filtered

    async def _save_recommendations(
        self,
        results: List[Dict[str, Any]],
        trip_id: int,
        search_query: str,
        db: Session,
    ) -> List[ActivityRecommendation]:
        """Save search results as activity recommendations, avoiding duplicates."""
        recommendations = []

        for result in results:
            # Check if recommendation already exists
            existing = (
                db.query(ActivityRecommendation)
                .filter(
                    ActivityRecommendation.trip_id == trip_id,
                    ActivityRecommendation.name == result["name"],
                    ActivityRecommendation.address == result.get("address"),
                )
                .first()
            )

            if existing:
                # Update existing recommendation if needed
                existing.search_query = search_query
                existing.updated_at = datetime.utcnow()
                recommendations.append(existing)
                continue

            # Create new recommendation
            recommendation = ActivityRecommendation(
                trip_id=trip_id,
                name=result["name"],
                description=result.get("description"),
                # category 字段可能不存在（Google Places结果无统一字段）。
                category=result.get("category")
                or (
                    result.get("types", ["general"])[0]
                    if isinstance(result.get("types"), list)
                    else "general"
                ),
                location_name=result.get("location_name"),
                address=result.get("address"),
                latitude=result.get("latitude"),
                longitude=result.get("longitude"),
                external_id=result.get("external_id"),
                external_source=result.get("external_source", "search"),
                external_rating=result.get("external_rating"),
                external_review_count=result.get("external_review_count"),
                estimated_cost=result.get("estimated_cost", 0.0),
                estimated_duration_hours=result.get("estimated_duration_hours"),
                difficulty_level=result.get("difficulty_level"),
                age_appropriate=result.get("age_appropriate"),
                primary_image_url=result.get("primary_image_url"),
                image_urls=json.dumps(result.get("image_urls", []))
                if result.get("image_urls")
                else None,
                quality_score=result.get("quality_score", 0),  # Save quality score
                search_query=search_query,
                discovery_date=datetime.utcnow(),
            )

            db.add(recommendation)
            recommendations.append(recommendation)

        db.commit()

        # Refresh to get IDs and relationships
        for rec in recommendations:
            db.refresh(rec)

        return recommendations
