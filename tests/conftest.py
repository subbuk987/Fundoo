import asyncio
import secrets
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth.authentication import Auth
from config.config_loader import db_settings
from db.database import Base, get_db
from fundoo.api import fundoo_api
from models.label import Label
from models.note import Note
from models.user import User

# Test database setup
SQLALCHEMY_DATABASE_URL = str(db_settings.SQLALCHEMY_DATABASE_URI)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency overrides."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    fundoo_api.dependency_overrides[get_db] = override_get_db
    with TestClient(fundoo_api) as test_client:
        yield test_client
    fundoo_api.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    """Mock Redis operations."""
    with patch("db.redis.redis_client") as mock_client:
        mock_client.set = AsyncMock()
        mock_client.get = AsyncMock(return_value=None)
        mock_client.delete = AsyncMock()
        yield mock_client


@pytest.fixture
def mock_celery():
    """Mock Celery tasks."""
    with patch("celery_logic.celery_tasks.send_verification_email_task") as mock_task:
        mock_task.delay = MagicMock()
        yield mock_task


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "TestPass@123",
    }


@pytest.fixture
def sample_note_data():
    """Sample note data for testing."""
    return {
        "title": "Test Note",
        "content": "This is a test note content",
        "labels": ["work", "important"],
    }


@pytest.fixture
def create_test_user(db_session):
    """Create a test user in the database."""

    def _create_user(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="testpass",
        is_verified=True,
    ):
        hashed_password = Auth.hash_password(password)
        secret_key = secrets.token_urlsafe(64)
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashed_password,
            secret_key=secret_key,
            is_verified=is_verified,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def create_test_note(db_session):
    """Create a test note in the database."""

    def _create_note(user, title="Test Note", content="Test content", labels=None):
        if labels is None:
            labels = []

        # Create labels
        label_objects = []
        for label_name in labels:
            label = db_session.query(Label).filter_by(name=label_name).first()
            if not label:
                label = Label(id=uuid.uuid4(), name=label_name)
                db_session.add(label)
                db_session.commit()
            label_objects.append(label)

        note = Note(
            id=uuid.uuid4(),
            title=title,
            content=content,
            user_id=user.id,
            labels=label_objects,
            created_at=datetime.now(),
            expiry=datetime.now() + timedelta(days=7),
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)
        return note

    return _create_note


@pytest.fixture
def auth_headers(create_test_user):
    def _get_headers(user=None):
        if user is None:
            user = create_test_user(is_verified=True)

        from auth.services import create_access_token

        token_data = {"username": user.username, "user_id": str(user.id)}

        access_token = create_access_token(
            data=token_data, secret_key=user.secret_key  # ✅ must match exactly
        )
        return {"Authorization": f"Bearer {access_token}"}, user

    return _get_headers
