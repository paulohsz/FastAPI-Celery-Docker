from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message
from app.schemas import MessageCreate


async def create_message(db: AsyncSession, message: MessageCreate) -> Message:
    """Create a new message in the database (async)."""
    db_message = Message(content=message.content)
    db.add(db_message)
    await db.flush()
    await db.refresh(db_message)
    return db_message


async def list_messages(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Message]:
    """List messages from the database (async)."""
    result = await db.execute(select(Message).offset(skip).limit(limit))
    return list(result.scalars().all())
