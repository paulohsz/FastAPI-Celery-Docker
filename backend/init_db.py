"""Database initialization script."""
import asyncio
from app.db import sync_engine, Base
from app.models import Message


def init_db():
    """Initialize database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
