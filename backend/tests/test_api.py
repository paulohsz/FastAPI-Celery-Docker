import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# Mark all tests in this module as integration and async tests
pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.mark.asyncio(loop_scope="session")
async def test_root_endpoint():
    """Test the root endpoint returns expected response."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_health_check():
    """Test the health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio(loop_scope="session")
async def test_create_message_direct():
    """Test creating a message directly via the FastAPI endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/messages/", json={"content": "Test message from pytest"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["content"] == "Test message from pytest"
        assert "created_at" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_list_messages():
    """Test listing messages."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create a message first
        await client.post("/messages/", json={"content": "Test message for listing"})

        # List messages
        response = await client.get("/messages/")
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        assert len(messages) > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_enqueue_task():
    """
    Test enqueuing a Celery task.

    Note: This is a simple test that verifies the task is enqueued.
    It does NOT wait for the task to complete or verify the result.
    For full integration testing with task execution, you need a running
    Celery worker and should use a test that polls the task status.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/tasks/", json={"content": "Async task test message"}
        )
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "PENDING"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_task_status():
    """
    Test retrieving task status.

    Note: Without a running worker, the task will remain in PENDING state.
    This test verifies the endpoint works but doesn't verify task execution.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Enqueue a task
        enqueue_response = await client.post(
            "/tasks/", json={"content": "Task status test"}
        )
        task_id = enqueue_response.json()["task_id"]

        # Get task status
        status_response = await client.get(f"/tasks/{task_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["task_id"] == task_id
        assert "status" in data
        # Without worker running, status will be PENDING
        assert data["status"] in ["PENDING", "STARTED", "SUCCESS"]
