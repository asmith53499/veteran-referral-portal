"""
Referrals database model
"""

from sqlalchemy import Column, String, DateTime, Text, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ProgramCodeEnum(str, enum.Enum):
    """Program code enumeration"""
    CRISIS_INTERVENTION = "CRISIS_INTERVENTION"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    HOUSING_ASSISTANCE = "HOUSING_ASSISTANCE"
    SUBSTANCE_ABUSE = "SUBSTANCE_ABUSE"
    EMPLOYMENT = "EMPLOYMENT"
    BENEFITS_NAVIGATION = "BENEFITS_NAVIGATION"
    LEGAL_AID = "LEGAL_AID"
    OTHER = "OTHER"

class ReferralTypeEnum(str, enum.Enum):
    """Referral type enumeration"""
    CRISIS_HOTLINE = "CRISIS_HOTLINE"
    CLINICAL_REFERRAL = "CLINICAL_REFERRAL"
    SELF_REFERRAL = "SELF_REFERRAL"
    COMMUNITY_REFERRAL = "COMMUNITY_REFERRAL"
    OTHER = "OTHER"

class PriorityLevelEnum(str, enum.Enum):
    """Priority level enumeration"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CrisisTypeEnum(str, enum.Enum):
    """Crisis type enumeration"""
    SUICIDE_RISK = "SUICIDE_RISK"
    HOMELESSNESS = "HOMELESSNESS"
    SUBSTANCE_ABUSE = "SUBSTANCE_ABUSE"
    DEPRESSION = "DEPRESSION"
    ANXIETY = "ANXIETY"
    PTSD = "PTSD"
    DOMESTIC_VIOLENCE = "DOMESTIC_VIOLENCE"
    FINANCIAL_CRISIS = "FINANCIAL_CRISIS"
    OTHER = "OTHER"

class UrgencyIndicatorEnum(str, enum.Enum):
    """Urgency indicator enumeration"""
    IMMEDIATE = "IMMEDIATE"
    WITHIN_24H = "WITHIN_24H"
    WITHIN_72H = "WITHIN_72H"
    WITHIN_WEEK = "WITHIN_WEEK"
    STANDARD = "STANDARD"

class Referral(Base):
    """Referrals table model"""
    
    __tablename__ = "referrals"
    
    # Primary key
    referral_token = Column(String(255), primary_key=True, index=True)
    
    # Required fields
    issued_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    vsa_id = Column(String(50), nullable=False, index=True)
    program_code = Column(Enum(ProgramCodeEnum), nullable=False)
    episode_id = Column(String(100), nullable=True)
    referral_type = Column(Enum(ReferralTypeEnum), nullable=False)
    priority_level = Column(Enum(PriorityLevelEnum), nullable=False)
    
    # Optional fields
    crisis_type = Column(Enum(CrisisTypeEnum), nullable=True)
    urgency_indicator = Column(Enum(UrgencyIndicatorEnum), nullable=True)
    expected_contact_date = Column(DateTime(timezone=True), nullable=True)
    va_facility_code = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    outcomes = relationship("Outcome", back_populates="referral", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="referral", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_referrals_vsa_id', 'vsa_id'),
        Index('idx_referrals_program_code', 'program_code'),
        Index('idx_referrals_issued_at', 'issued_at'),
        Index('idx_referrals_priority_level', 'priority_level'),
    )
    
    def __repr__(self):
        return f"<Referral(token={self.referral_token}, vsa_id={self.vsa_id}, program_code={self.program_code})>"
