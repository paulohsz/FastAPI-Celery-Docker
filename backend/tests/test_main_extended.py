"""Comprehensive tests for main.py endpoints to achieve full coverage."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app, lifespan
from app.models import Message


client = TestClient(app)


def test_enqueue_slow_task():
    """Test enqueueing a slow task."""
    response = client.post("/tasks/slow?duration=5")
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert "status" in data
    assert "message" in data
    assert "5 seconds" in data["message"]


def test_enqueue_slow_task_default_duration():
    """Test enqueueing a slow task with default duration."""
    response = client.post("/tasks/slow")
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    assert "10 seconds" in data["message"]


def test_get_task_status_invalid_uuid():
    """Test getting task status with invalid UUID format."""
    response = client.get("/tasks/invalid-task-id")
    assert response.status_code == 404
    data = response.json()
    assert "Invalid task ID format" in data["detail"]
    assert "invalid-task-id" in data["detail"]


def test_get_task_status_with_valid_uuid():
    """Test getting task status with valid UUID."""
    # Use a valid UUID format (won't exist, but format is valid)
    valid_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/tasks/{valid_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == valid_uuid
    assert "status" in data


# =============================================================================
# Lifespan and Application Lifecycle Tests
# =============================================================================


@pytest.mark.asyncio
async def test_lifespan_startup_and_shutdown():
    """Test lifespan context manager (lines 26-30)."""
    mock_app = MagicMock()
    
    with patch('app.main.async_engine') as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.begin.return_value.__aexit__.return_value = None
        mock_engine.dispose = AsyncMock()
        
        # Enter the context manager
        async with lifespan(mock_app):
            # Verify startup: create_all was called
            mock_conn.run_sync.assert_called_once()
            pass
        
        # Verify shutdown: dispose was called (line 30)
        mock_engine.dispose.assert_called_once()


# =============================================================================
# Task Listing Tests - Various States
# =============================================================================


def test_list_all_tasks_with_active_tasks():
    """Test list_all_tasks with active tasks (lines 114-121)."""
    mock_active = {
        "worker1": [
            {"id": "task-1", "name": "app.tasks.slow_task"},
            {"id": "task-2", "name": "app.tasks.create_message_task"}
        ]
    }
    
    with patch('app.main.celery_app.control.inspect') as mock_inspect:
        mock_inspector = MagicMock()
        mock_inspector.active.return_value = mock_active
        mock_inspector.scheduled.return_value = None
        mock_inspector.reserved.return_value = None
        mock_inspect.return_value = mock_inspector
        
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2
        assert data["tasks"][0]["status"] == "ACTIVE"
        assert data["tasks"][1]["status"] == "ACTIVE"


def test_list_all_tasks_with_scheduled_tasks():
    """Test list_all_tasks with scheduled tasks (lines 124-131)."""
    mock_scheduled = {
        "worker1": [
            {"request": {"id": "scheduled-1"}},
            {"request": {"id": "scheduled-2"}}
        ]
    }
    
    with patch('app.main.celery_app.control.inspect') as mock_inspect:
        mock_inspector = MagicMock()
        mock_inspector.active.return_value = None
        mock_inspector.scheduled.return_value = mock_scheduled
        mock_inspector.reserved.return_value = None
        mock_inspect.return_value = mock_inspector
        
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(task["status"] == "SCHEDULED" for task in data["tasks"])


def test_list_all_tasks_with_reserved_tasks():
    """Test list_all_tasks with reserved tasks (lines 134-141)."""
    mock_reserved = {
        "worker1": [
            {"id": "reserved-1"},
            {"id": "reserved-2"}
        ]
    }
    
    with patch('app.main.celery_app.control.inspect') as mock_inspect:
        mock_inspector = MagicMock()
        mock_inspector.active.return_value = None
        mock_inspector.scheduled.return_value = None
        mock_inspector.reserved.return_value = mock_reserved
        mock_inspect.return_value = mock_inspector
        
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(task["status"] == "RESERVED" for task in data["tasks"])


def test_list_all_tasks_mixed_states():
    """Test list_all_tasks with tasks in different states (lines 107-146)."""
    mock_active = {"worker1": [{"id": "active-1"}]}
    mock_scheduled = {"worker1": [{"request": {"id": "scheduled-1"}}]}
    mock_reserved = {"worker1": [{"id": "reserved-1"}]}
    
    with patch('app.main.celery_app.control.inspect') as mock_inspect:
        mock_inspector = MagicMock()
        mock_inspector.active.return_value = mock_active
        mock_inspector.scheduled.return_value = mock_scheduled
        mock_inspector.reserved.return_value = mock_reserved
        mock_inspect.return_value = mock_inspector
        
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        
        statuses = [task["status"] for task in data["tasks"]]
        assert "ACTIVE" in statuses
        assert "SCHEDULED" in statuses
        assert "RESERVED" in statuses


def test_list_all_tasks_with_duplicate_ids():
    """Test list_all_tasks deduplicates task IDs (lines 111-141)."""
    # Same task ID in active and reserved (shouldn't duplicate)
    mock_active = {"worker1": [{"id": "task-1"}]}
    mock_reserved = {"worker1": [{"id": "task-1"}]}  # Same ID
    
    with patch('app.main.celery_app.control.inspect') as mock_inspect:
        mock_inspector = MagicMock()
        mock_inspector.active.return_value = mock_active
        mock_inspector.scheduled.return_value = None
        mock_inspector.reserved.return_value = mock_reserved
        mock_inspect.return_value = mock_inspector
        
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        # Should only have 1 task (deduplicated)
        assert data["total"] == 1
        assert data["tasks"][0]["task_id"] == "task-1"


def test_list_all_tasks_with_missing_task_ids():
    """Test list_all_tasks handles tasks without IDs (lines 118-120, 128-130, 138-140)."""
    mock_active = {
        "worker1": [
            {"id": "task-1"},
            {"name": "no-id-task"},  # Missing id
            {"id": None}  # None id
        ]
    }
    
    with patch('app.main.celery_app.control.inspect') as mock_inspect:
        mock_inspector = MagicMock()
        mock_inspector.active.return_value = mock_active
        mock_inspector.scheduled.return_value = None
        mock_inspector.reserved.return_value = None
        mock_inspect.return_value = mock_inspector
        
        response = client.get("/tasks/")
        assert response.status_code == 200
        data = response.json()
        # Should only include the task with valid ID
        assert data["total"] == 1
        assert data["tasks"][0]["task_id"] == "task-1"


# =============================================================================
# Task Status Tests - Success and Failure Cases
# =============================================================================


def test_get_task_status_successful_with_result():
    """Test get_task_status when task is successful (line 173)."""
    with patch('app.main.AsyncResult') as mock_async_result:
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.successful.return_value = True
        mock_result.failed.return_value = False
        mock_result.result = {"message": "Task completed", "id": 123}
        mock_async_result.return_value = mock_result
        
        valid_uuid = "12345678-1234-5678-1234-567812345678"
        response = client.get(f"/tasks/{valid_uuid}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["result"] == {"message": "Task completed", "id": 123}


def test_get_task_status_failed_with_error():
    """Test get_task_status when task fails (line 175)."""
    with patch('app.main.AsyncResult') as mock_async_result:
        mock_result = MagicMock()
        mock_result.status = "FAILURE"
        mock_result.successful.return_value = False
        mock_result.failed.return_value = True
        mock_result.info = Exception("Database connection failed")
        mock_async_result.return_value = mock_result
        
        valid_uuid = "12345678-1234-5678-1234-567812345678"
        response = client.get(f"/tasks/{valid_uuid}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FAILURE"
        assert "error" in data["result"]


# =============================================================================
# Message Endpoint Tests
# =============================================================================


def test_create_message_endpoint_mock():
    """Test create_message_endpoint with mock (line 195)."""
    mock_message = Message(id=1, content="Test message", created_at=datetime.now())
    
    with patch('app.main.create_message', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_message
        
        response = client.post(
            "/messages/",
            json={"content": "Test message"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test message"
        assert "id" in data
        mock_create.assert_called_once()


def test_list_messages_endpoint_mock():
    """Test list_messages_endpoint with mock (line 210)."""
    mock_messages = [
        Message(id=1, content="Message 1", created_at=datetime.now()),
        Message(id=2, content="Message 2", created_at=datetime.now()),
    ]
    
    with patch('app.main.list_messages', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_messages
        
        response = client.get("/messages/?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["content"] == "Message 1"
        assert data[1]["content"] == "Message 2"
        mock_list.assert_called_once()


def test_list_messages_endpoint_pagination_mock():
    """Test list_messages_endpoint with pagination mock (line 210)."""
    mock_messages = [
        Message(id=3, content="Message 3", created_at=datetime.now()),
        Message(id=4, content="Message 4", created_at=datetime.now()),
    ]
    
    with patch('app.main.list_messages', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_messages
        
        response = client.get("/messages/?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        # Verify skip and limit were passed correctly
        mock_list.assert_called_once()
        call_args = mock_list.call_args
        assert call_args.kwargs.get('skip') == 2
        assert call_args.kwargs.get('limit') == 2


# =============================================================================
# Legacy Tests (kept for backward compatibility)
# Note: These tests are skipped because TestClient doesn't work well with async
# database sessions. Use test_api.py for proper async endpoint testing.
# =============================================================================


@pytest.mark.skip(reason="TestClient incompatible with async sessions. Use test_api.py instead.")
def test_list_messages_with_pagination():
    """Test listing messages with pagination parameters."""
    pass


@pytest.mark.skip(reason="TestClient incompatible with async sessions. Use test_api.py instead.")
def test_list_messages_default_pagination():
    """Test listing messages with default pagination."""
    pass


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_task_status_successful():
    """Test getting task status when task is successful (with real Celery task)."""
    # Create a task that will complete immediately (using eager mode)
    from app.tasks import slow_task
    result = slow_task.delay(0)
    
    response = client.get(f"/tasks/{result.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == result.id
    assert data["status"] in ["SUCCESS", "PENDING", "STARTED"]


def test_get_task_status_failed():
    """Test getting task status when task doesn't exist (PENDING state)."""
    # Use a valid UUID that doesn't exist
    valid_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/tasks/{valid_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == valid_uuid
    # Task should be PENDING since it doesn't exist
    assert "status" in data
