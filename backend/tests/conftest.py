import asyncio
import uuid
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, text

from app.core.database import Base, get_db
from app.core.config import settings
from app.core.auth import hash_password, create_access_token
from app.models.user import User, Role
from app.models.vendor import Vendor, VendorDataAccess
from app.models.risk import RiskScore
from app.models.anomaly import AnomalyEvent
from app.models.evaluation import EvaluationResult
from app.models.ground_truth import GroundTruthLabel
from app.models.compliance import Certification, ComplianceFramework
from app.models.alert import SecurityAlert
from app.models.contract import Contract
from app.models.import_job import CsvImport
from app.main import app

TEST_DB_URL = "postgresql+asyncpg://sentinel:sentinel@localhost:5433/sentinel_test"


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    engine = create_async_engine(TEST_DB_URL, echo=False, pool_size=1)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield


@pytest_asyncio.fixture
async def db_session(setup_database):
    engine = create_async_engine(TEST_DB_URL, echo=False, pool_size=2, pool_pre_ping=True)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    tables = list(Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        for table in reversed(tables):
            await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))

    session = factory()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    result = await db_session.execute(select(Role).where(Role.role_name == "admin"))
    if not result.scalar_one_or_none():
        db_session.add(Role(role_name="admin", description="Admin"))
        db_session.add(Role(role_name="analyst", description="Analyst"))
        db_session.add(Role(role_name="executive", description="Executive"))
        await db_session.flush()

    result = await db_session.execute(select(User).where(User.email == "admin@test.com"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            first_name="Admin",
            role="admin",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
    return user


@pytest_asyncio.fixture
async def analyst_user(db_session: AsyncSession) -> User:
    result = await db_session.execute(select(User).where(User.email == "analyst@test.com"))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email="analyst@test.com",
            password_hash=hash_password("analyst123"),
            first_name="Analyst",
            role="analyst",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()
    return user


@pytest_asyncio.fixture
async def sample_vendor(db_session: AsyncSession) -> Vendor:
    result = await db_session.execute(select(Vendor).where(Vendor.vendor_name == "TestCorp"))
    vendor = result.scalar_one_or_none()
    if not vendor:
        vendor = Vendor(
            vendor_name="TestCorp",
            vendor_type="SaaS",
            criticality="HIGH",
            contract_status="active",
            annual_spend=500000,
            risk_tier="YELLOW",
        )
        db_session.add(vendor)
        await db_session.flush()
    return vendor


@pytest_asyncio.fixture
async def sample_vendors(db_session: AsyncSession) -> list[Vendor]:
    names = ["Acme Corp", "Beta Inc", "Gamma LLC"]
    result = await db_session.execute(select(Vendor).where(Vendor.vendor_name.in_(names)))
    existing = {v.vendor_name: v for v in result.scalars().all()}
    vendors = []
    vendor_data = [
        ("Acme Corp", "SaaS", "HIGH", "active", "GREEN"),
        ("Beta Inc", "Consulting", "MEDIUM", "active", "YELLOW"),
        ("Gamma LLC", "Infrastructure", "LOW", "expired", "RED"),
    ]
    for name, vtype, crit, cstatus, tier in vendor_data:
        if name in existing:
            vendors.append(existing[name])
        else:
            v = Vendor(vendor_name=name, vendor_type=vtype, criticality=crit, contract_status=cstatus, risk_tier=tier)
            db_session.add(v)
            vendors.append(v)
    await db_session.flush()
    return vendors


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    return create_access_token({"sub": str(admin_user.user_id), "role": admin_user.role})


@pytest_asyncio.fixture
async def analyst_token(analyst_user: User) -> str:
    return create_access_token({"sub": str(analyst_user.user_id), "role": analyst_user.role})


@pytest_asyncio.fixture
def override_get_db(db_session: AsyncSession):
    async def _override():
        yield db_session
    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def client(override_get_db) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, admin_token: str) -> AsyncClient:
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client
