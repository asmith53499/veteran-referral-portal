"""
User database model for authentication and authorization
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRoleEnum(str, enum.Enum):
    """User role enumeration"""
    VA_ADMIN = "VA_ADMIN"           # VA system administrators
    VSA_ADMIN = "VSA_ADMIN"         # VSA organization administrators
    VSA_USER = "VSA_USER"           # VSA organization users

class User(Base):
    """Users table model"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(String(50), primary_key=True, index=True)
    
    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), nullable=False)
    vsa_id = Column(String(50), nullable=True)  # TODO: Add ForeignKey when Organization model is created
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Contact information
    phone = Column(String(50), nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    # organization = relationship("Organization", back_populates="users")  # TODO: Add Organization model
    # audit_logs = relationship("AuditLog", back_populates="user")  # TODO: Add user relationship to AuditLog
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
    
    @property
    def is_va_admin(self) -> bool:
        """Check if user is a VA admin"""
        return self.role == UserRoleEnum.VA_ADMIN
    
    @property
    def is_vsa_admin(self) -> bool:
        """Check if user is a VSA admin"""
        return self.role == UserRoleEnum.VSA_ADMIN
    
    @property
    def is_vsa_user(self) -> bool:
        """Check if user is a VSA user"""
        return self.role == UserRoleEnum.VSA_USER
    
    @property
    def can_access_vsa_data(self) -> bool:
        """Check if user can access VSA data"""
        return self.role in [UserRoleEnum.VSA_ADMIN, UserRoleEnum.VSA_USER, UserRoleEnum.VA_ADMIN]
    
    @property
    def can_access_va_data(self) -> bool:
        """Check if user can access VA data"""
        return self.role == UserRoleEnum.VA_ADMIN
