"""
Translation API Routes

Provides endpoints for managing content translations, particularly for Chinese content.
Supports both on-demand translation and batch processing of existing activities.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from ..database import get_db
from ..models import ActivityRecommendation, Activity, Trip
from ..services.translation_service import translation_service
from ..services.search_service import SearchService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/translation", tags=["translation"])


class TranslationRequest(BaseModel):
    """Request model for translation operations."""
    activity_ids: List[int]
    source_language: str = "en"
    target_language: str = "zh"
    include_cultural_content: bool = True


class BatchTranslationRequest(BaseModel):
    """Request model for batch translation operations."""
    trip_id: Optional[int] = None
    source_language: str = "en" 
    target_language: str = "zh"
    include_cultural_content: bool = True
    force_retranslate: bool = False


class TranslationResponse(BaseModel):
    """Response model for translation operations."""
    success: bool
    translated_count: int
    skipped_count: int
    error_count: int
    errors: List[str] = []
    message: str


@router.post("/activities", response_model=TranslationResponse)
async def translate_activities(
    request: TranslationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Translate specific activities by their IDs.
    
    This endpoint allows targeted translation of specific activities,
    useful for translating newly discovered activities or retranslating
    specific content.
    """
    try:
        # Fetch activities from database
        activities = db.query(ActivityRecommendation).filter(
            ActivityRecommendation.id.in_(request.activity_ids)
        ).all()
        
        if not activities:
            raise HTTPException(
                status_code=404, 
                detail="No activities found with the provided IDs"
            )
        
        logger.info(f"Starting translation for {len(activities)} activities")
        
        # Convert to dict format for translation service
        activities_for_translation = []
        for activity in activities:
            activity_dict = {
                "name": activity.name,
                "description": activity.description,
                "external_rating": activity.external_rating,
                "external_review_count": activity.external_review_count,
                "types": activity.category,
                "category": activity.category
            }
            activities_for_translation.append(activity_dict)
        
        # Perform translation
        translated_activities = await translation_service.batch_translate_activities(
            db, activities_for_translation, 
            request.source_language, request.target_language
        )
        
        # Update database with translations
        translated_count = 0
        error_count = 0
        errors = []
        
        for i, activity in enumerate(activities):
            if i < len(translated_activities):
                try:
                    translated = translated_activities[i]
                    
                    # Update Chinese content fields
                    if translated.get("description_zh"):
                        activity.description_zh = translated["description_zh"]
                    if translated.get("cultural_notes_zh"):
                        activity.cultural_notes_zh = translated["cultural_notes_zh"]
                    if translated.get("tips_for_chinese_travelers"):
                        activity.tips_for_chinese_travelers = translated["tips_for_chinese_travelers"]
                    
                    translated_count += 1
                    logger.info(f"Updated activity {activity.id} with Chinese content")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Failed to update activity {activity.id}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        # Commit changes
        db.commit()
        
        return TranslationResponse(
            success=error_count == 0,
            translated_count=translated_count,
            skipped_count=0,
            error_count=error_count,
            errors=errors,
            message=f"Successfully translated {translated_count} activities"
        )
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/batch", response_model=TranslationResponse)
async def batch_translate_trip_activities(
    request: BatchTranslationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Batch translate all activities for a trip or all activities in the system.
    
    This endpoint processes multiple activities efficiently, with options to:
    - Translate all activities for a specific trip
    - Translate all activities in the system (if no trip_id provided)
    - Force retranslation of already translated content
    - Skip activities that already have translations
    """
    try:
        # Get both regular activities and activity recommendations
        activities_to_translate = []
        
        if request.trip_id:
            # Validate trip exists
            trip = db.query(Trip).filter(Trip.id == request.trip_id).first()
            if not trip:
                raise HTTPException(status_code=404, detail="Trip not found")
            
            # Get regular activities for the trip
            activity_query = db.query(Activity).filter(Activity.trip_id == request.trip_id)
            if not request.force_retranslate:
                activity_query = activity_query.filter(
                    (Activity.description_zh.is_(None)) |
                    (Activity.description_zh == "")
                )
            activities_to_translate.extend(activity_query.all())
            
            # Get activity recommendations for the trip
            rec_query = db.query(ActivityRecommendation).filter(ActivityRecommendation.trip_id == request.trip_id)
            if not request.force_retranslate:
                rec_query = rec_query.filter(
                    (ActivityRecommendation.description_zh.is_(None)) |
                    (ActivityRecommendation.description_zh == "")
                )
            activities_to_translate.extend(rec_query.all())
            
            logger.info(f"Batch translating activities for trip {request.trip_id}")
        else:
            # Get all activities and recommendations
            activity_query = db.query(Activity)
            rec_query = db.query(ActivityRecommendation)
            
            if not request.force_retranslate:
                activity_query = activity_query.filter(
                    (Activity.description_zh.is_(None)) |
                    (Activity.description_zh == "")
                )
                rec_query = rec_query.filter(
                    (ActivityRecommendation.description_zh.is_(None)) |
                    (ActivityRecommendation.description_zh == "")
                )
            
            activities_to_translate.extend(activity_query.all())
            activities_to_translate.extend(rec_query.all())
            logger.info("Batch translating all activities in system")
        
        activities = activities_to_translate
        
        if not activities:
            return TranslationResponse(
                success=True,
                translated_count=0,
                skipped_count=0,
                error_count=0,
                message="No activities found that need translation"
            )
        
        logger.info(f"Found {len(activities)} activities to translate")
        
        # Process in batches to avoid overwhelming the API
        batch_size = 10
        total_translated = 0
        total_errors = 0
        all_errors = []
        
        for i in range(0, len(activities), batch_size):
            batch = activities[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(activities)-1)//batch_size + 1}")
            
            try:
                # Convert to dict format, handling different model types
                activities_for_translation = []
                for activity in batch:
                    activity_dict = {
                        "name": activity.name,
                        "description": activity.description or "",
                        "types": activity.category,
                        "category": activity.category
                    }
                    
                    # Add recommendation-specific fields if available
                    if hasattr(activity, 'external_rating'):
                        activity_dict["external_rating"] = activity.external_rating
                    if hasattr(activity, 'external_review_count'):
                        activity_dict["external_review_count"] = activity.external_review_count
                    
                    activities_for_translation.append(activity_dict)
                
                # Translate batch
                translated_batch = await translation_service.batch_translate_activities(
                    db, activities_for_translation,
                    request.source_language, request.target_language
                )
                
                # Update database
                for j, activity in enumerate(batch):
                    if j < len(translated_batch):
                        try:
                            translated = translated_batch[j]
                            
                            if translated.get("description_zh"):
                                activity.description_zh = translated["description_zh"]
                            if translated.get("cultural_notes_zh"):
                                activity.cultural_notes_zh = translated["cultural_notes_zh"]
                            if translated.get("tips_for_chinese_travelers"):
                                activity.tips_for_chinese_travelers = translated["tips_for_chinese_travelers"]
                            
                            total_translated += 1
                            
                        except Exception as e:
                            total_errors += 1
                            error_msg = f"Failed to update activity {activity.id}: {str(e)}"
                            all_errors.append(error_msg)
                            logger.error(error_msg)
                
                # Commit batch
                db.commit()
                logger.info(f"Committed batch {i//batch_size + 1}")
                
            except Exception as e:
                total_errors += len(batch)
                error_msg = f"Batch translation failed: {str(e)}"
                all_errors.append(error_msg)
                logger.error(error_msg)
        
        success_rate = total_translated / (total_translated + total_errors) if (total_translated + total_errors) > 0 else 1.0
        
        return TranslationResponse(
            success=success_rate > 0.8,  # Consider successful if >80% succeeded
            translated_count=total_translated,
            skipped_count=0,
            error_count=total_errors,
            errors=all_errors[:10],  # Limit error list to first 10
            message=f"Batch translation completed: {total_translated} translated, {total_errors} errors"
        )
        
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")


@router.get("/status/{trip_id}")
async def get_translation_status(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Get translation status for activities in a trip.
    
    Returns statistics about how many activities have been translated,
    useful for displaying progress and deciding whether to trigger translations.
    """
    try:
        # Validate trip exists
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # Get all activities for trip
        activities = db.query(ActivityRecommendation).filter(
            ActivityRecommendation.trip_id == trip_id
        ).all()
        
        # Count translation status
        total_activities = len(activities)
        translated_activities = len([
            a for a in activities 
            if a.description_zh and a.description_zh.strip()
        ])
        has_cultural_content = len([
            a for a in activities 
            if a.cultural_notes_zh and a.cultural_notes_zh.strip()
        ])
        has_travel_tips = len([
            a for a in activities 
            if a.tips_for_chinese_travelers and a.tips_for_chinese_travelers.strip()
        ])
        
        return {
            "trip_id": trip_id,
            "trip_name": trip.name,
            "total_activities": total_activities,
            "translated_activities": translated_activities,
            "translation_percentage": round((translated_activities / total_activities * 100) if total_activities > 0 else 0, 1),
            "has_cultural_content": has_cultural_content,
            "has_travel_tips": has_travel_tips,
            "needs_translation": total_activities - translated_activities,
            "fully_translated": translated_activities == total_activities
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/trigger/{trip_id}")
async def trigger_trip_translation(
    trip_id: int,
    background_tasks: BackgroundTasks,
    force_retranslate: bool = False,
    db: Session = Depends(get_db)
):
    """
    Convenient endpoint to trigger translation for all activities in a trip.
    
    This is a simplified wrapper around the batch translation endpoint,
    designed for easy integration with frontend "Translate" buttons.
    """
    request = BatchTranslationRequest(
        trip_id=trip_id,
        force_retranslate=force_retranslate,
        include_cultural_content=True
    )
    
    return await batch_translate_trip_activities(request, background_tasks, db)