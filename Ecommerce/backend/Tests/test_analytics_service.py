"""
Tests for AnalyticsService

Comprehensive tests for Amazon-style analytics functionality.
"""
import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from Services.AnalyticsService import AnalyticsService
from Models.User import User, UserRole
from Models.Order import Order, OrderStatus
from Models.OrderItem import OrderItem
from Models.Product import Product
from Models.Payment import Payment
from Models.Refund import Refund
from Models.Employee import Employee, EmploymentStatus, EmploymentType
from Models.HoursWorked import HoursWorked
from database import Base


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_test"


@pytest.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create test database session"""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def sample_products(db_session):
    """Create sample products for testing"""
    products = []
    
    for i in range(3):
        product = Product(
            name=f"Test Product {i+1}",
            description=f"Description for product {i+1}",
            price_cents=1000 * (i+1),  # $10, $20, $30
            stock_quantity=100,
            seller_id=1,
            is_active=True
        )
        db_session.add(product)
        products.append(product)
    
    await db_session.commit()
    
    for product in products:
        await db_session.refresh(product)
    
    return products


@pytest.fixture
async def sample_orders(db_session, sample_products):
    """Create sample orders for testing"""
    orders = []
    
    # Create orders with different statuses
    statuses = [OrderStatus.DELIVERED, OrderStatus.SHIPPED, OrderStatus.PENDING, OrderStatus.CANCELLED]
    
    for i, status in enumerate(statuses):
        order = Order(
            user_id=1,
            status=status,
            subtotal_cents=5000 + (i * 1000),
            tax_cents=500,
            shipping_cents=1000,
            discount_cents=0,
            final_amount_cents=6500 + (i * 1000),
            created_at=datetime.now() - timedelta(days=i)
        )
        db_session.add(order)
        await db_session.flush()
        
        # Add order items
        item = OrderItem(
            order_id=order.id,
            product_id=sample_products[0].id,
            quantity=2,
            price_cents=sample_products[0].price_cents
        )
        db_session.add(item)
        orders.append(order)
    
    await db_session.commit()
    
    for order in orders:
        await db_session.refresh(order)
    
    return orders


@pytest.fixture
async def sample_payments(db_session, sample_orders):
    """Create sample payments"""
    payments = []
    
    for i, order in enumerate(sample_orders[:2]):  # Only completed orders
        payment = Payment(
            order_id=order.id,
            amount_cents=order.final_amount_cents,
            payment_method="credit_card" if i == 0 else "paypal",
            status="completed",
            created_at=order.created_at
        )
        db_session.add(payment)
        payments.append(payment)
    
    await db_session.commit()
    
    for payment in payments:
        await db_session.refresh(payment)
    
    return payments


@pytest.fixture
async def sample_employees(db_session):
    """Create sample employees"""
    employees = []
    
    departments = ["Sales", "Marketing", "Engineering"]
    
    for i, dept in enumerate(departments):
        employee = Employee(
            first_name=f"Employee{i+1}",
            last_name=f"Test{i+1}",
            email=f"employee{i+1}@test.com",
            employee_number=f"EMP{i+1:03d}",
            position="Analyst" if dept == "Sales" else "Staff",
            department=dept,
            employment_type=EmploymentType.FULL_TIME,
            employment_status=EmploymentStatus.ACTIVE,
            hire_date=date.today() - timedelta(days=365),
            is_active=True
        )
        db_session.add(employee)
        employees.append(employee)
    
    await db_session.commit()
    
    for employee in employees:
        await db_session.refresh(employee)
    
    return employees


@pytest.fixture
async def sample_hours_worked(db_session, sample_employees):
    """Create sample hours worked records"""
    hours_records = []
    
    for i, employee in enumerate(sample_employees):
        for day in range(5):  # 5 days of work
            hours = HoursWorked(
                employee_id=employee.id,
                date=date.today() - timedelta(days=day),
                clock_in=datetime.now().replace(hour=9, minute=0),
                clock_out=datetime.now().replace(hour=17, minute=0),
                regular_hours=Decimal("8.0"),
                overtime_hours=Decimal("0.0"),
                approval_status="approved" if day < 3 else "pending"
            )
            db_session.add(hours)
            hours_records.append(hours)
    
    await db_session.commit()
    
    return hours_records


# ==================== SALES & REVENUE ANALYTICS TESTS ====================

@pytest.mark.asyncio
async def test_get_sales_analytics(db_session, sample_orders):
    """Test comprehensive sales analytics"""
    service = AnalyticsService(db_session)
    
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.get_sales_analytics(start_date, end_date)
    
    assert "period" in result
    assert "orders" in result
    assert "revenue" in result
    assert "products" in result
    
    # Check order counts
    assert result["orders"]["total"] == 4
    assert result["orders"]["completed"] == 2  # DELIVERED + SHIPPED
    assert result["orders"]["pending"] == 1
    assert result["orders"]["cancelled"] == 1
    
    # Check revenue
    assert result["revenue"]["gross_revenue"] > 0
    assert result["revenue"]["net_revenue"] > 0


@pytest.mark.asyncio
async def test_get_system_overview(db_session, sample_orders, sample_products, sample_employees):
    """Test system overview dashboard"""
    service = AnalyticsService(db_session)
    
    result = await service.get_system_overview()
    
    assert "snapshot_date" in result
    assert "totals" in result
    assert "recent_activity" in result
    
    # Verify counts
    assert result["totals"]["total_orders"] >= 4
    assert result["totals"]["active_products"] >= 3
    assert result["totals"]["active_employees"] >= 3


@pytest.mark.asyncio
async def test_get_revenue_report(db_session, sample_payments):
    """Test detailed revenue report"""
    service = AnalyticsService(db_session)
    
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.get_revenue_report(start_date, end_date)
    
    assert "period" in result
    assert "revenue" in result
    assert "by_payment_method" in result
    
    # Check payment methods
    assert "credit_card" in result["by_payment_method"]
    assert "paypal" in result["by_payment_method"]
    
    # Check revenue totals
    assert result["revenue"]["gross_revenue"] > 0
    assert result["revenue"]["total_payments"] == 2


@pytest.mark.asyncio
async def test_get_expense_report(db_session, sample_hours_worked):
    """Test expense report with payroll"""
    service = AnalyticsService(db_session)
    
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.get_expense_report(start_date, end_date)
    
    assert "period" in result
    assert "payroll" in result
    assert "by_department" in result
    
    # Check payroll totals
    assert result["payroll"]["total_hours_paid"] > 0
    assert result["payroll"]["employees_paid"] >= 3


@pytest.mark.asyncio
async def test_get_profit_loss_report(db_session, sample_orders, sample_payments, sample_hours_worked):
    """Test P&L report"""
    service = AnalyticsService(db_session)
    
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.get_profit_loss_report(start_date, end_date)
    
    assert "period" in result
    assert "revenue" in result
    assert "expenses" in result
    assert "net_profit" in result
    assert "profit_margin_percent" in result


@pytest.mark.asyncio
async def test_get_seller_performance(db_session, sample_products, sample_orders):
    """Test seller performance metrics"""
    service = AnalyticsService(db_session)
    
    result = await service.get_seller_performance(seller_id=1)
    
    assert "seller_id" in result
    assert "products" in result
    assert "sales" in result
    
    # Check product counts
    assert result["products"]["total"] >= 3


# ==================== PRODUCT ANALYTICS TESTS ====================

@pytest.mark.asyncio
async def test_compare_products(db_session, sample_products, sample_orders):
    """Test product comparison analytics"""
    service = AnalyticsService(db_session)
    
    product_ids = [p.id for p in sample_products[:2]]
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.compare_products(product_ids, start_date, end_date)
    
    assert "period" in result
    assert "products" in result
    assert len(result["products"]) >= 1
    
    # Check product data structure
    if result["products"]:
        product_data = result["products"][0]
        assert "product_id" in product_data
        assert "product_name" in product_data
        assert "units_sold" in product_data
        assert "revenue" in product_data


@pytest.mark.asyncio
async def test_get_product_performance_over_time(db_session, sample_products, sample_orders):
    """Test time-series product performance"""
    service = AnalyticsService(db_session)
    
    product_id = sample_products[0].id
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    # Test daily interval
    result = await service.get_product_performance_over_time(
        product_id, start_date, end_date, interval="day"
    )
    
    assert "product_id" in result
    assert "period" in result
    assert "interval" in result
    assert "time_series" in result
    assert result["interval"] == "day"


# ==================== INVENTORY ANALYTICS TESTS ====================

@pytest.mark.asyncio
async def test_get_inventory_metrics(db_session, sample_products):
    """Test inventory analytics"""
    service = AnalyticsService(db_session)
    
    result = await service.get_inventory_metrics()
    
    assert "total_products" in result
    assert "low_stock_count" in result
    assert "out_of_stock_count" in result
    assert "total_inventory_value" in result
    
    # Should have 3 products
    assert result["total_products"] >= 3


# ==================== EMPLOYEE PRODUCTIVITY TESTS ====================

@pytest.mark.asyncio
async def test_get_employee_productivity(db_session, sample_hours_worked, sample_employees):
    """Test employee productivity analytics"""
    service = AnalyticsService(db_session)
    
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.get_employee_productivity(start_date, end_date)
    
    assert "period" in result
    assert "by_department" in result
    assert "summary" in result
    
    # Check department breakdown
    assert len(result["by_department"]) >= 3  # Sales, Marketing, Engineering
    
    # Check metrics
    assert result["summary"]["total_hours"] > 0
    assert result["summary"]["total_employees"] >= 3


@pytest.mark.asyncio
async def test_get_employee_productivity_filtered_by_department(db_session, sample_hours_worked):
    """Test employee productivity filtered by department"""
    service = AnalyticsService(db_session)
    
    start_date = date.today() - timedelta(days=10)
    end_date = date.today()
    
    result = await service.get_employee_productivity(
        start_date, end_date, department="Sales"
    )
    
    assert "by_department" in result
    
    # Should only have Sales department
    sales_depts = [d for d in result["by_department"] if d["department"] == "Sales"]
    assert len(sales_depts) >= 1


# ==================== EDGE CASES & ERROR HANDLING ====================

@pytest.mark.asyncio
async def test_empty_date_range(db_session):
    """Test analytics with no data in date range"""
    service = AnalyticsService(db_session)
    
    # Future date range with no data
    start_date = date.today() + timedelta(days=100)
    end_date = date.today() + timedelta(days=110)
    
    result = await service.get_sales_analytics(start_date, end_date)
    
    assert result["orders"]["total"] == 0
    assert result["revenue"]["gross_revenue"] == 0


@pytest.mark.asyncio
async def test_nonexistent_seller(db_session):
    """Test seller performance for non-existent seller"""
    service = AnalyticsService(db_session)
    
    result = await service.get_seller_performance(seller_id=99999)
    
    assert result["products"]["total"] == 0
    assert result["sales"]["total_orders"] == 0


@pytest.mark.asyncio
async def test_product_comparison_with_no_sales(db_session, sample_products):
    """Test product comparison when products have no sales"""
    service = AnalyticsService(db_session)
    
    # Use products that don't have orders
    product_ids = [p.id for p in sample_products]
    start_date = date.today() + timedelta(days=10)  # Future date
    end_date = date.today() + timedelta(days=20)
    
    result = await service.compare_products(product_ids, start_date, end_date)
    
    assert "products" in result
    # Products should have zero sales
    for product in result["products"]:
        assert product["units_sold"] == 0
        assert product["revenue"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
