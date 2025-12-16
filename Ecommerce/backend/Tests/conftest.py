"""
Pytest configuration and shared fixtures for testing.
"""
import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator
from datetime import datetime, date
from decimal import Decimal
import sys
import os

# Add backend directory to path so we can import from it
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database import Base
from config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test"
TEST_DATABASE_URL_SYNC = "postgresql://postgres:password@localhost:5432/ecommerce_test"


# Configure pytest-asyncio to use function scope for event loops
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a shared test database engine for the session."""
    engine = create_async_engine(
        TEST_DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """
    Create a test database session.
    Each test gets a fresh session. Repositories can commit normally.
    Tables are truncated before each test for isolation.
    """
    async_session = async_sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
    
    # Clean up BEFORE test: truncate all tables
    from sqlalchemy import text
    try:
        async with async_session() as cleanup_session:
            # Get all table names dynamically
            result = await cleanup_session.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version'"
            ))
            tables = [row[0] for row in result]
            if tables:
                tables_str = ', '.join(tables)
                await cleanup_session.execute(text(
                    f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE"
                ))
                await cleanup_session.commit()
    except Exception as e:
        print(f"Warning: Cleanup before test failed: {e}")
    
    async with async_session() as session:
        try:
            yield session
            await session.commit()  # Commit any pending changes
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()


# HTTP Client fixture for integration tests
@pytest_asyncio.fixture
async def async_client():
    """Create httpx AsyncClient for API testing"""
    from httpx import AsyncClient
    from app import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# HTTP Client fixture for integration tests
@pytest_asyncio.fixture
async def async_client():
    """Create httpx AsyncClient for API testing"""
    from httpx import AsyncClient, ASGITransport
    import sys
    sys.path.insert(0, os.path.join(backend_dir))
    from app import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Sample test data fixtures
@pytest.fixture
def sample_employee_data():
    """Sample employee data for testing."""
    return {
        "employee_number": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "555-0100",
        "hire_date": date(2024, 1, 1),
        "position": "Software Engineer",
        "department": "Engineering",
        "location": "Toronto Office",
        "employment_type": "full_time",
        "status": "active"
    }


@pytest.fixture
def sample_employee_financial_data():
    """Sample employee financial data for testing."""
    return {
        "pay_rate": Decimal("50.00"),
        "pay_rate_currency": "CAD",
        "is_salary": False,
        "overtime_eligible": True,
        "overtime_rate_multiplier": Decimal("1.5"),
        "payment_frequency": "bi_weekly",
        "payment_method": "direct_deposit",
        "bank_name": "TD Bank",
        "tax_id_number": "123-456-789",
        "federal_tax_rate": Decimal("0.15"),
        "provincial_tax_rate": Decimal("0.10"),
        "cpp_contribution_rate": Decimal("0.0595"),
        "ei_contribution_rate": Decimal("0.0166")
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "sku": "PROD-001",
        "name": "Test Product",
        "description": "A test product",
        "base_price_cents": 9999,
        "currency": "CAD",
        "stock_quantity": 100,
        "low_stock_threshold": 10,
        "reorder_point": 20,
        "is_active": True,
        "is_featured": False
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "user_id": "user-123",
        "status": "pending",
        "subtotal_cents": 10000,
        "tax_cents": 1300,
        "shipping_cents": 500,
        "total_cents": 11800,
        "currency": "CAD"
    }


@pytest.fixture
def sample_shipment_carriers():
    """Sample carrier list from config."""
    return ["purolator", "fedex", "dhl", "ups", "canadapost"]


@pytest.fixture
def sample_hours_worked_data():
    """Sample hours worked data for testing."""
    return {
        "clock_in": datetime(2024, 1, 1, 9, 0, 0),
        "clock_out": datetime(2024, 1, 1, 17, 0, 0),
        "hours_worked": Decimal("8.0"),
        "overtime_hours": Decimal("0.0"),
        "status": "approved"
    }


@pytest.fixture
def sample_pto_data():
    """Sample PTO data for testing."""
    return {
        "leave_type": "vacation",
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 6, 5),
        "days_requested": Decimal("5.0"),
        "status": "pending",
        "reason": "Summer vacation"
    }


@pytest.fixture
def invalid_employee_data():
    """Invalid employee data for negative testing."""
    return {
        "employee_number": "",  # Empty required field
        "first_name": "A" * 300,  # Too long
        "last_name": "",  # Empty required field
        "email": "invalid-email",  # Invalid email format
        "phone_number": "123",  # Invalid phone format
        "hire_date": date(2030, 1, 1),  # Future date
        "position": "",  # Empty required field
        "department": "",  # Empty required field
        "employment_type": "invalid_type",  # Invalid enum
        "status": "invalid_status"  # Invalid enum
    }


@pytest.fixture
def invalid_financial_data():
    """Invalid financial data for negative testing."""
    return {
        "pay_rate": Decimal("-10.00"),  # Negative pay rate
        "overtime_rate_multiplier": Decimal("0.5"),  # Too low
        "payment_frequency": "invalid",  # Invalid enum
        "federal_tax_rate": Decimal("1.5"),  # > 100%
        "cpp_contribution_rate": Decimal("-0.05")  # Negative
    }


# Helper functions
@pytest.fixture
def create_test_employee(db_session):
    """Factory to create test employees."""
    counter = {"value": 0}
    
    async def _create_employee(**kwargs):
        from Models.Employee import Employee
        from Repositories.EmployeeRepository import EmployeeRepository
        from datetime import date
        import uuid
        
        # Provide default hire_date if not specified
        if 'hire_date' not in kwargs:
            kwargs['hire_date'] = date.today()
        
        # Always make email unique by adding UUID
        counter["value"] += 1
        if 'email' in kwargs:
            base_email = kwargs['email']
            kwargs['email'] = f"{counter['value']}_{uuid.uuid4().hex[:8]}_{base_email}"
        else:
            kwargs['email'] = f"{counter['value']}_{uuid.uuid4().hex[:8]}_test@test.com"
        
        # Always make employee_number unique
        if 'employee_number' in kwargs:
            base_number = kwargs['employee_number']
            kwargs['employee_number'] = f"{base_number}_{uuid.uuid4().hex[:6]}"
        else:
            kwargs['employee_number'] = f"EMP{counter['value']:05d}_{uuid.uuid4().hex[:6]}"
        
        repo = EmployeeRepository(db_session)
        employee = Employee(**kwargs)
        return await repo.create(employee)
    
    return _create_employee


@pytest.fixture
def create_test_product(db_session):
    """Factory to create test products."""
    async def _create_product(**kwargs):
        from Models.Product import Product
        from Models.Seller import Seller
        from Models.User import User
        from Repositories.ProductRepository import ProductRepository
        from Repositories.SellerRepository import SellerRepository
        from Repositories.UserRepository import UserRepository
        
        # Create a test seller if seller_id not provided
        if 'seller_id' not in kwargs:
            # First check if a seller already exists
            from sqlalchemy import select
            result = await db_session.execute(select(Seller))
            existing_seller = result.scalar_one_or_none()
            
            if existing_seller:
                kwargs['seller_id'] = existing_seller.id
            else:
                # Create user first
                user_repo = UserRepository(db_session)
                test_user = User(
                    email="testseller@example.com",
                    first_name="Test",
                    last_name="Seller",
                    hashed_password="$2b$12$test_hash"
                )
                test_user = await user_repo.create(test_user)
                
                # Create seller
                seller_repo = SellerRepository(db_session)
                seller = Seller(
                    user_id=test_user.id,
                    legal_business_name="Test Business LLC",
                    business_type="LLC",
                    phone_number="555-0100",
                    business_address="123 Test St",
                    tax_id="12-3456789",
                    tax_country="US"
                )
                seller = await seller_repo.create(seller)
                kwargs['seller_id'] = seller.id
        
        # Set required defaults if not provided
        if 'slug' not in kwargs and 'name' in kwargs:
            kwargs['slug'] = kwargs['name'].lower().replace(' ', '-')
        
        repo = ProductRepository(db_session)
        product = Product(**kwargs)
        return await repo.create(product)
    
    return _create_product


@pytest.fixture
def mock_carrier_service():
    """Mock shipping carrier service."""
    from Services.ShippingCarrierService import ShippingCarrierService
    return ShippingCarrierService()
