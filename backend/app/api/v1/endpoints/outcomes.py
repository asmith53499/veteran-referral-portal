"""
Outcomes API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import structlog
import uuid

from app.core.database import get_db
from app.core.auth import get_current_active_user, require_vsa_access
from app.models.outcomes import Outcome, OutcomeStatusEnum, ReasonCodeEnum
from app.models.referrals import Referral
from app.models.users import User
from app.schemas.outcomes import (
    OutcomeCreate, OutcomeUpdate, OutcomeResponse, OutcomeListResponse,
    OutcomeStatsResponse, OutcomeBulkCreate, OutcomeBulkResponse
)

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=OutcomeResponse)
async def create_outcome(
    outcome_data: OutcomeCreate,
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Create a new outcome for a referral"""
    try:
        # Verify the referral exists and belongs to the VSA
        referral = db.query(Referral).filter(Referral.referral_token == outcome_data.referral_token).first()
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        if referral.vsa_id != current_user.vsa_id:
            raise HTTPException(status_code=403, detail="Access denied - referral belongs to different VSA")
        
        # Check if outcome already exists for this referral
        existing_outcome = db.query(Outcome).filter(Outcome.referral_token == outcome_data.referral_token).first()
        if existing_outcome:
            raise HTTPException(status_code=400, detail="Outcome already exists for this referral")
        
        # Create outcome
        db_outcome = Outcome(
            id=str(uuid.uuid4()),
            referral_token=outcome_data.referral_token,
            vsa_id=current_user.vsa_id,
            status=outcome_data.status,
            reason_code=outcome_data.reason_code,
            first_contact_at=outcome_data.first_contact_at,
            closed_at=outcome_data.closed_at,
            notes=outcome_data.notes,
            updated_by=current_user.id
        )
        
        db.add(db_outcome)
        db.commit()
        db.refresh(db_outcome)
        
        logger.info("Outcome created", 
                   outcome_id=db_outcome.id, 
                   referral_token=db_outcome.referral_token,
                   status=db_outcome.status,
                   user_id=current_user.id)
        
        return db_outcome
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to create outcome", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create outcome")

@router.get("/", response_model=OutcomeListResponse)
async def list_outcomes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(100, ge=1, le=1000, description="Page size"),
    status: Optional[OutcomeStatusEnum] = Query(None, description="Filter by status"),
    reason_code: Optional[ReasonCodeEnum] = Query(None, description="Filter by reason code"),
    referral_token: Optional[str] = Query(None, description="Filter by referral token"),
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """List outcomes for the current VSA"""
    try:
        query = db.query(Outcome).filter(Outcome.vsa_id == current_user.vsa_id)
        
        # Apply filters
        if status:
            query = query.filter(Outcome.status == status)
        if reason_code:
            query = query.filter(Outcome.reason_code == reason_code)
        if referral_token:
            query = query.filter(Outcome.referral_token == referral_token)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        outcomes = query.order_by(Outcome.updated_at.desc()).offset((page - 1) * size).limit(size).all()
        
        return OutcomeListResponse(
            outcomes=outcomes,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error("Failed to list outcomes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list outcomes")

@router.get("/{outcome_id}", response_model=OutcomeResponse)
async def get_outcome(
    outcome_id: str,
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Get a specific outcome"""
    try:
        outcome = db.query(Outcome).filter(
            Outcome.id == outcome_id,
            Outcome.vsa_id == current_user.vsa_id
        ).first()
        
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found")
        
        return outcome
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get outcome", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get outcome")

@router.put("/{outcome_id}", response_model=OutcomeResponse)
async def update_outcome(
    outcome_id: str,
    outcome_data: OutcomeUpdate,
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Update an outcome"""
    try:
        outcome = db.query(Outcome).filter(
            Outcome.id == outcome_id,
            Outcome.vsa_id == current_user.vsa_id
        ).first()
        
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found")
        
        # Update fields
        update_data = outcome_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(outcome, field, value)
        
        outcome.updated_by = current_user.id
        outcome.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(outcome)
        
        logger.info("Outcome updated", 
                   outcome_id=outcome.id, 
                   status=outcome.status,
                   user_id=current_user.id)
        
        return outcome
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to update outcome", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update outcome")

@router.post("/bulk", response_model=OutcomeBulkResponse)
async def create_bulk_outcomes(
    bulk_data: OutcomeBulkCreate,
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Create multiple outcomes in bulk"""
    try:
        created_outcomes = []
        failed_count = 0
        errors = []
        
        for i, outcome_data in enumerate(bulk_data.outcomes):
            try:
                # Verify the referral exists and belongs to the VSA
                referral = db.query(Referral).filter(Referral.referral_token == outcome_data.referral_token).first()
                if not referral:
                    errors.append(f"Row {i+1}: Referral not found")
                    failed_count += 1
                    continue
                
                if referral.vsa_id != current_user.vsa_id:
                    errors.append(f"Row {i+1}: Access denied - referral belongs to different VSA")
                    failed_count += 1
                    continue
                
                # Check if outcome already exists
                existing_outcome = db.query(Outcome).filter(Outcome.referral_token == outcome_data.referral_token).first()
                if existing_outcome:
                    errors.append(f"Row {i+1}: Outcome already exists for this referral")
                    failed_count += 1
                    continue
                
                # Create outcome
                db_outcome = Outcome(
                    id=str(uuid.uuid4()),
                    referral_token=outcome_data.referral_token,
                    vsa_id=current_user.vsa_id,
                    status=outcome_data.status,
                    reason_code=outcome_data.reason_code,
                    first_contact_at=outcome_data.first_contact_at,
                    closed_at=outcome_data.closed_at,
                    notes=outcome_data.notes,
                    updated_by=current_user.id
                )
                
                db.add(db_outcome)
                created_outcomes.append(db_outcome)
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
                failed_count += 1
        
        # Commit all successful creations
        if created_outcomes:
            db.commit()
            # Refresh each outcome individually to avoid UUID issues
            for outcome in created_outcomes:
                db.refresh(outcome)
        
        logger.info("Bulk outcomes created", 
                   created=len(created_outcomes),
                   failed=failed_count,
                   user_id=current_user.id)
        
        return OutcomeBulkResponse(
            created=len(created_outcomes),
            failed=failed_count,
            errors=errors,
            outcomes=created_outcomes
        )
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to create bulk outcomes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create bulk outcomes")

@router.get("/summary/stats", response_model=OutcomeStatsResponse)
async def get_outcome_stats(
    vsa_id: Optional[str] = Query(None, description="VSA ID filter (VA admin only)"),
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Get outcome statistics"""
    try:
        # VA admins can view any VSA stats, VSA users can only view their own
        if current_user.role == "VA_ADMIN" and vsa_id:
            target_vsa_id = vsa_id
        else:
            target_vsa_id = current_user.vsa_id
        
        query = db.query(Outcome).filter(Outcome.vsa_id == target_vsa_id)
        
        # Get counts by status
        status_stats = db.query(
            Outcome.status,
            func.count(Outcome.id)
        ).filter(Outcome.vsa_id == target_vsa_id).group_by(Outcome.status).all()
        
        # Get counts by reason code
        reason_stats = db.query(
            Outcome.reason_code,
            func.count(Outcome.id)
        ).filter(
            Outcome.vsa_id == target_vsa_id,
            Outcome.reason_code.isnot(None)
        ).group_by(Outcome.reason_code).all()
        
        # Get total count
        total_outcomes = query.count()
        
        # Calculate average time to contact (if first_contact_at is available)
        avg_contact_time = None
        contact_times = db.query(
            func.avg(
                func.extract('epoch', Outcome.first_contact_at - Referral.issued_at) / 3600
            )
        ).join(Referral, Outcome.referral_token == Referral.referral_token).filter(
            Outcome.vsa_id == target_vsa_id,
            Outcome.first_contact_at.isnot(None)
        ).scalar()
        
        if contact_times:
            avg_contact_time = float(contact_times)
        
        # Calculate average time to close (if closed_at is available)
        avg_close_time = None
        close_times = db.query(
            func.avg(
                func.extract('epoch', Outcome.closed_at - Referral.issued_at) / 3600
            )
        ).join(Referral, Outcome.referral_token == Referral.referral_token).filter(
            Outcome.vsa_id == target_vsa_id,
            Outcome.closed_at.isnot(None)
        ).scalar()
        
        if close_times:
            avg_close_time = float(close_times)
        
        return OutcomeStatsResponse(
            total_outcomes=total_outcomes,
            by_status=dict(status_stats),
            by_reason=dict(reason_stats),
            avg_time_to_contact=avg_contact_time,
            avg_time_to_close=avg_close_time,
            vsa_id=target_vsa_id
        )
        
    except Exception as e:
        logger.error("Failed to get outcome stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get outcome stats")

@router.get("/referral/{referral_token}", response_model=OutcomeResponse)
async def get_outcome_by_referral(
    referral_token: str,
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Get outcome for a specific referral"""
    try:
        # Verify the referral exists and belongs to the VSA
        referral = db.query(Referral).filter(Referral.referral_token == referral_token).first()
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        if referral.vsa_id != current_user.vsa_id:
            raise HTTPException(status_code=403, detail="Access denied - referral belongs to different VSA")
        
        # Get the outcome
        outcome = db.query(Outcome).filter(Outcome.referral_token == referral_token).first()
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found for this referral")
        
        return outcome
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get outcome by referral", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get outcome by referral")

@router.delete("/{outcome_id}")
async def delete_outcome(
    outcome_id: str,
    current_user: User = Depends(require_vsa_access()),
    db: Session = Depends(get_db)
):
    """Delete an outcome (soft delete by marking as OTHER status)"""
    try:
        outcome = db.query(Outcome).filter(
            Outcome.id == outcome_id,
            Outcome.vsa_id == current_user.vsa_id
        ).first()
        
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found")
        
        # Soft delete by changing status to OTHER
        outcome.status = OutcomeStatusEnum.OTHER
        outcome.reason_code = ReasonCodeEnum.OTHER_NONPII
        outcome.notes = f"Deleted by {current_user.username} on {datetime.utcnow().isoformat()}"
        outcome.updated_by = current_user.id
        outcome.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info("Outcome soft deleted", 
                   outcome_id=outcome.id,
                   user_id=current_user.id)
        
        return {"message": "Outcome deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete outcome", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete outcome")
