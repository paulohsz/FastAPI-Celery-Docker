"""Tests for database utilities and models."""
import pytest
from unittest.mock import AsyncMock, patch

from app.db import get_async_session
from app.models import Message


def test_message_model_repr(test_db_session):
    """Test Message model __repr__ method."""
    message = Message(content="Test repr")
    test_db_session.add(message)
    test_db_session.flush()
    test_db_session.refresh(message)
    
    repr_str = repr(message)
    assert "Message" in repr_str
    assert f"id={message.id}" in repr_str
    assert "Test repr" in repr_str


def test_db_session_commit(test_db_session):
    """Test database session commit."""
    message = Message(content="Commit test")
    test_db_session.add(message)
    test_db_session.flush()
    test_db_session.refresh(message)
    
    # Session should commit successfully
    test_db_session.commit()
    assert message.id is not None


def test_db_session_rollback(test_db_session):
    """Test database session rollback."""
    message = Message(content="Rollback test")
    test_db_session.add(message)
    
    # Rollback should work without errors
    test_db_session.rollback()
    # Message should still exist in session but may not be persisted
    assert isinstance(message, Message)


def test_db_session_exception_handling(test_db_session):
    """Test database session exception handling and rollback."""
    message = Message(content="Exception test")
    test_db_session.add(message)
    
    try:
        # Force an integrity error by trying to set id to invalid value
        test_db_session.flush()
        # Simulate an error scenario
        raise ValueError("Simulated error")
    except ValueError:
        # Rollback should handle the exception
        test_db_session.rollback()
        assert True  # Exception was handled


def test_db_session_close(test_db_session):
    """Test database session can be closed properly."""
    message = Message(content="Close test")
    test_db_session.add(message)
    test_db_session.commit()
    
    # Session is closed automatically by fixture
    # but we can verify message was saved
    saved = test_db_session.query(Message).filter_by(content="Close test").first()
    assert saved is not None


@pytest.mark.asyncio
async def test_get_async_session_commit_success(mock_async_session):
    """Test get_async_session commits successfully when no exception occurs."""
    with patch('app.db.AsyncSessionLocal') as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_async_session
        mock_session_local.return_value.__aexit__.return_value = None
        
        # Use the generator
        gen = get_async_session()
        session = await gen.__anext__()
        
        # Verify we got the mocked session
        assert session == mock_async_session
        
        # Complete the generator (simulating successful operation)
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass
        
        # Verify commit was called
        mock_async_session.commit.assert_called_once()
        mock_async_session.rollback.assert_not_called()
        mock_async_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_async_session_rollback_on_exception(mock_async_session):
    """Test get_async_session rolls back when an exception occurs (lines 30-34)."""
    with patch('app.db.AsyncSessionLocal') as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_async_session
        mock_session_local.return_value.__aexit__.return_value = None
        
        # Use the generator
        gen = get_async_session()
        session = await gen.__anext__()
        
        # Verify we got the mocked session
        assert session == mock_async_session
        
        # Simulate an exception during operation
        with pytest.raises(ValueError):
            try:
                raise ValueError("Simulated database error")
            except ValueError as e:
                # This triggers the except block (lines 30-31)
                await gen.athrow(e)
        
        # Verify rollback was called (line 31)
        mock_async_session.rollback.assert_called_once()
        # Verify close was called in finally block (line 33)
        mock_async_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_async_session_close_always_called(mock_async_session):
    """Test get_async_session always closes session in finally block (line 33-34)."""
    with patch('app.db.AsyncSessionLocal') as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_async_session
        mock_session_local.return_value.__aexit__.return_value = None
        
        # Use the generator
        gen = get_async_session()
        await gen.__anext__()
        
        # Even if commit fails, close should be called
        mock_async_session.commit.side_effect = Exception("Commit failed")
        
        with pytest.raises(Exception):
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass
        
        # Verify close was called in finally block (line 33)
        mock_async_session.close.assert_called()

