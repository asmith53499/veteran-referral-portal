"""
Regression tests for referrals API authorization.

Before this fix, every /v1/referrals endpoint had no auth dependency at all -
anyone could list, read, or import referrals with no token. These tests run
against an in-memory SQLite database and override the context-setting DB
dependency (which calls a Postgres function, set_app_context, that SQLite
doesn't have) so they can exercise the FastAPI-level authorization logic in
isolation from the database-level RLS policies.
"""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.auth import get_current_active_user, get_db_with_context
from app.models.users import User, UserRoleEnum
from app.models.referrals import Referral, ProgramCodeEnum, ReferralTypeEnum, PriorityLevelEnum

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_with_context] = override_get_db

client = TestClient(app, base_url="http://localhost")


@pytest.fixture(autouse=True)
def seed_data():
    db = TestingSessionLocal()
    db.query(Referral).delete()
    db.query(User).delete()

    db.add_all([
        User(id="va-1", username="va_admin", email="va@example.com", hashed_password="x",
             full_name="VA Admin", role=UserRoleEnum.VA_ADMIN, vsa_id=None, is_active=True),
        User(id="vsa-1", username="vsa_one", email="vsa1@example.com", hashed_password="x",
             full_name="VSA One", role=UserRoleEnum.VSA_ADMIN, vsa_id="VSA001", is_active=True),
    ])
    db.add_all([
        Referral(referral_token=str(uuid.uuid4()), issued_at=datetime.now(timezone.utc), vsa_id="VSA001",
                  program_code=ProgramCodeEnum.MENTAL_HEALTH, referral_type=ReferralTypeEnum.SELF_REFERRAL,
                  priority_level=PriorityLevelEnum.LOW),
        Referral(referral_token=str(uuid.uuid4()), issued_at=datetime.now(timezone.utc), vsa_id="VSA002",
                  program_code=ProgramCodeEnum.HOUSING_ASSISTANCE, referral_type=ReferralTypeEnum.SELF_REFERRAL,
                  priority_level=PriorityLevelEnum.LOW),
    ])
    db.commit()
    db.close()
    yield


def as_user(user_id):
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()

    def _override():
        return user

    app.dependency_overrides[get_current_active_user] = _override


def test_list_referrals_requires_auth():
    app.dependency_overrides.pop(get_current_active_user, None)
    response = client.get("/v1/referrals/")
    assert response.status_code == 401


def test_vsa_user_only_sees_own_vsa():
    as_user("vsa-1")
    response = client.get("/v1/referrals/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["referrals"][0]["vsa_id"] == "VSA001"


def test_va_admin_sees_all_vsas():
    as_user("va-1")
    response = client.get("/v1/referrals/")
    assert response.status_code == 200
    assert response.json()["total"] == 2
