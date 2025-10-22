from contextlib import asynccontextmanager
import uuid

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.config import settings
from app.crud import create_message, list_messages
from app.db import Base, async_engine, get_async_session
from app.schemas import (
    MessageCreate,
    MessageResponse,
    TaskEnqueueResponse,
    TaskListResponse,
    TaskStatusResponse,
)
from app.tasks import create_message_task, slow_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Create tables (for development only)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Clean up
    await async_engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI + Celery + PostgreSQL + RabbitMQ application",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI + Celery application",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.post(
    "/tasks/",
    response_model=TaskEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_task(message: MessageCreate):
    """
    Enqueue a Celery task to create a message asynchronously.

    Returns the task ID for tracking.
    """
    task = create_message_task.delay(message.content)
    print(task)
    return TaskEnqueueResponse(task_id=task.id, status=task.state)


@app.post(
    "/tasks/slow",
    response_model=TaskEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_slow_task(duration: int = 10):
    """
    Enqueue a slow test task that takes several seconds to complete.

    Useful for testing task listing and monitoring.

    Args:
        duration: How many seconds the task should run (default: 10)
    """
    task = slow_task.delay(duration)
    return TaskEnqueueResponse(
        task_id=task.id, status=task.state, message=f"Slow task enqueued for {duration} seconds"
    )


@app.get("/tasks/", response_model=TaskListResponse)
async def list_all_tasks():
    """
    List all active/pending Celery tasks.

    Returns a list of task IDs and their current status for tasks that are:
    - ACTIVE: Currently being executed by workers
    - SCHEDULED: Waiting to be executed (scheduled for future)
    - RESERVED: Queued but not yet active

    Note: Completed tasks (SUCCESS/FAILURE) are not included as the application
    uses RPC backend which doesn't persist results long-term. To track a specific
    task, use GET /tasks/{task_id} immediately after creating it.

    To see completed tasks, consider:
    - Using a persistent result backend (Redis, Database)
    - Implementing a custom task tracking system
    - Checking the messages table (GET /messages/) for successfully created messages
    """
    # Get inspect instance
    inspect = celery_app.control.inspect()

    # Collect all tasks from different states
    all_tasks = []
    task_ids_seen = set()

    # Active tasks (currently being executed)
    active_tasks = inspect.active()
    if active_tasks:
        for worker, tasks in active_tasks.items():
            for task in tasks:
                task_id = task.get("id")
                if task_id and task_id not in task_ids_seen:
                    task_ids_seen.add(task_id)
                    all_tasks.append({"task_id": task_id, "status": "ACTIVE"})

    # Scheduled tasks (waiting to be executed)
    scheduled_tasks = inspect.scheduled()
    if scheduled_tasks:
        for worker, tasks in scheduled_tasks.items():
            for task in tasks:
                task_id = task.get("request", {}).get("id")
                if task_id and task_id not in task_ids_seen:
                    task_ids_seen.add(task_id)
                    all_tasks.append({"task_id": task_id, "status": "SCHEDULED"})

    # Reserved tasks (queued but not yet active)
    reserved_tasks = inspect.reserved()
    if reserved_tasks:
        for worker, tasks in reserved_tasks.items():
            for task in tasks:
                task_id = task.get("id")
                if task_id and task_id not in task_ids_seen:
                    task_ids_seen.add(task_id)
                    all_tasks.append({"task_id": task_id, "status": "RESERVED"})

    # Registered tasks (available task types - these are not task instances)
    # We'll skip these as they are task definitions, not actual task executions

    return TaskListResponse(tasks=all_tasks, total=len(all_tasks))


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status and result of a Celery task.

    Returns task status (PENDING, STARTED, SUCCESS, FAILURE) and result if available.
    
    Raises:
        HTTPException 404: If task_id is not a valid UUID format
    """
    # Validate task_id format (Celery uses UUID by default)
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid task ID format. Task ID must be a valid UUID, got: '{task_id}'"
        )
    
    task_result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(task_id=task_id, status=task_result.status)

    if task_result.successful():
        response.result = task_result.result
    elif task_result.failed():
        response.result = {"error": str(task_result.info)}

    return response


@app.post(
    "/messages/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message_endpoint(
    message: MessageCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create a message directly via FastAPI (synchronous operation).

    This endpoint creates the message immediately using async database access.
    """
    db_message = await create_message(db, message)
    return db_message


@app.get("/messages/", response_model=list[MessageResponse])
async def list_messages_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
):
    """
    List all messages from the database.

    Supports pagination with skip and limit parameters.
    """
    messages = await list_messages(db, skip=skip, limit=limit)
    return messages


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
