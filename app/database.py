from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import settings

# Async Engine for FastAPI
async_db_url = settings.DATABASE_URL
if async_db_url.startswith("sqlite://"):
    async_db_url = async_db_url.replace("sqlite://", "sqlite+aiosqlite://")

async_engine = create_async_engine(
    async_db_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync Engine for Celery & Alembic
sync_db_url = settings.SYNC_DATABASE_URL
sync_engine = create_engine(sync_db_url, echo=False)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
