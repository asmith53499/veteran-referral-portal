"""
Referrals API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import csv
import io
import structlog
from datetime import datetime
import uuid
from uuid import UUID

from app.core.database import get_db
from app.models.referrals import Referral, ProgramCodeEnum, ReferralTypeEnum, PriorityLevelEnum
from app.schemas.referrals import (
    ReferralCreate, ReferralResponse, ReferralListResponse, 
    ReferralImportRequest, ReferralImportResponse
)
from app.core.pii_detector import detect_pii

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=ReferralResponse)
async def create_referral(
    referral: ReferralCreate,
    db: Session = Depends(get_db)
):
    """Create a new referral"""
    try:
        # Check if referral token already exists
        existing = db.query(Referral).filter(Referral.referral_token == referral.referral_token).first()
        if existing:
            raise HTTPException(status_code=400, detail="Referral token already exists")
        
        # Create new referral
        db_referral = Referral(**referral.dict())
        db.add(db_referral)
        db.commit()
        db.refresh(db_referral)
        
        logger.info("Referral created", referral_token=referral.referral_token, vsa_id=referral.vsa_id)
        return db_referral
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to create referral", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create referral")

@router.get("/", response_model=ReferralListResponse)
async def list_referrals(
    vsa_id: str = None,
    program_code: ProgramCodeEnum = None,
    page: int = 1,
    size: int = 100,
    db: Session = Depends(get_db)
):
    """List referrals with optional filtering"""
    try:
        query = db.query(Referral)
        
        # Apply filters
        if vsa_id:
            query = query.filter(Referral.vsa_id == vsa_id)
        if program_code:
            query = query.filter(Referral.program_code == program_code)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        referrals = query.offset((page - 1) * size).limit(size).all()
        
        return ReferralListResponse(
            referrals=referrals,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error("Failed to list referrals", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list referrals")

@router.get("/{referral_token}", response_model=ReferralResponse)
async def get_referral(
    referral_token: str,
    db: Session = Depends(get_db)
):
    """Get a specific referral by token"""
    try:
        referral = db.query(Referral).filter(Referral.referral_token == referral_token).first()
        if not referral:
            raise HTTPException(status_code=404, detail="Referral not found")
        
        return referral
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get referral", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get referral")

@router.post("/import/csv", response_model=ReferralImportResponse)
async def import_referrals_csv(
    file: UploadFile = File(...),
    vsa_id: str = Form(...),
    import_notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Import referrals from CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(csv_reader)
        
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Validate required columns
        required_columns = ['referral_token', 'issued_at', 'vsa_id', 'program_code', 'referral_type', 'priority_level']
        missing_columns = [col for col in required_columns if col not in rows[0].keys()]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process each row
        successful_imports = 0
        failed_imports = 0
        errors = []
        
        for index, row in enumerate(rows):
            try:
                # Check for PII in the row
                row_text = ' '.join(str(val) for val in row.values() if val and val.strip())
                if detect_pii(row_text):
                    errors.append(f"Row {index + 1}: PII detected - row skipped")
                    failed_imports += 1
                    continue
                
                # Validate data types and values
                try:
                    issued_at = datetime.fromisoformat(row['issued_at'].replace('Z', '+00:00'))
                except ValueError:
                    errors.append(f"Row {index + 1}: Invalid issued_at format - {row['issued_at']}")
                    failed_imports += 1
                    continue
                
                referral_data = {
                    'referral_token': UUID(row['referral_token']),
                    'issued_at': issued_at,
                    'vsa_id': str(row['vsa_id']),
                    'program_code': row['program_code'],
                    'episode_id': str(row['episode_id']) if row.get('episode_id') and row['episode_id'].strip() else None,
                    'referral_type': row['referral_type'],
                    'priority_level': row['priority_level'],
                    'crisis_type': row.get('crisis_type') if row.get('crisis_type') and row['crisis_type'].strip() else None,
                    'urgency_indicator': row.get('urgency_indicator') if row.get('urgency_indicator') and row['urgency_indicator'].strip() else None,
                    'expected_contact_date': datetime.fromisoformat(row['expected_contact_date'].replace('Z', '+00:00')) if row.get('expected_contact_date') and row['expected_contact_date'].strip() else None,
                    'va_facility_code': str(row['va_facility_code']) if row.get('va_facility_code') and row['va_facility_code'].strip() else None,
                }
                
                # Check if referral already exists
                existing = db.query(Referral).filter(Referral.referral_token == UUID(row['referral_token'])).first()
                if existing:
                    errors.append(f"Row {index + 1}: Referral token {row['referral_token']} already exists")
                    failed_imports += 1
                    continue
                
                # Create referral
                db_referral = Referral(**referral_data)
                db.add(db_referral)
                successful_imports += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                failed_imports += 1
        
        # Commit all successful imports
        if successful_imports > 0:
            db.commit()
        
        # Create import response
        import_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        logger.info("CSV import completed", 
                   import_id=import_id, 
                   vsa_id=vsa_id, 
                   successful=successful_imports, 
                   failed=failed_imports)
        
        return ReferralImportResponse(
            import_id=import_id,
            total_rows=len(rows),
            successful_imports=successful_imports,
            failed_imports=failed_imports,
            errors=errors,
            timestamp=timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("CSV import failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"CSV import failed: {str(e)}")

@router.get("/summary/stats")
async def get_referral_stats(
    vsa_id: str = None,
    db: Session = Depends(get_db)
):
    """Get referral statistics"""
    try:
        query = db.query(Referral)
        
        if vsa_id:
            query = query.filter(Referral.vsa_id == vsa_id)
        
        # Get counts by program code
        program_stats = db.query(
            Referral.program_code,
            func.count(Referral.referral_token)
        ).group_by(Referral.program_code).all()
        
        # Get counts by priority level
        priority_stats = db.query(
            Referral.priority_level,
            func.count(Referral.referral_token)
        ).group_by(Referral.priority_level).all()
        
        # Get total count
        total_referrals = query.count()
        
        return {
            "total_referrals": total_referrals,
            "by_program": dict(program_stats),
            "by_priority": dict(priority_stats),
            "vsa_id": vsa_id
        }
        
    except Exception as e:
        logger.error("Failed to get referral stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get referral stats")
