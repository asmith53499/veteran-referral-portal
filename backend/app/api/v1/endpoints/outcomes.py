"""
Outcomes API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import structlog
from sqlalchemy import func

from app.core.database import get_db
from app.models.outcomes import Outcome, OutcomeStatusEnum, ReasonCodeEnum
from app.models.referrals import Referral

logger = structlog.get_logger()
router = APIRouter()

@router.get("/")
async def list_outcomes(
    vsa_id: str = None,
    status: OutcomeStatusEnum = None,
    db: Session = Depends(get_db)
):
    """List outcomes with optional filtering"""
    try:
        query = db.query(Outcome)
        
        # Apply filters
        if vsa_id:
            query = query.filter(Outcome.vsa_id == vsa_id)
        if status:
            query = query.filter(Outcome.status == status)
        
        outcomes = query.all()
        return {"outcomes": outcomes, "total": len(outcomes)}
        
    except Exception as e:
        logger.error("Failed to list outcomes", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list outcomes")

@router.get("/{referral_token}")
async def get_outcome_by_referral(
    referral_token: str,
    db: Session = Depends(get_db)
):
    """Get outcome for a specific referral"""
    try:
        outcome = db.query(Outcome).filter(Outcome.referral_token == referral_token).first()
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome not found for this referral")
        
        return outcome
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get outcome", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get outcome")

@router.post("/{referral_token}")
async def create_outcome(
    referral_token: str,
    status: OutcomeStatusEnum,
    reason_code: ReasonCodeEnum = None,
    notes: str = None,
    vsa_id: str = None,
    db: Session = Depends(get_db)
):
    """Create or update outcome for a referral"""
    try:
        # Check if referral exists
        referral = db.query(Referral).filter(Referral.referral_token == referral_token).first()
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        # Check if outcome already exists
        existing_outcome = db.query(Outcome).filter(Outcome.referral_token == referral_token).first()
        
        if existing_outcome:
            # Update existing outcome
            existing_outcome.status = status
            existing_outcome.reason_code = reason_code
            existing_outcome.notes = notes
            existing_outcome.vsa_id = vsa_id or existing_outcome.vsa_id
            existing_outcome.updated_by = vsa_id or existing_outcome.vsa_id
            
            if status in [OutcomeStatusEnum.COMPLETED, OutcomeStatusEnum.DECLINED, OutcomeStatusEnum.TRANSFERRED]:
                existing_outcome.closed_at = func.now()
            
            db.commit()
            db.refresh(existing_outcome)
            
            logger.info("Outcome updated", referral_token=referral_token, status=status, vsa_id=vsa_id)
            return existing_outcome
        else:
            # Create new outcome
            outcome_data = {
                'referral_token': referral_token,
                'vsa_id': vsa_id or referral.vsa_id,
                'status': status,
                'reason_code': reason_code,
                'notes': notes,
                'updated_by': vsa_id or referral.vsa_id,
                'first_contact_at': func.now()
            }
            
            if status in [OutcomeStatusEnum.COMPLETED, OutcomeStatusEnum.DECLINED, OutcomeStatusEnum.TRANSFERRED]:
                outcome_data['closed_at'] = func.now()
            
            new_outcome = Outcome(**outcome_data)
            db.add(new_outcome)
            db.commit()
            db.refresh(new_outcome)
            
            logger.info("Outcome created", referral_token=referral_token, status=status, vsa_id=vsa_id)
            return new_outcome
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to create/update outcome", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create/update outcome")
