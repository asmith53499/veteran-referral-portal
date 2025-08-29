"""
Authentication API endpoints
"""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import structlog
import uuid

from app.core.database import get_db
from app.core.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_password_hash, require_role, require_va_access
)
from app.models.users import User, UserRoleEnum
from app.schemas.auth import (
    Token, UserLogin, UserCreate, UserUpdate, UserResponse, 
    UserListResponse, PasswordChange
)
from app.config import settings

logger = structlog.get_logger()
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
        
        logger.info("User logged in", user_id=user.id, username=user.username, role=user.role)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user_id=user.id,
            username=user.username,
            role=user.role,
            vsa_id=user.vsa_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_va_access()),
    db: Session = Depends(get_db)
):
    """Create a new user (VA admin only)"""
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            vsa_id=user_data.vsa_id,
            phone=user_data.phone,
            position=user_data.position,
            department=user_data.department,
            is_verified=True  # Auto-verify for VA admin created users
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info("User created", 
                   created_by=str(current_user.id), 
                   new_user_id=str(db_user.id), 
                   role=str(db_user.role))
        
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    size: int = 100,
    role: UserRoleEnum = None,
    vsa_id: str = None,
    current_user: User = Depends(require_va_access()),
    db: Session = Depends(get_db)
):
    """List users (VA admin only)"""
    try:
        query = db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        if vsa_id:
            query = query.filter(User.vsa_id == vsa_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset((page - 1) * size).limit(size).all()
        
        return UserListResponse(
            users=users,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error("Failed to list users", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list users")

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Update fields
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        logger.info("User updated", user_id=current_user.id)
        return current_user
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to update user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.post("/users/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change current user password"""
    try:
        from app.core.auth import verify_password
        
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info("Password changed", user_id=current_user.id)
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to change password", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to change password")

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_va_access()),
    db: Session = Depends(get_db)
):
    """Get user by ID (VA admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_va_access()),
    db: Session = Depends(get_db)
):
    """Update user by ID (VA admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info("User updated by admin", 
                   admin_id=current_user.id, 
                   user_id=user.id)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Failed to update user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update user")
