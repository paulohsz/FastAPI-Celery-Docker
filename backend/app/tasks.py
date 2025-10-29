from celery import Task

from app.celery_app import celery_app
from app.db import SyncSessionLocal
from app.helpers import utc_now_naive
from app.models import Message


class DatabaseTask(Task):
    """Base task class with database session handling."""

    _session = None

    @property
    def session(self):
        if self._session is None:
            if SyncSessionLocal is None:
                raise RuntimeError("Sync database session not available. Check DATABASE_URL_SYNC configuration.")
            self._session = SyncSessionLocal()
        return self._session

    def after_return(self, *args, **kwargs):
        if self._session is not None:
            self._session.close()
            self._session = None


@celery_app.task(bind=True, base=DatabaseTask, name="app.tasks.create_message_task")
def create_message_task(self, content: str) -> dict:
    """
    Celery task to create a message in the database.

    Args:
        content: The message content to store

    Returns:
        dict with id, content, and created_at of the created message
    """
    session = self.session

    try:
        # Create new message
        message = Message(content=content, created_at=utc_now_naive())
        session.add(message)
        session.commit()
        session.refresh(message)

        return {
            "id": message.id,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
    except Exception as e:
        session.rollback()
        raise e


@celery_app.task(name="app.tasks.slow_task")
def slow_task(duration: int = 10) -> dict:
    """
    A slow task for testing task listing.

    Args:
        duration: How many seconds to sleep

    Returns:
        dict with completion message
    """
    import time

    time.sleep(duration)
    return {"message": f"Task completed after {duration} seconds"}
