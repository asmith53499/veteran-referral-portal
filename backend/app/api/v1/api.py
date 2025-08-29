"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import referrals, outcomes, health, auth

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(outcomes.router, prefix="/outcomes", tags=["outcomes"])
