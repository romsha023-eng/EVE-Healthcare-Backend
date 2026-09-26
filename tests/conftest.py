import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, get_db
from app.db.models.user import User, UserRole
from app.db.models.centre import DiagnosticCentre
from app.db.models.test import DiagnosticTest
from app.main import app

# Create in-memory SQLite engine for fast, isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh database tables for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient with overridden get_db dependency."""
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """Create and return an admin user."""
    user = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    """Authorization headers for admin user."""
    token = create_access_token(
        data={"sub": str(admin_user.id), "email": admin_user.email, "role": admin_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def normal_user(db):
    """Create and return a standard user."""
    user = User(
        name="John Doe",
        email="john@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_headers(normal_user):
    """Authorization headers for normal user."""
    token = create_access_token(
        data={"sub": str(normal_user.id), "email": normal_user.email, "role": normal_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user(db):
    """Create and return a second standard user."""
    user = User(
        name="Jane Smith",
        email="jane@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def other_user_headers(other_user):
    """Authorization headers for second standard user."""
    token = create_access_token(
        data={"sub": str(other_user.id), "email": other_user.email, "role": other_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_centre(db):
    """Create a sample diagnostic centre."""
    centre = DiagnosticCentre(
        name="EVE Health Care Centre - Main Branch",
        location="777 Innovation Way, Tech City",
    )
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@pytest.fixture
def sample_test(db):
    """Create a sample diagnostic test."""
    test = DiagnosticTest(
        name="Lipid Profile Test",
        description="Comprehensive cholesterol assessment",
        price=120.00,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@pytest.fixture
def centre_with_test(db, sample_centre, sample_test):
    """Link sample test to sample centre."""
    sample_centre.tests.append(sample_test)
    db.commit()
    db.refresh(sample_centre)
    return sample_centre, sample_test
