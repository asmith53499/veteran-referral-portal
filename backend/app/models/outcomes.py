"""
Outcomes database model
"""

from sqlalchemy import Column, String, DateTime, Text, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class OutcomeStatusEnum(str, enum.Enum):
    """Outcome status enumeration"""
    RECEIVED = "RECEIVED"
    ENGAGED = "ENGAGED"
    WAITLIST = "WAITLIST"
    COMPLETED = "COMPLETED"
    UNREACHABLE = "UNREACHABLE"
    DECLINED = "DECLINED"
    TRANSFERRED = "TRANSFERRED"
    OTHER = "OTHER"

class ReasonCodeEnum(str, enum.Enum):
    """Reason code enumeration"""
    NO_SHOW = "NO_SHOW"
    CONTACT_FAILED = "CONTACT_FAILED"
    CAPACITY = "CAPACITY"
    INELIGIBLE = "INELIGIBLE"
    WITHDREW = "WITHDREW"
    COMPLETED_SUCCESSFULLY = "COMPLETED_SUCCESSFULLY"
    REFERRED_TO_OTHER_SERVICE = "REFERRED_TO_OTHER_SERVICE"
    OTHER_NONPII = "OTHER_NONPII"

class Outcome(Base):
    """Outcomes table model"""
    
    __tablename__ = "outcomes"
    
    # Primary key
    id = Column(String(255), primary_key=True, default=lambda: f"outcome_{func.now().strftime('%Y%m%d_%H%M%S')}_{func.random()}")
    
    # Foreign key to referral
    referral_token = Column(String(255), ForeignKey("referrals.referral_token"), nullable=False, index=True)
    
    # VSA that created this outcome
    vsa_id = Column(String(50), nullable=False, index=True)
    
    # Outcome details
    status = Column(Enum(OutcomeStatusEnum), nullable=False)
    reason_code = Column(Enum(ReasonCodeEnum), nullable=True)
    
    # Timestamps
    first_contact_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    updated_by = Column(String(100), nullable=False)  # VSA user ID
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Optional notes (non-PII only)
    notes = Column(Text, nullable=True)
    
    # Relationships
    referral = relationship("Referral", back_populates="outcomes")
    audit_logs = relationship("AuditLog", back_populates="outcome", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_outcomes_referral_token', 'referral_token'),
        Index('idx_outcomes_vsa_id', 'vsa_id'),
        Index('idx_outcomes_status', 'status'),
        Index('idx_outcomes_updated_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<Outcome(id={self.id}, referral_token={self.referral_token}, status={self.status})>"
