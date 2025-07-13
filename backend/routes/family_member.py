"""
Family Member CRUD API routes.

Provides REST endpoints for family member management.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from ..dependencies import DatabaseSession
from ..models import FamilyMember, MemberRole
from ..schemas import (
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
    FamilyMemberSummary,
)

router = APIRouter(prefix="/api/family-members", tags=["family-members"])


@router.post(
    "/", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED
)
def create_family_member(
    member_data: FamilyMemberCreate, db: DatabaseSession
) -> FamilyMemberResponse:
    """
    Create a new family member.

    Args:
        member_data: Family member creation data
        db: Database session

    Returns:
        Created family member object
    """
    try:
        # Validate image URL size if provided
        if member_data.profile_image_url and len(member_data.profile_image_url) > 1000000:  # 1MB limit for URL
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Profile image is too large. Please choose a smaller image (max 2MB)."
            )
        
        # Create new family member instance
        db_member = FamilyMember(**member_data.model_dump())
        db.add(db_member)
        db.commit()
        db.refresh(db_member)

        return FamilyMemberResponse.model_validate(db_member)

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "String too long" in error_msg or "Data too long" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Profile image is too large. Please choose a smaller image."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating family member: {error_msg}",
        )


@router.get("/", response_model=List[FamilyMemberSummary])
def get_family_members(
    db: DatabaseSession,
    trip_id: int = Query(None, description="Filter by trip ID"),
    role: MemberRole = Query(None, description="Filter by member role"),
    skip: int = 0,
    limit: int = 100,
) -> List[FamilyMemberSummary]:
    """
    Get family members with optional filtering.

    Args:
        db: Database session
        trip_id: Optional trip ID filter
        role: Optional role filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of family member summaries
    """
    query = db.query(FamilyMember)

    # Apply filters
    if trip_id:
        query = query.filter(FamilyMember.trip_id == trip_id)
    if role:
        query = query.filter(FamilyMember.role == role)

    # Apply pagination and ordering
    members = query.order_by(FamilyMember.name).offset(skip).limit(limit).all()

    return [FamilyMemberSummary.model_validate(member) for member in members]


@router.get("/{member_id}", response_model=FamilyMemberResponse)
def get_family_member(member_id: int, db: DatabaseSession) -> FamilyMemberResponse:
    """
    Get a specific family member by ID.

    Args:
        member_id: Family member identifier
        db: Database session

    Returns:
        Family member details
    """
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member with id {member_id} not found",
        )

    return FamilyMemberResponse.model_validate(member)


@router.put("/{member_id}", response_model=FamilyMemberResponse)
def update_family_member(
    member_id: int, member_update: FamilyMemberUpdate, db: DatabaseSession
) -> FamilyMemberResponse:
    """
    Update an existing family member.

    Args:
        member_id: Family member identifier
        member_update: Updated family member data
        db: Database session

    Returns:
        Updated family member object
    """
    # Get existing family member
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member with id {member_id} not found",
        )

    try:
        # Update only provided fields
        update_data = member_update.model_dump(exclude_unset=True)
        
        # Validate image URL size if provided
        if 'profile_image_url' in update_data and update_data['profile_image_url'] and len(update_data['profile_image_url']) > 1000000:  # 1MB limit for URL
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Profile image is too large. Please choose a smaller image (max 2MB)."
            )

        for field, value in update_data.items():
            setattr(member, field, value)

        db.commit()
        db.refresh(member)

        return FamilyMemberResponse.model_validate(member)

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "String too long" in error_msg or "Data too long" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Profile image is too large. Please choose a smaller image."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating family member: {error_msg}",
        )


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_family_member(member_id: int, db: DatabaseSession):
    """
    Delete a family member.

    Args:
        member_id: Family member identifier
        db: Database session
    """
    member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member with id {member_id} not found",
        )

    try:
        db.delete(member)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting family member: {str(e)}",
        )


@router.get("/trip/{trip_id}/summary")
def get_trip_family_summary(trip_id: int, db: DatabaseSession) -> dict:
    """
    Get family summary for a specific trip.

    Args:
        trip_id: Trip identifier
        db: Database session

    Returns:
        Family summary with member count, age distribution, etc.
    """
    members = db.query(FamilyMember).filter(FamilyMember.trip_id == trip_id).all()

    if not members:
        return {
            "trip_id": trip_id,
            "total_members": 0,
            "members": [],
            "age_distribution": {},
            "roles": {},
        }

    # Calculate age distribution
    age_groups = {"children": 0, "teens": 0, "adults": 0, "seniors": 0}
    roles = {"parent": 0, "child": 0, "adult": 0}

    for member in members:
        # Count roles
        roles[member.role.value] = roles.get(member.role.value, 0) + 1

        # Count age groups if age is provided
        if member.age is not None:
            if member.age < 13:
                age_groups["children"] += 1
            elif member.age < 18:
                age_groups["teens"] += 1
            elif member.age < 65:
                age_groups["adults"] += 1
            else:
                age_groups["seniors"] += 1

    return {
        "trip_id": trip_id,
        "total_members": len(members),
        "members": [FamilyMemberSummary.model_validate(m) for m in members],
        "age_distribution": age_groups,
        "roles": roles,
    }
