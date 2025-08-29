"""
Audit Log database model for WORM compliance
"""

from sqlalchemy import Column, String, DateTime, Text, Enum, Index, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class AuditActionEnum(str, enum.Enum):
    """Audit action enumeration"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    STATUS_CHANGE = "STATUS_CHANGE"
    CSV_IMPORT = "CSV_IMPORT"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    ACCESS_DENIED = "ACCESS_DENIED"

class AuditResourceEnum(str, enum.Enum):
    """Audit resource enumeration"""
    REFERRAL = "REFERRAL"
    OUTCOME = "OUTCOME"
    USER = "USER"
    SYSTEM = "SYSTEM"

class AuditLog(Base):
    """Audit log table model for WORM compliance"""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(String(255), primary_key=True, default=lambda: f"audit_{func.now().strftime('%Y%m%d_%H%M%S')}_{func.random()}")
    
    # Timestamp (immutable)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # User/actor information
    user_id = Column(String(100), nullable=False, index=True)
    vsa_id = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Action details
    action = Column(Enum(AuditActionEnum), nullable=False)
    resource_type = Column(Enum(AuditResourceEnum), nullable=False)
    resource_id = Column(String(255), nullable=True, index=True)
    
    # Change details
    old_values = Column(JSON, nullable=True)  # Previous state
    new_values = Column(JSON, nullable=True)  # New state
    change_summary = Column(Text, nullable=True)  # Human-readable summary
    
    # Context
    session_id = Column(String(255), nullable=True)
    request_id = Column(String(255), nullable=True)
    
    # Foreign keys (optional, for related records)
    referral_token = Column(String(255), ForeignKey("referrals.referral_token"), nullable=True, index=True)
    outcome_id = Column(String(255), ForeignKey("outcomes.id"), nullable=True, index=True)
    
    # Relationships
    referral = relationship("Referral", back_populates="audit_logs")
    outcome = relationship("Outcome", back_populates="audit_logs")
    
    # Indexes for performance and compliance
    __table_args__ = (
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_vsa_id', 'vsa_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource_type', 'resource_type'),
        Index('idx_audit_logs_resource_id', 'resource_id'),
        Index('idx_audit_logs_referral_token', 'referral_token'),
        Index('idx_audit_logs_outcome_id', 'outcome_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type}, timestamp={self.timestamp})>"
