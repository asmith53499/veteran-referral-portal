"""
Pydantic schemas for outcome data validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.outcomes import OutcomeStatusEnum, ReasonCodeEnum

class OutcomeBase(BaseModel):
    """Base outcome schema"""
    status: OutcomeStatusEnum = Field(..., description="Outcome status")
    reason_code: Optional[ReasonCodeEnum] = Field(None, description="Reason code for the outcome")
    first_contact_at: Optional[datetime] = Field(None, description="When first contact was made")
    closed_at: Optional[datetime] = Field(None, description="When the case was closed")
    notes: Optional[str] = Field(None, max_length=1000, description="Non-PII notes about the outcome")

class OutcomeCreate(OutcomeBase):
    """Schema for creating a new outcome"""
    referral_token: str = Field(..., description="Referral token")
    vsa_id: str = Field(..., min_length=1, max_length=50, description="VSA identifier")

class OutcomeUpdate(BaseModel):
    """Schema for updating an outcome"""
    status: Optional[OutcomeStatusEnum] = Field(None, description="Outcome status")
    reason_code: Optional[ReasonCodeEnum] = Field(None, description="Reason code for the outcome")
    first_contact_at: Optional[datetime] = Field(None, description="When first contact was made")
    closed_at: Optional[datetime] = Field(None, description="When the case was closed")
    notes: Optional[str] = Field(None, max_length=1000, description="Non-PII notes about the outcome")

class OutcomeResponse(OutcomeBase):
    """Schema for outcome response"""
    id: UUID
    referral_token: UUID
    vsa_id: str
    updated_by: str
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OutcomeListResponse(BaseModel):
    """Schema for list of outcomes"""
    outcomes: list[OutcomeResponse]
    total: int
    page: int
    size: int

class OutcomeStatsResponse(BaseModel):
    """Schema for outcome statistics"""
    total_outcomes: int
    by_status: dict[str, int]
    by_reason: dict[str, int]
    avg_time_to_contact: Optional[float] = None
    avg_time_to_close: Optional[float] = None
    vsa_id: Optional[str] = None

class OutcomeBulkCreate(BaseModel):
    """Schema for bulk outcome creation"""
    outcomes: list[OutcomeCreate] = Field(..., min_items=1, max_items=100, description="List of outcomes to create")

class OutcomeBulkResponse(BaseModel):
    """Schema for bulk outcome response"""
    created: int
    failed: int
    errors: list[str]
    outcomes: list[OutcomeResponse]
