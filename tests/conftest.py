"""
Pytest configuration and shared fixtures for Cup Streaming API tests.
"""

import os
import sys
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test configuration first
from tests import test_config

from app.core.database import get_db
from main import app
from app.models.user import User, UserRole, ProfileStatus, SignupType
from app.models.faq import FAQ
from app.core.auth import get_password_hash
from sqlmodel import SQLModel


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with proper isolation."""
    # Use in-memory SQLite database for complete isolation
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Clean up - in-memory database is automatically destroyed when engine is disposed
    await engine.dispose()


@pytest.fixture
def client(test_db: AsyncSession) -> TestClient:
    """Create test client with database override."""
    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        password=get_password_hash("TestPassword123!"),
        first_name="Test",
        last_name="User",
        is_active=True,
        role=UserRole.USER,
        profile_status=ProfileStatus.ACTIVE,
        signup_type=SignupType.EMAIL,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_pending(test_db: AsyncSession) -> User:
    """Create test user with pending verification."""
    user = User(
        email="pending@example.com",
        password=get_password_hash("TestPassword123!"),
        first_name="Pending",
        last_name="User",
        is_active=True,
        role=UserRole.USER,
        profile_status=ProfileStatus.PENDING_VERIFICATION,
        signup_type=SignupType.EMAIL,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_inactive(test_db: AsyncSession) -> User:
    """Create inactive test user."""
    user = User(
        email="inactive@example.com",
        password=get_password_hash("TestPassword123!"),
        first_name="Inactive",
        last_name="User",
        is_active=False,
        role=UserRole.USER,
        profile_status=ProfileStatus.ACTIVE,
        signup_type=SignupType.EMAIL,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin_user(test_db: AsyncSession) -> User:
    """Create test admin user."""
    user = User(
        email="admin@example.com",
        password=get_password_hash("AdminPassword123!"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        role=UserRole.ADMIN,
        profile_status=ProfileStatus.ACTIVE,
        signup_type=SignupType.EMAIL,
        is_staff=True,
        is_superuser=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_faq(test_db: AsyncSession) -> FAQ:
    """Create test FAQ."""
    faq = FAQ(
        question="What is this service?",
        answer="This is a streaming service for movies and TV shows.",
        category="General",
        is_active=True,
        is_featured=False,
        sort_order=1,
        view_count=0,
    )
    test_db.add(faq)
    await test_db.commit()
    await test_db.refresh(faq)
    return faq


@pytest_asyncio.fixture
async def test_faq_featured(test_db: AsyncSession) -> FAQ:
    """Create featured test FAQ."""
    faq = FAQ(
        question="How do I get started?",
        answer="Sign up for an account and start streaming immediately.",
        category="Getting Started",
        is_active=True,
        is_featured=True,
        sort_order=0,
        view_count=5,
    )
    test_db.add(faq)
    await test_db.commit()
    await test_db.refresh(faq)
    return faq


@pytest_asyncio.fixture
async def test_faq_inactive(test_db: AsyncSession) -> FAQ:
    """Create inactive test FAQ."""
    faq = FAQ(
        question="Old question?",
        answer="This FAQ is no longer relevant.",
        category="Deprecated",
        is_active=False,
        is_featured=False,
        sort_order=10,
        view_count=2,
    )
    test_db.add(faq)
    await test_db.commit()
    await test_db.refresh(faq)
    return faq


@pytest_asyncio.fixture
async def multiple_test_faqs(test_db: AsyncSession) -> list[FAQ]:
    """Create multiple test FAQs."""
    faqs = [
        FAQ(
            question="How to reset password?",
            answer="Click on forgot password and follow the instructions.",
            category="Account",
            is_active=True,
            is_featured=True,
            sort_order=1,
            view_count=10,
        ),
        FAQ(
            question="What devices are supported?",
            answer="We support all major devices and browsers.",
            category="Technical",
            is_active=True,
            is_featured=False,
            sort_order=2,
            view_count=8,
        ),
        FAQ(
            question="How to cancel subscription?",
            answer="Go to your account settings and cancel your subscription.",
            category="Billing",
            is_active=True,
            is_featured=False,
            sort_order=3,
            view_count=15,
        ),
    ]
    
    for faq in faqs:
        test_db.add(faq)
    
    await test_db.commit()
    
    for faq in faqs:
        await test_db.refresh(faq)
    
    return faqs


@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get auth headers for test user."""
    login_data = {
        "email": test_user.email,
        "password": "TestPassword123!",
        "remember_me": False
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['tokens']['access_token']}"}


@pytest.fixture
def admin_auth_headers(client: TestClient, test_admin_user: User) -> dict:
    """Get auth headers for admin user."""
    login_data = {
        "email": test_admin_user.email,
        "password": "AdminPassword123!",
        "remember_me": False
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['tokens']['access_token']}"}


@pytest.fixture
def mock_email_tasks():
    """Mock email sending tasks."""
    with patch('app.tasks.email_tasks.send_registration_otp_email_task.delay') as mock_reg, \
         patch('app.tasks.email_tasks.send_password_reset_otp_email_task.delay') as mock_reset:
        yield {
            'registration': mock_reg,
            'password_reset': mock_reset
        }


@pytest.fixture
def mock_google_oauth():
    """Mock Google OAuth."""
    with patch('app.api.v1.endpoints.auth.verify_google_token') as mock:
        mock.return_value = AsyncMock(
            id="google_123",
            email="google@example.com",
            verified_email=True,
            name="Google User",
            given_name="Google",
            family_name="User",
            picture="https://example.com/avatar.jpg"
        )
        yield mock


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Clean up any leftover test database files
    import os
    test_db_files = ["test.db", "test.db-journal", "test.db-wal", "test.db-shm"]
    for db_file in test_db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except OSError:
                pass  # Ignore errors if file is locked
