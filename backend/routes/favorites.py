"""
Favorites API routes for activity recommendations.

Endpoints for favoriting and managing favorite activity recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import ActivityFavorite, ActivityRecommendation, FamilyMember, Trip
from ..schemas.activity_favorite import (
    ActivityFavoriteCreate,
    ActivityFavoriteUpdate,
    ActivityFavoriteResponse,
    FavoritesDashboardResponse,
    RecommendationWithFavorites,
    FamilyMemberFavoriteInfo,
    FavoritesListResponse,
)

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.post("/", response_model=ActivityFavoriteResponse)
def create_favorite(
    favorite_data: ActivityFavoriteCreate, db: Session = Depends(get_db)
):
    """
    Add an activity recommendation to a family member's favorites.

    If the recommendation is already favorited by this family member,
    this will update their existing favorite with new notes.
    """
    # Check if recommendation exists
    recommendation = (
        db.query(ActivityRecommendation)
        .filter(ActivityRecommendation.id == favorite_data.recommendation_id)
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Check if family member exists
    family_member = (
        db.query(FamilyMember)
        .filter(FamilyMember.id == favorite_data.family_member_id)
        .first()
    )
    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    # Check if favorite already exists
    existing_favorite = (
        db.query(ActivityFavorite)
        .filter(
            ActivityFavorite.recommendation_id == favorite_data.recommendation_id,
            ActivityFavorite.family_member_id == favorite_data.family_member_id,
        )
        .first()
    )

    if existing_favorite:
        # Update existing favorite
        if favorite_data.notes:
            existing_favorite.notes = favorite_data.notes
        db.commit()
        db.refresh(existing_favorite)
        return existing_favorite
    else:
        # Create new favorite
        favorite = ActivityFavorite(
            recommendation_id=favorite_data.recommendation_id,
            family_member_id=favorite_data.family_member_id,
            notes=favorite_data.notes,
        )
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite


@router.get("/", response_model=List[ActivityFavoriteResponse])
def get_favorites(
    recommendation_id: Optional[int] = Query(
        None, description="Filter by recommendation ID"
    ),
    family_member_id: Optional[int] = Query(
        None, description="Filter by family member ID"
    ),
    trip_id: Optional[int] = Query(None, description="Filter by trip ID"),
    db: Session = Depends(get_db),
):
    """Get favorites with optional filtering."""
    query = db.query(ActivityFavorite)

    if recommendation_id is not None:
        query = query.filter(ActivityFavorite.recommendation_id == recommendation_id)

    if family_member_id is not None:
        query = query.filter(ActivityFavorite.family_member_id == family_member_id)

    if trip_id is not None:
        # Join with recommendations to filter by trip
        query = query.join(ActivityRecommendation).filter(
            ActivityRecommendation.trip_id == trip_id
        )

    favorites = query.order_by(ActivityFavorite.favorite_date.desc()).all()
    return favorites


@router.get("/list/{family_member_id}", response_model=FavoritesListResponse)
def get_family_member_favorites(
    family_member_id: int,
    trip_id: Optional[int] = Query(None, description="Filter by trip ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get a family member's favorites list with full recommendation details."""
    # Check if family member exists
    family_member = (
        db.query(FamilyMember).filter(FamilyMember.id == family_member_id).first()
    )
    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")

    # Build query
    query = (
        db.query(ActivityFavorite)
        .filter(ActivityFavorite.family_member_id == family_member_id)
        .join(ActivityRecommendation)
    )

    if trip_id is not None:
        query = query.filter(ActivityRecommendation.trip_id == trip_id)

    # Get total count
    total_count = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    favorites = (
        query.order_by(ActivityFavorite.favorite_date.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Get full recommendation details
    recommendation_ids = [fav.recommendation_id for fav in favorites]
    recommendations = (
        db.query(ActivityRecommendation)
        .filter(ActivityRecommendation.id.in_(recommendation_ids))
        .all()
    )

    # Convert recommendations to dict for easy lookup
    recommendations_dict = {
        rec.id: {
            "id": rec.id,
            "name": rec.name,
            "description": rec.description,
            "category": rec.category,
            "location_name": rec.location_name,
            "address": rec.address,
            "latitude": rec.latitude,
            "longitude": rec.longitude,
            "external_rating": rec.external_rating,
            "external_review_count": rec.external_review_count,
            "estimated_cost": rec.estimated_cost,
            "estimated_duration_hours": rec.estimated_duration_hours,
            "primary_image_url": rec.primary_image_url,
            "discovery_date": rec.discovery_date,
            "vote_summary": rec.vote_summary,
            "popularity_score": rec.popularity_score,
            # Chinese translation fields
            "description_zh": rec.description_zh,
            "cultural_notes_zh": rec.cultural_notes_zh,
            "tips_for_chinese_travelers": rec.tips_for_chinese_travelers,
            "quality_score": rec.quality_score,
        }
        for rec in recommendations
    }

    recommendations_list = [
        recommendations_dict[fav.recommendation_id]
        for fav in favorites
        if fav.recommendation_id in recommendations_dict
    ]

    has_next = offset + page_size < total_count
    has_previous = page > 1

    return FavoritesListResponse(
        favorites=favorites,
        recommendations=recommendations_list,
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.put("/{favorite_id}", response_model=ActivityFavoriteResponse)
def update_favorite(
    favorite_id: int,
    favorite_update: ActivityFavoriteUpdate,
    db: Session = Depends(get_db),
):
    """Update a favorite (mainly notes)."""
    favorite = (
        db.query(ActivityFavorite).filter(ActivityFavorite.id == favorite_id).first()
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    if favorite_update.notes is not None:
        favorite.notes = favorite_update.notes

    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    """Remove a favorite."""
    favorite = (
        db.query(ActivityFavorite).filter(ActivityFavorite.id == favorite_id).first()
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
    return {"message": "Favorite removed successfully"}


@router.delete("/recommendation/{recommendation_id}/member/{family_member_id}")
def delete_favorite_by_ids(
    recommendation_id: int, family_member_id: int, db: Session = Depends(get_db)
):
    """Remove a favorite by recommendation and family member IDs."""
    favorite = (
        db.query(ActivityFavorite)
        .filter(
            ActivityFavorite.recommendation_id == recommendation_id,
            ActivityFavorite.family_member_id == family_member_id,
        )
        .first()
    )

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()
    return {"message": "Favorite removed successfully"}


@router.get("/dashboard/{trip_id}", response_model=FavoritesDashboardResponse)
def get_favorites_dashboard(trip_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive favorites dashboard for a trip.

    Returns all recommendations with favorite details, family member info,
    and favorite statistics for the dashboard view.
    """
    # Get trip
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Get family members
    family_members = (
        db.query(FamilyMember).filter(FamilyMember.trip_id == trip_id).all()
    )
    family_member_data = [
        {"id": fm.id, "name": fm.name, "role": fm.role.value} for fm in family_members
    ]

    # Get recommendations with favorites
    recommendations = (
        db.query(ActivityRecommendation)
        .filter(
            ActivityRecommendation.trip_id == trip_id,
            ActivityRecommendation.is_active == True,
        )
        .all()
    )

    recommendations_with_favorites = []
    total_favorites = 0
    total_recommendations = len(recommendations)

    for rec in recommendations:
        # Get favorites for this recommendation
        favorites = (
            db.query(ActivityFavorite)
            .filter(ActivityFavorite.recommendation_id == rec.id)
            .all()
        )

        # Build family favorite info
        family_favorites = []
        favorites_by_member = {fav.family_member_id: fav for fav in favorites}

        for fm in family_members:
            favorite = favorites_by_member.get(fm.id)
            family_favorites.append(
                FamilyMemberFavoriteInfo(
                    family_member_id=fm.id,
                    family_member_name=fm.name,
                    has_favorited=favorite is not None,
                    favorite_date=favorite.favorite_date if favorite else None,
                    notes=favorite.notes if favorite else None,
                )
            )

        total_favorites += len(favorites)

        recommendations_with_favorites.append(
            RecommendationWithFavorites(
                recommendation_id=rec.id,
                recommendation_name=rec.name,
                total_favorites=len(favorites),
                family_favorites=family_favorites,
            )
        )

    # Calculate favorite statistics
    favorite_statistics = {
        "total_recommendations": total_recommendations,
        "total_favorites": total_favorites,
        "total_family_members": len(family_members),
        "average_favorites_per_recommendation": total_favorites / total_recommendations
        if total_recommendations > 0
        else 0,
        "favorite_participation_rate": (
            total_favorites / (total_recommendations * len(family_members))
        )
        if total_recommendations > 0 and len(family_members) > 0
        else 0,
    }

    return FavoritesDashboardResponse(
        trip_id=trip_id,
        trip_name=trip.name,
        family_members=family_member_data,
        recommendations_with_favorites=recommendations_with_favorites,
        favorite_statistics=favorite_statistics,
    )


@router.get("/check/{recommendation_id}/member/{family_member_id}")
def check_if_favorited(
    recommendation_id: int, family_member_id: int, db: Session = Depends(get_db)
):
    """Check if a recommendation is favorited by a specific family member."""
    favorite = (
        db.query(ActivityFavorite)
        .filter(
            ActivityFavorite.recommendation_id == recommendation_id,
            ActivityFavorite.family_member_id == family_member_id,
        )
        .first()
    )

    return {
        "is_favorited": favorite is not None,
        "favorite_id": favorite.id if favorite else None,
        "favorite_date": favorite.favorite_date if favorite else None,
        "notes": favorite.notes if favorite else None,
    }
