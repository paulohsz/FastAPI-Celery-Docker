from datetime import datetime

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    content: str = Field(..., min_length=1, max_length=500, description="Message content")


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskEnqueueResponse(BaseModel):
    """Schema for task enqueue response."""

    task_id: str
    status: str = "PENDING"
    message: str = "Task enqueued successfully"


class TaskStatusResponse(BaseModel):
    """Schema for task status response."""

    task_id: str
    status: str
    result: dict | None = None


class TaskListItem(BaseModel):
    """Schema for a task in the list."""

    task_id: str
    status: str


class TaskListResponse(BaseModel):
    """Schema for listing all tasks."""

    tasks: list[TaskListItem]
    total: int
