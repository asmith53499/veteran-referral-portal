"""
Pydantic schemas for referral data validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.referrals import (
    ProgramCodeEnum, ReferralTypeEnum, PriorityLevelEnum, 
    CrisisTypeEnum, UrgencyIndicatorEnum
)

class ReferralBase(BaseModel):
    """Base referral schema"""
    vsa_id: str = Field(..., min_length=1, max_length=50, description="VSA identifier")
    program_code: ProgramCodeEnum = Field(..., description="Program code for the referral")
    episode_id: Optional[str] = Field(None, max_length=100, description="Episode identifier")
    referral_type: ReferralTypeEnum = Field(..., description="Type of referral")
    priority_level: PriorityLevelEnum = Field(..., description="Priority level")
    crisis_type: Optional[CrisisTypeEnum] = Field(None, description="Type of crisis")
    urgency_indicator: Optional[UrgencyIndicatorEnum] = Field(None, description="Urgency indicator")
    expected_contact_date: Optional[datetime] = Field(None, description="Expected contact date")
    va_facility_code: Optional[str] = Field(None, max_length=50, description="VA facility code")

class ReferralCreate(ReferralBase):
    """Schema for creating a new referral"""
    referral_token: UUID = Field(..., description="Referral token")
    issued_at: datetime = Field(..., description="When the referral was issued")

class ReferralUpdate(BaseModel):
    """Schema for updating a referral"""
    crisis_type: Optional[CrisisTypeEnum] = None
    urgency_indicator: Optional[UrgencyIndicatorEnum] = None
    expected_contact_date: Optional[datetime] = None
    va_facility_code: Optional[str] = Field(None, max_length=50)

class ReferralResponse(ReferralBase):
    """Schema for referral response"""
    referral_token: UUID
    issued_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReferralListResponse(BaseModel):
    """Schema for list of referrals"""
    referrals: list[ReferralResponse]
    total: int
    page: int
    size: int

class ReferralImportRequest(BaseModel):
    """Schema for CSV import request"""
    vsa_id: str = Field(..., description="VSA identifier for the import")
    import_notes: Optional[str] = Field(None, max_length=500, description="Notes about the import")

class ReferralImportResponse(BaseModel):
    """Schema for CSV import response"""
    import_id: str
    total_rows: int
    successful_imports: int
    failed_imports: int
    errors: list[str]
    timestamp: datetime
