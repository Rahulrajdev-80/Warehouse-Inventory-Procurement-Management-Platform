import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.security import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def super_admin_headers(db_session):
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    token = create_access_token({"sub": str(admin.id), "role": admin.role.value})
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def manager_headers(db_session):
    mgr = User(
        email="manager@test.com",
        hashed_password=get_password_hash("manager123"),
        full_name="Warehouse Manager",
        role=UserRole.WAREHOUSE_MANAGER,
        is_active=True
    )
    db_session.add(mgr)
    await db_session.commit()
    await db_session.refresh(mgr)

    token = create_access_token({"sub": str(mgr.id), "role": mgr.role.value})
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def staff_headers(db_session):
    staff = User(
        email="staff@test.com",
        hashed_password=get_password_hash("staff123"),
        full_name="Inventory Staff",
        role=UserRole.INVENTORY_STAFF,
        is_active=True
    )
    db_session.add(staff)
    await db_session.commit()
    await db_session.refresh(staff)

    token = create_access_token({"sub": str(staff.id), "role": staff.role.value})
    return {"Authorization": f"Bearer {token}"}
