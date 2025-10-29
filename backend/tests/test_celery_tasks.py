"""
Unit tests for Celery tasks.
"""
import pytest
from unittest.mock import Mock, patch, PropertyMock
from datetime import datetime

from app.tasks import create_message_task, slow_task, DatabaseTask
from app.models import Message


# Mark all tests in this module as Celery-related
pytestmark = [pytest.mark.celery, pytest.mark.integration]


class TestCreateMessageTask:
    """Tests for create_message_task."""

    def test_create_message_task_success(self, mock_sync_session_local, test_db_session, reset_database_task_session):
        """Test successful message creation."""
        # Patch SyncSessionLocal at module level before task execution
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            # Reset the cached session
            DatabaseTask._session = None
            
            # Execute the task
            result = create_message_task("Test message content")
            
            # Assertions
            assert result is not None
            assert "id" in result
            assert result["content"] == "Test message content"
            assert "created_at" in result
            
            # Verify message was saved to database
            message = test_db_session.query(Message).filter_by(id=result["id"]).first()
            assert message is not None
            assert message.content == "Test message content"

    def test_create_message_task_empty_content(self, mock_sync_session_local, reset_database_task_session):
        """Test task with empty content."""
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            DatabaseTask._session = None
            result = create_message_task("")
            
            assert result is not None
            assert result["content"] == ""

    def test_create_message_task_long_content(self, mock_sync_session_local, reset_database_task_session):
        """Test task with long content."""
        long_content = "A" * 1000
        
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            DatabaseTask._session = None
            result = create_message_task(long_content)
            
            assert result is not None
            assert result["content"] == long_content
            assert len(result["content"]) == 1000

    def test_create_message_task_special_characters(self, mock_sync_session_local, reset_database_task_session):
        """Test task with special characters."""
        special_content = "Test with émojis 🎉 and spëcial çhars!"
        
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            DatabaseTask._session = None
            result = create_message_task(special_content)
            
            assert result is not None
            assert result["content"] == special_content


class TestSlowTask:
    """Tests for slow_task."""

    def test_slow_task_completes(self):
        """Test that slow_task completes successfully."""
        # Use duration=0 for fast testing
        result = slow_task.apply(args=[0]).get()
        
        assert result is not None
        assert "message" in result
        assert "completed after 0 seconds" in result["message"]

    def test_slow_task_with_custom_duration(self):
        """Test slow_task with custom duration."""
        result = slow_task.apply(args=[0]).get()
        
        assert result["message"] == "Task completed after 0 seconds"

    def test_slow_task_default_duration(self):
        """Test slow_task with default duration (mocked)."""
        # Mock time.sleep to avoid actual waiting
        with patch('time.sleep') as mock_sleep:
            result = slow_task.apply(args=[10]).get()
            
            # Verify sleep was called with correct duration
            mock_sleep.assert_called_once_with(10)
            assert "completed after 10 seconds" in result["message"]


class TestCeleryTaskIntegration:
    """Integration tests for Celery task system."""

    def test_task_registration(self):
        """Test that tasks are properly registered with Celery."""
        from app.celery_app import celery_app
        
        # Check if tasks are registered
        assert "app.tasks.create_message_task" in celery_app.tasks
        assert "app.tasks.slow_task" in celery_app.tasks

    def test_task_names(self):
        """Test that task names are correct."""
        assert create_message_task.name == "app.tasks.create_message_task"
        assert slow_task.name == "app.tasks.slow_task"

    def test_database_task_session_property(self, mock_sync_session_local, test_db_session):
        """Test that DatabaseTask session property works correctly."""
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            # Create a task instance
            task_instance = DatabaseTask()
            task_instance._session = None  # Reset session
            
            # Access session property
            session = task_instance.session
            assert session is not None
            
            # Test session caching (should return same instance)
            session2 = task_instance.session
            assert session2 is session
            
            # Cleanup
            task_instance._session = None

    def test_database_task_after_return_cleanup(self, mock_sync_session_local):
        """Test that DatabaseTask properly cleans up sessions after task execution."""
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            task = DatabaseTask()
            task._session = None
            
            # Access session to create it
            _ = task.session
            assert task._session is not None
            
            # Call after_return to simulate task completion
            task.after_return()
            
            # Verify session was cleaned up
            assert task._session is None


class TestTaskErrorHandling:
    """Tests for error handling in tasks."""

    def test_database_task_runtime_error_no_session(self):
        """Test that DatabaseTask raises error when SyncSessionLocal is None."""
        with patch('app.tasks.SyncSessionLocal', None):
            task = DatabaseTask()
            task._session = None  # Ensure no cached session
            
            with pytest.raises(RuntimeError, match="Sync database session not available"):
                _ = task.session

    def test_create_message_exception_triggers_rollback(self, mock_sync_session_local, reset_database_task_session):
        """Test that exceptions during task execution trigger rollback."""
        from unittest.mock import MagicMock
        
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            DatabaseTask._session = None
            
            # Create a real session but wrap it to spy on methods
            real_session = mock_sync_session_local()
            
            # Track rollback calls
            rollback_called = []
            original_rollback = real_session.rollback
            
            def rollback_spy():
                rollback_called.append(True)
                return original_rollback()
            
            real_session.rollback = rollback_spy
            
            # Make commit raise an exception
            def failing_commit():
                raise Exception("Simulated commit error")
            
            real_session.commit = failing_commit
            
            # Patch the DatabaseTask to return our instrumented session
            with patch.object(DatabaseTask, 'session', new_callable=PropertyMock) as mock_session_property:
                mock_session_property.return_value = real_session
                
                # Execute task and expect exception
                with pytest.raises(Exception, match="Simulated commit error"):
                    create_message_task("Test rollback")
                
                # Verify rollback was called
                assert len(rollback_called) == 1, "Rollback should have been called exactly once"


class TestTaskReturnValues:
    """Tests for task return values and data integrity."""

    def test_create_message_returns_correct_structure(self, mock_sync_session_local, reset_database_task_session):
        """Test that create_message_task returns the correct data structure."""
        with patch('app.tasks.SyncSessionLocal', mock_sync_session_local):
            DatabaseTask._session = None
            result = create_message_task("Test structure")
            
            # Verify structure
            assert isinstance(result, dict)
            assert "id" in result
            assert "content" in result
            assert "created_at" in result
            
            # Verify types
            assert isinstance(result["id"], int)
            assert isinstance(result["content"], str)
            assert isinstance(result["created_at"], str)
            
            # Verify ISO format for created_at
            from datetime import datetime
            datetime.fromisoformat(result["created_at"])  # Should not raise

    def test_slow_task_returns_correct_structure(self):
        """Test that slow_task returns the correct data structure."""
        result = slow_task.apply(args=[0]).get()
        
        assert isinstance(result, dict)
        assert "message" in result
        assert isinstance(result["message"], str)

