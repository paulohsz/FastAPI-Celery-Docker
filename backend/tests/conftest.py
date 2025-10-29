"""
Pytest configuration and fixtures for Celery tests.
"""
from contextlib import contextmanager
from datetime import datetime

import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

from app.celery_app import celery_app
from app.db import Base
from app.models import Message
from app.tasks import DatabaseTask


@contextmanager
def _mock_db_time(*, model, time=None):
    """
    Context manager to mock database timestamp fields.
    
    Args:
        model: The SQLAlchemy model class to hook into
        time: Optional datetime to use. If None, uses current datetime.
    
    Yields:
        datetime: The mocked time being used
    """
    if time is None:
        time = datetime.now()  # Use current datetime for tests
    
    def fake_time_hook(mapper, connection, target):
        # Set the created_at field to our fixed time
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """Fixture that returns the mock_db_time context manager."""
    return _mock_db_time


@pytest.fixture
def mock_async_session():
    """
    Helper fixture to create a mocked async session with common setup.
    
    Returns a configured AsyncMock with commit, rollback, and close methods.
    """
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


@pytest.fixture(scope="session")
def celery_config():
    """Celery configuration for tests - use eager mode."""
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": True,  # Execute tasks synchronously
        "task_eager_propagates": True,  # Propagate exceptions in eager mode
    }


@pytest.fixture(scope="session")
def celery_app_fixture(celery_config):
    """Configure Celery app for testing."""
    celery_app.config_from_object(celery_config)
    return celery_app


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine using SQLite in-memory.
    Scope: session - shared across all tests to keep database alive.
    """
    # Use SQLite in-memory for testing
    test_engine = create_engine("sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(test_engine)
    
    yield test_engine
    
    # Cleanup after all tests
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """
    Create a test database session.
    This fixture creates a fresh session for each test and cleans data after.
    """
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestSessionLocal()
    
    yield session
    
    # Rollback any uncommitted changes and clean tables
    session.rollback()
    
    # Delete all data from tables (but keep schema)
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    session.close()


@pytest.fixture(scope="function")
def mock_sync_session_local(test_db_engine):
    """
    Create a mock SyncSessionLocal that returns test sessions.
    This can be used to patch app.db.SyncSessionLocal.
    """
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    return TestSessionLocal


@pytest.fixture(scope="function", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["DATABASE_URL_SYNC"] = "sqlite:///:memory:"
    yield
    # Cleanup is automatic when test ends


@pytest.fixture(scope="function")
def reset_database_task_session():
    """Reset DatabaseTask._session between tests."""
    # Store original value
    original_session = DatabaseTask._session
    
    yield
    
    # Reset to original value (usually None)
    DatabaseTask._session = original_session


@pytest.fixture(scope="function")
def db_with_messages(test_db_session):
    """
    Fixture that populates the database with 3 messages.
    Returns the session with pre-populated data.
    """
    # Create 3 messages
    messages_data = [
        {"content": "First test message"},
        {"content": "Second test message"},
        {"content": "Third test message"},
    ]
    
    created_messages = []
    for data in messages_data:
        message = Message(content=data["content"])
        test_db_session.add(message)
        created_messages.append(message)
    
    test_db_session.commit()
    
    # Refresh to get IDs
    for message in created_messages:
        test_db_session.refresh(message)
    
    return test_db_session


@pytest.fixture(scope="session")
async def async_test_db_engine():
    """
    Create an async test database engine using SQLite with aiosqlite.
    Scope: session - shared across all async tests.
    """
    # Create async engine
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield async_engine
    
    # Cleanup
    await async_engine.dispose()


@pytest.fixture(scope="function")
async def async_test_db_session(async_test_db_engine):
    """
    Create an async test database session.
    This fixture creates a fresh async session for each test and cleans data after.
    """
    # Create session maker
    AsyncSessionLocal = sessionmaker(
        async_test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
        
        # Rollback any uncommitted changes
        await session.rollback()
        
        # Delete all data from tables (but keep schema)
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest.fixture(scope="function")
async def async_db_with_messages(async_test_db_session):
    """
    Fixture that populates the async database with 3 messages.
    Returns the async session with pre-populated data.
    """
    # Create 3 messages
    messages_data = [
        {"content": "First test message"},
        {"content": "Second test message"},
        {"content": "Third test message"},
    ]
    
    for data in messages_data:
        message = Message(content=data["content"])
        async_test_db_session.add(message)
    
    await async_test_db_session.commit()
    
    return async_test_db_session
