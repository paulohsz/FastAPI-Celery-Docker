from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create database engines
async_engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
sync_engine = create_engine(settings.DATABASE_URL_SYNC, echo=settings.DEBUG, future=True)

# Create session makers
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

SyncSessionLocal = sessionmaker(
    sync_engine, autocommit=False, autoflush=False, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_async_session() -> AsyncSession:
    """Dependency for FastAPI to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
