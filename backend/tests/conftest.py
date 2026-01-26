import os
import sys
import asyncio
import pytest

# ---------------------------------------------------------------
# Ensure backend is importable from project root
# ---------------------------------------------------------------
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

# ---------------------------------------------------------------
# Set test database URL BEFORE importing backend
# ---------------------------------------------------------------
# Force test database URL to Postgres for all tests
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/divina_dev"

# Ensure environment is set for settings loading
os.environ["ENV"] = "test"
os.environ.setdefault("EMAIL_API_KEY", "test-email-key")
os.environ.setdefault("SECRET_KEY", "change-me")

# ---------------------------------------------------------------
# Imports AFTER env setup
# ---------------------------------------------------------------
from fastapi.testclient import TestClient
from backend.app import app, get_db
from backend.persistance.async_base import AsyncSessionLocal, engine
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from backend.persistance.base import Base

# ---------------------------------------------------------------
# Override get_db dependency (ASYNC + MANAGED)
# ---------------------------------------------------------------
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

# ---------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

# ---------------------------------------------------------------
# Event loop (required on Windows)
# ---------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ---------------------------------------------------------------
# Reset database schema before tests (drop -> create)
# ---------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def init_db(event_loop):
    # Import persistence models so metadata has all tables
    import backend.persistance.department
    import backend.persistance.user
    import backend.persistance.employee
    import backend.persistance.manager
    import backend.persistance.shift
    import backend.persistance.incident
    import backend.persistance.cart
    import backend.persistance.order
    import backend.persistance.shipment
    import backend.persistance.product
    import backend.persistance.product_variant
    import backend.persistance.order_item
    import backend.persistance.shipment_item
    import backend.persistance.category
    import backend.persistance.subcategory
    import backend.persistance.product_image
    import backend.persistance.product_variant_image
    import backend.persistance.wishlist
    import backend.persistance.wishlist_item

    async def _setup():
        async with engine.begin() as conn:
            # Clear existing schema and data
            await conn.run_sync(Base.metadata.drop_all)
            # Recreate schema to ensure all tables exist before tests
            await conn.run_sync(Base.metadata.create_all)

    event_loop.run_until_complete(_setup())
    # Tests run after this yield; final cleanup handled below
    yield

# ---------------------------------------------------------------
# Database cleanup after all tests
# ---------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def cleanup_db(event_loop):
    yield
    async def _cleanup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    event_loop.run_until_complete(_cleanup())
