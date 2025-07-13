"""
Voting API routes for activity recommendations.

Endpoints for family voting and commenting on activity recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import ActivityVote, ActivityComment, ActivityRecommendation, FamilyMember, Trip
from ..schemas.activity_vote import (
    ActivityVoteCreate,
    ActivityVoteUpdate,
    ActivityVoteResponse,
    ActivityCommentCreate,
    ActivityCommentUpdate,
    ActivityCommentResponse,
    VotingDashboardResponse,
    RecommendationWithVotes,
    FamilyMemberVoteInfo
)

router = APIRouter(prefix="/api/voting", tags=["voting"])


@router.post("/votes", response_model=ActivityVoteResponse)
def create_vote(
    vote_data: ActivityVoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update a family member's vote on an activity recommendation.
    
    Each family member can only vote once per recommendation.
    If they vote again, their previous vote is updated.
    """
    # Validate vote_type
    if vote_data.vote_type not in ["positive", "negative", "neutral"]:
        raise HTTPException(
            status_code=400, 
            detail="Vote type must be 'positive', 'negative', or 'neutral'"
        )
    
    # Check if recommendation exists
    recommendation = db.query(ActivityRecommendation).filter(
        ActivityRecommendation.id == vote_data.recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Check if family member exists
    family_member = db.query(FamilyMember).filter(
        FamilyMember.id == vote_data.family_member_id
    ).first()
    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")
    
    # Check if vote already exists
    existing_vote = db.query(ActivityVote).filter(
        ActivityVote.recommendation_id == vote_data.recommendation_id,
        ActivityVote.family_member_id == vote_data.family_member_id
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.vote_type = vote_data.vote_type
        db.commit()
        db.refresh(existing_vote)
        return existing_vote
    else:
        # Create new vote
        vote = ActivityVote(
            recommendation_id=vote_data.recommendation_id,
            family_member_id=vote_data.family_member_id,
            vote_type=vote_data.vote_type
        )
        db.add(vote)
        db.commit()
        db.refresh(vote)
        return vote


@router.get("/votes", response_model=List[ActivityVoteResponse])
def get_votes(
    recommendation_id: Optional[int] = Query(None, description="Filter by recommendation ID"),
    family_member_id: Optional[int] = Query(None, description="Filter by family member ID"),
    trip_id: Optional[int] = Query(None, description="Filter by trip ID"),
    db: Session = Depends(get_db)
):
    """Get votes with optional filtering."""
    query = db.query(ActivityVote)
    
    if recommendation_id is not None:
        query = query.filter(ActivityVote.recommendation_id == recommendation_id)
    
    if family_member_id is not None:
        query = query.filter(ActivityVote.family_member_id == family_member_id)
    
    if trip_id is not None:
        # Join with recommendations to filter by trip
        query = query.join(ActivityRecommendation).filter(
            ActivityRecommendation.trip_id == trip_id
        )
    
    votes = query.all()
    return votes


@router.put("/votes/{vote_id}", response_model=ActivityVoteResponse)
def update_vote(
    vote_id: int,
    vote_update: ActivityVoteUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing vote."""
    # Validate vote_type
    if vote_update.vote_type not in ["positive", "negative", "neutral"]:
        raise HTTPException(
            status_code=400, 
            detail="Vote type must be 'positive', 'negative', or 'neutral'"
        )
    
    vote = db.query(ActivityVote).filter(ActivityVote.id == vote_id).first()
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    vote.vote_type = vote_update.vote_type
    db.commit()
    db.refresh(vote)
    return vote


@router.delete("/votes/{vote_id}")
def delete_vote(
    vote_id: int,
    db: Session = Depends(get_db)
):
    """Delete a vote."""
    vote = db.query(ActivityVote).filter(ActivityVote.id == vote_id).first()
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    db.delete(vote)
    db.commit()
    return {"message": "Vote deleted successfully"}


@router.post("/comments", response_model=ActivityCommentResponse)
def create_comment(
    comment_data: ActivityCommentCreate,
    db: Session = Depends(get_db)
):
    """Create a comment on an activity recommendation."""
    # Check if recommendation exists
    recommendation = db.query(ActivityRecommendation).filter(
        ActivityRecommendation.id == comment_data.recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Check if family member exists
    family_member = db.query(FamilyMember).filter(
        FamilyMember.id == comment_data.family_member_id
    ).first()
    if not family_member:
        raise HTTPException(status_code=404, detail="Family member not found")
    
    comment = ActivityComment(
        recommendation_id=comment_data.recommendation_id,
        family_member_id=comment_data.family_member_id,
        comment_text=comment_data.comment_text
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/comments", response_model=List[ActivityCommentResponse])
def get_comments(
    recommendation_id: Optional[int] = Query(None, description="Filter by recommendation ID"),
    family_member_id: Optional[int] = Query(None, description="Filter by family member ID"),
    db: Session = Depends(get_db)
):
    """Get comments with optional filtering."""
    query = db.query(ActivityComment)
    
    if recommendation_id is not None:
        query = query.filter(ActivityComment.recommendation_id == recommendation_id)
    
    if family_member_id is not None:
        query = query.filter(ActivityComment.family_member_id == family_member_id)
    
    comments = query.order_by(ActivityComment.created_at.desc()).all()
    return comments


@router.put("/comments/{comment_id}", response_model=ActivityCommentResponse)
def update_comment(
    comment_id: int,
    comment_update: ActivityCommentUpdate,
    db: Session = Depends(get_db)
):
    """Update a comment."""
    comment = db.query(ActivityComment).filter(ActivityComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment.comment_text = comment_update.comment_text
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Delete a comment."""
    comment = db.query(ActivityComment).filter(ActivityComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


@router.get("/dashboard/{trip_id}", response_model=VotingDashboardResponse)
def get_voting_dashboard(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive voting dashboard for a trip.
    
    Returns all recommendations with vote details, family member info,
    and voting statistics for the dashboard view.
    """
    # Get trip
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Get family members
    family_members = db.query(FamilyMember).filter(FamilyMember.trip_id == trip_id).all()
    family_member_data = [
        {"id": fm.id, "name": fm.name, "role": fm.role.value}
        for fm in family_members
    ]
    
    # Get recommendations with votes and comments
    recommendations = db.query(ActivityRecommendation).filter(
        ActivityRecommendation.trip_id == trip_id,
        ActivityRecommendation.is_active == True
    ).all()
    
    recommendations_with_votes = []
    total_votes = 0
    total_recommendations = len(recommendations)
    vote_distribution = {"positive": 0, "negative": 0, "neutral": 0}
    
    for rec in recommendations:
        # Get votes for this recommendation
        votes = db.query(ActivityVote).filter(
            ActivityVote.recommendation_id == rec.id
        ).all()
        
        # Get comments for this recommendation
        comments = db.query(ActivityComment).filter(
            ActivityComment.recommendation_id == rec.id
        ).order_by(ActivityComment.created_at.desc()).all()
        
        # Build family vote info
        family_votes = []
        votes_by_member = {vote.family_member_id: vote for vote in votes}
        
        for fm in family_members:
            vote = votes_by_member.get(fm.id)
            family_votes.append(FamilyMemberVoteInfo(
                family_member_id=fm.id,
                family_member_name=fm.name,
                vote_type=vote.vote_type if vote else None,
                has_voted=vote is not None
            ))
        
        # Calculate vote summary
        vote_summary = rec.vote_summary
        total_votes += vote_summary["total"]
        
        # Update vote distribution
        for vote in votes:
            vote_distribution[vote.vote_type] += 1
        
        recommendations_with_votes.append(RecommendationWithVotes(
            recommendation_id=rec.id,
            recommendation_name=rec.name,
            vote_summary=vote_summary,
            family_votes=family_votes,
            comments=[ActivityCommentResponse(
                id=comment.id,
                recommendation_id=comment.recommendation_id,
                family_member_id=comment.family_member_id,
                comment_text=comment.comment_text,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            ) for comment in comments]
        ))
    
    # Calculate voting statistics
    voting_statistics = {
        "total_recommendations": total_recommendations,
        "total_votes": total_votes,
        "total_family_members": len(family_members),
        "vote_distribution": vote_distribution,
        "average_votes_per_recommendation": total_votes / total_recommendations if total_recommendations > 0 else 0,
        "voting_participation_rate": (total_votes / (total_recommendations * len(family_members))) if total_recommendations > 0 and len(family_members) > 0 else 0
    }
    
    return VotingDashboardResponse(
        trip_id=trip_id,
        trip_name=trip.name,
        family_members=family_member_data,
        recommendations_with_votes=recommendations_with_votes,
        voting_statistics=voting_statistics
    )