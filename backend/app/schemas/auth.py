"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.users import UserRoleEnum

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    role: UserRoleEnum
    vsa_id: Optional[str] = None

class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None

class UserLogin(BaseModel):
    """User login request schema"""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")

class UserCreate(BaseModel):
    """User creation request schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: UserRoleEnum = Field(..., description="User role")
    vsa_id: Optional[str] = Field(None, description="VSA organization ID")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    position: Optional[str] = Field(None, max_length=100, description="Job position")
    department: Optional[str] = Field(None, max_length=100, description="Department")

class UserUpdate(BaseModel):
    """User update request schema"""
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Full name")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    position: Optional[str] = Field(None, max_length=100, description="Job position")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    is_active: Optional[bool] = Field(None, description="Active status")

class UserResponse(BaseModel):
    """User response schema"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRoleEnum
    vsa_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """User list response schema"""
    users: list[UserResponse]
    total: int
    page: int
    size: int

class PasswordChange(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="Email address")

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
