from sqlalchemy import Column, DateTime, Integer, String

from app.db import Base
from app.helpers import utc_now_naive


class Message(Base):
    """Message model for storing messages in the database."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=utc_now_naive, nullable=False)

    def __repr__(self):
        return f"<Message(id={self.id}, content={self.content})>"
