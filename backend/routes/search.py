"""
Search API routes for activity discovery.

Endpoints for searching and managing activity recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import ActivityRecommendation, Trip
from ..schemas.activity_recommendation import (
    SearchRequest,
    SearchResponse,
    ActivityRecommendationResponse,
    ActivityRecommendationListResponse,
    ActivityRecommendationUpdate
)
from ..services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/activities", response_model=SearchResponse)
async def search_activities(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for activity recommendations using external APIs.
    
    This endpoint searches multiple sources (Google Places, etc.) for activities
    based on the provided query and filters, then saves the results as 
    activity recommendations for family voting.
    """
    async with SearchService() as search_service:
        try:
            recommendations, metadata = await search_service.search_activities(
                query=search_request.query,
                trip_id=search_request.trip_id,
                db=db,
                category=search_request.category,
                budget_min=search_request.budget_min,
                budget_max=search_request.budget_max,
                radius_km=search_request.radius_km,
                limit=search_request.limit
            )
            
            # Convert to response format
            recommendation_responses = []
            for rec in recommendations:
                # Calculate vote summary and popularity score
                vote_summary = rec.vote_summary
                popularity_score = rec.popularity_score
                
                response = ActivityRecommendationResponse(
                    id=rec.id,
                    name=rec.name,
                    description=rec.description,
                    category=rec.category,
                    location_name=rec.location_name,
                    address=rec.address,
                    latitude=rec.latitude,
                    longitude=rec.longitude,
                    external_id=rec.external_id,
                    external_source=rec.external_source,
                    external_rating=rec.external_rating,
                    external_review_count=rec.external_review_count,
                    estimated_cost=rec.estimated_cost,
                    estimated_duration_hours=rec.estimated_duration_hours,
                    difficulty_level=rec.difficulty_level,
                    age_appropriate=rec.age_appropriate,
                    primary_image_url=rec.primary_image_url,
                    image_urls=rec.image_urls,
                    search_query=rec.search_query,
                    trip_id=rec.trip_id,
                    discovery_date=rec.discovery_date,
                    is_active=rec.is_active,
                    created_at=rec.created_at,
                    updated_at=rec.updated_at,
                    vote_summary=vote_summary,
                    popularity_score=popularity_score
                )
                recommendation_responses.append(response)
            
            return SearchResponse(
                recommendations=recommendation_responses,
                total_count=len(recommendation_responses),
                search_metadata=metadata
            )
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/recommendations", response_model=ActivityRecommendationListResponse)
def get_recommendations(
    trip_id: Optional[int] = Query(None, description="Filter by trip ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    sort_by: str = Query("popularity_score", description="Sort by: popularity_score, created_at, vote_score"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of activity recommendations with filtering and sorting.
    """
    from sqlalchemy.orm import joinedload
    
    query = db.query(ActivityRecommendation).options(joinedload(ActivityRecommendation.votes))
    
    # Apply filters
    if trip_id is not None:
        query = query.filter(ActivityRecommendation.trip_id == trip_id)
    
    if category is not None:
        query = query.filter(ActivityRecommendation.category == category)
    
    if is_active is not None:
        query = query.filter(ActivityRecommendation.is_active == is_active)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply sorting
    if sort_by == "created_at":
        order_column = ActivityRecommendation.created_at
    elif sort_by == "vote_score":
        # For now, sort by created_at (vote score would need a complex query)
        order_column = ActivityRecommendation.created_at
    else:  # popularity_score or default
        order_column = ActivityRecommendation.created_at
    
    if sort_order == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
    
    # Apply pagination
    offset = (page - 1) * page_size
    recommendations = query.offset(offset).limit(page_size).all()
    
    # Convert to response format
    recommendation_responses = []
    for rec in recommendations:
        vote_summary = rec.vote_summary
        popularity_score = rec.popularity_score
        
        response = ActivityRecommendationResponse(
            id=rec.id,
            name=rec.name,
            description=rec.description,
            category=rec.category,
            location_name=rec.location_name,
            address=rec.address,
            latitude=rec.latitude,
            longitude=rec.longitude,
            external_id=rec.external_id,
            external_source=rec.external_source,
            external_rating=rec.external_rating,
            external_review_count=rec.external_review_count,
            estimated_cost=rec.estimated_cost,
            estimated_duration_hours=rec.estimated_duration_hours,
            difficulty_level=rec.difficulty_level,
            age_appropriate=rec.age_appropriate,
            primary_image_url=rec.primary_image_url,
            image_urls=rec.image_urls,
            search_query=rec.search_query,
            trip_id=rec.trip_id,
            discovery_date=rec.discovery_date,
            is_active=rec.is_active,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
            vote_summary=vote_summary,
            popularity_score=popularity_score
        )
        recommendation_responses.append(response)
    
    has_next = offset + page_size < total_count
    has_previous = page > 1
    
    return ActivityRecommendationListResponse(
        recommendations=recommendation_responses,
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_previous=has_previous
    )


@router.get("/recommendations/{recommendation_id}", response_model=ActivityRecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific activity recommendation by ID."""
    from sqlalchemy.orm import joinedload
    
    recommendation = db.query(ActivityRecommendation).options(
        joinedload(ActivityRecommendation.votes)
    ).filter(
        ActivityRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    vote_summary = recommendation.vote_summary
    popularity_score = recommendation.popularity_score
    
    return ActivityRecommendationResponse(
        id=recommendation.id,
        name=recommendation.name,
        description=recommendation.description,
        category=recommendation.category,
        location_name=recommendation.location_name,
        address=recommendation.address,
        latitude=recommendation.latitude,
        longitude=recommendation.longitude,
        external_id=recommendation.external_id,
        external_source=recommendation.external_source,
        external_rating=recommendation.external_rating,
        external_review_count=recommendation.external_review_count,
        estimated_cost=recommendation.estimated_cost,
        estimated_duration_hours=recommendation.estimated_duration_hours,
        difficulty_level=recommendation.difficulty_level,
        age_appropriate=recommendation.age_appropriate,
        primary_image_url=recommendation.primary_image_url,
        image_urls=recommendation.image_urls,
        search_query=recommendation.search_query,
        trip_id=recommendation.trip_id,
        discovery_date=recommendation.discovery_date,
        is_active=recommendation.is_active,
        created_at=recommendation.created_at,
        updated_at=recommendation.updated_at,
        vote_summary=vote_summary,
        popularity_score=popularity_score
    )


@router.put("/recommendations/{recommendation_id}", response_model=ActivityRecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    update_data: ActivityRecommendationUpdate,
    db: Session = Depends(get_db)
):
    """Update an activity recommendation."""
    recommendation = db.query(ActivityRecommendation).filter(
        ActivityRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(recommendation, field, value)
    
    db.commit()
    db.refresh(recommendation)
    
    vote_summary = recommendation.vote_summary
    popularity_score = recommendation.popularity_score
    
    return ActivityRecommendationResponse(
        id=recommendation.id,
        name=recommendation.name,
        description=recommendation.description,
        category=recommendation.category,
        location_name=recommendation.location_name,
        address=recommendation.address,
        latitude=recommendation.latitude,
        longitude=recommendation.longitude,
        external_id=recommendation.external_id,
        external_source=recommendation.external_source,
        external_rating=recommendation.external_rating,
        external_review_count=recommendation.external_review_count,
        estimated_cost=recommendation.estimated_cost,
        estimated_duration_hours=recommendation.estimated_duration_hours,
        difficulty_level=recommendation.difficulty_level,
        age_appropriate=recommendation.age_appropriate,
        primary_image_url=recommendation.primary_image_url,
        image_urls=recommendation.image_urls,
        search_query=recommendation.search_query,
        trip_id=recommendation.trip_id,
        discovery_date=recommendation.discovery_date,
        is_active=recommendation.is_active,
        created_at=recommendation.created_at,
        updated_at=recommendation.updated_at,
        vote_summary=vote_summary,
        popularity_score=popularity_score
    )


@router.delete("/recommendations/{recommendation_id}")
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Delete an activity recommendation."""
    recommendation = db.query(ActivityRecommendation).filter(
        ActivityRecommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    db.delete(recommendation)
    db.commit()
    
    return {"message": "Recommendation deleted successfully"}