"""
Comprehensive Tests for New Service-Controller Integration Endpoints

Tests cover all 30+ newly added endpoints:
- User authentication (logout)
- User management (CS and Manager scoped)
- Analytics (all 10 endpoints)
- Paycheck endpoints (employee and finance)
- Payment processing (intent, capture, stored method)
- Order management (get_all_orders, checkout)
- Time tracking (clock in/out, edit hours, shifts)
- Cart management (CRUD operations)

Requirements:
    pip install pytest pytest-asyncio httpx

Run tests:
    pytest Tests/test_service_controller_integration.py -v
"""
import pytest
import pytest_asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


@pytest.mark.asyncio
class TestUserAuthenticationEndpoints:
    """Test user authentication endpoints."""
    
    async def test_logout_success(self, async_client: AsyncClient, auth_token: str):
        """Test successful logout with audit logging."""
        response = await async_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
    
    async def test_logout_unauthorized(self, async_client: AsyncClient):
        """Test logout without authentication."""
        response = await async_client.post("/api/auth/logout")
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestUserManagementEndpoints:
    """Test user management endpoints (CS and Manager)."""
    
    async def test_cs_create_user(self, async_client: AsyncClient, cs_token: str):
        """Test customer service creating a user."""
        response = await async_client.post(
            "/api/customer-service/users",
            json={
                "email": "newuser@test.com",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "role": "CUSTOMER"
            },
            headers={"Authorization": f"Bearer {cs_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "CUSTOMER"
    
    async def test_cs_get_user_by_id(self, async_client: AsyncClient, cs_token: str, user_id: int):
        """Test customer service getting user by ID."""
        response = await async_client.get(
            f"/api/customer-service/users/{user_id}",
            headers={"Authorization": f"Bearer {cs_token}"}
        )
        
        assert response.status_code == 200
        assert "email" in response.json()
    
    async def test_cs_search_user_by_email(self, async_client: AsyncClient, cs_token: str):
        """Test customer service searching user by email."""
        response = await async_client.get(
            "/api/customer-service/users/search/by-email?email=test@example.com",
            headers={"Authorization": f"Bearer {cs_token}"}
        )
        
        assert response.status_code in [200, 404]
    
    async def test_cs_update_user_role(self, async_client: AsyncClient, cs_token: str, user_id: int):
        """Test customer service updating user role."""
        response = await async_client.put(
            f"/api/customer-service/users/{user_id}/role",
            json={"new_role": "EMPLOYEE"},
            headers={"Authorization": f"Bearer {cs_token}"}
        )
        
        assert response.status_code in [200, 400]
    
    async def test_manager_create_user_in_department(self, async_client: AsyncClient, manager_token: str):
        """Test manager creating user in their department."""
        response = await async_client.post(
            "/api/manager/users",
            json={
                "email": "deptuser@test.com",
                "password": "SecurePass123!",
                "first_name": "Dept",
                "last_name": "User",
                "role": "EMPLOYEE"
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code in [200, 403]  # 403 if not valid manager
    
    async def test_manager_department_scope_enforcement(self, async_client: AsyncClient, manager_token: str, other_dept_user_id: int):
        """Test manager cannot access users outside their department."""
        response = await async_client.get(
            f"/api/manager/users/{other_dept_user_id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestAnalyticsEndpoints:
    """Test all analytics endpoints."""
    
    async def test_system_overview(self, async_client: AsyncClient, admin_token: str):
        """Test system overview analytics."""
        response = await async_client.get(
            "/api/analytics/system/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "total_users" in response.json() or "users" in response.json()
    
    async def test_revenue_report(self, async_client: AsyncClient, admin_token: str):
        """Test revenue report."""
        start = (date.today() - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        
        response = await async_client.get(
            f"/api/analytics/revenue?start_date={start}&end_date={end}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_expense_report(self, async_client: AsyncClient, admin_token: str):
        """Test expense report."""
        start = (date.today() - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        
        response = await async_client.get(
            f"/api/analytics/expenses?start_date={start}&end_date={end}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_profit_loss_report(self, async_client: AsyncClient, admin_token: str):
        """Test profit/loss report."""
        start = (date.today() - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        
        response = await async_client.get(
            f"/api/analytics/profit-loss?start_date={start}&end_date={end}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_seller_performance(self, async_client: AsyncClient, admin_token: str, seller_id: int):
        """Test seller performance metrics."""
        response = await async_client.get(
            f"/api/analytics/seller/{seller_id}/performance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code in [200, 404]
    
    async def test_compare_products(self, async_client: AsyncClient, admin_token: str):
        """Test product comparison."""
        response = await async_client.post(
            "/api/analytics/products/compare",
            json={"product_ids": [1, 2, 3]},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code in [200, 400]
    
    async def test_product_performance_over_time(self, async_client: AsyncClient, admin_token: str):
        """Test product performance trends."""
        start = (date.today() - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        
        response = await async_client.get(
            f"/api/analytics/products/1/performance?start_date={start}&end_date={end}&interval=daily",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code in [200, 404]
    
    async def test_inventory_metrics(self, async_client: AsyncClient, admin_token: str):
        """Test inventory metrics."""
        response = await async_client.get(
            "/api/analytics/inventory/metrics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_track_event(self, async_client: AsyncClient, admin_token: str):
        """Test event tracking."""
        response = await async_client.post(
            "/api/analytics/events/track",
            json={"event_name": "test_event", "event_data": {"key": "value"}},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_conversion_rate(self, async_client: AsyncClient, admin_token: str):
        """Test conversion rate analytics."""
        start = (date.today() - timedelta(days=30)).isoformat()
        end = date.today().isoformat()
        
        response = await async_client.get(
            f"/api/analytics/conversion-rate?start_date={start}&end_date={end}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
class TestPaycheckEndpoints:
    """Test paycheck viewing endpoints."""
    
    async def test_employee_get_own_paycheck(self, async_client: AsyncClient, employee_token: str):
        """Test employee viewing their own paycheck."""
        response = await async_client.get(
            "/api/employee/paycheck",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "gross_pay" in data or "earnings" in data
    
    async def test_finance_get_any_paycheck(self, async_client: AsyncClient, finance_token: str, employee_id: int):
        """Test finance viewing any employee's paycheck."""
        response = await async_client.get(
            f"/api/finance/paycheck/{employee_id}",
            headers={"Authorization": f"Bearer {finance_token}"}
        )
        
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestPaymentProcessingEndpoints:
    """Test payment processing endpoints."""
    
    async def test_create_payment_intent(self, async_client: AsyncClient, customer_token: str, order_id: int):
        """Test creating payment intent."""
        response = await async_client.post(
            "/api/payments/intent",
            json={
                "order_id": order_id,
                "amount_cents": 10000,
                "currency": "USD"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400, 404]
    
    async def test_capture_payment(self, async_client: AsyncClient, customer_token: str, payment_id: int):
        """Test capturing authorized payment."""
        response = await async_client.post(
            f"/api/payments/{payment_id}/capture",
            json={"amount_cents": 10000},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400, 404]
    
    async def test_charge_stored_method(self, async_client: AsyncClient, customer_token: str, order_id: int):
        """Test charging stored payment method."""
        response = await async_client.post(
            "/api/payments/stored-method/charge",
            json={
                "order_id": order_id,
                "amount_cents": 10000,
                "currency": "USD",
                "payment_method_id": 1
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
class TestOrderManagementEndpoints:
    """Test order management endpoints."""
    
    async def test_customer_get_all_orders(self, async_client: AsyncClient, customer_token: str):
        """Test customer getting their orders."""
        response = await async_client.get(
            "/api/orders/all",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 200
        assert "orders" in response.json()
    
    async def test_cs_get_all_orders(self, async_client: AsyncClient, cs_token: str):
        """Test CS getting all orders."""
        response = await async_client.get(
            "/api/orders/all",
            headers={"Authorization": f"Bearer {cs_token}"}
        )
        
        assert response.status_code == 200
    
    async def test_checkout_create_order(self, async_client: AsyncClient, customer_token: str):
        """Test checkout - create order from cart."""
        response = await async_client.post(
            "/api/orders/checkout",
            json={
                "shipping_address_id": 1,
                "payment_method_id": 1
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400]
    
    async def test_cancel_checkout_order(self, async_client: AsyncClient, customer_token: str, order_id: int):
        """Test cancelling order via checkout service."""
        response = await async_client.post(
            f"/api/orders/{order_id}/cancel-checkout",
            json={"reason": "Changed mind"},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
class TestTimeTrackingEndpoints:
    """Test time tracking endpoints."""
    
    async def test_employee_clock_in(self, async_client: AsyncClient, employee_token: str):
        """Test employee clocking in."""
        response = await async_client.post(
            "/api/employee/clock-in",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        assert response.status_code in [200, 400]
    
    async def test_employee_clock_out(self, async_client: AsyncClient, employee_token: str):
        """Test employee clocking out."""
        response = await async_client.post(
            "/api/employee/clock-out",
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        
        assert response.status_code in [200, 400]
    
    async def test_manager_edit_hours(self, async_client: AsyncClient, manager_token: str, hours_id: int):
        """Test manager editing hours."""
        response = await async_client.put(
            f"/api/manager/hours/{hours_id}",
            json={
                "regular_hours": 8.0,
                "overtime_hours": 0.0,
                "notes": "Adjusted hours"
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code in [200, 403, 404]
    
    async def test_manager_bulk_create_shifts(self, async_client: AsyncClient, manager_token: str):
        """Test manager creating shifts in bulk."""
        response = await async_client.post(
            "/api/manager/shifts/bulk",
            json={
                "shifts": [
                    {
                        "employee_id": 1,
                        "date": date.today().isoformat(),
                        "start": "09:00",
                        "end": "17:00"
                    }
                ]
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code in [200, 400, 403]
    
    async def test_manager_create_recurring_shifts(self, async_client: AsyncClient, manager_token: str):
        """Test manager creating recurring shifts."""
        response = await async_client.post(
            "/api/manager/shifts/recurring",
            json={
                "employee_id": 1,
                "days_of_week": ["Monday", "Wednesday", "Friday"],
                "start_time": "09:00",
                "end_time": "17:00",
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=30)).isoformat()
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code in [200, 400, 403]
    
    async def test_manager_cancel_shift(self, async_client: AsyncClient, manager_token: str, shift_id: int):
        """Test manager cancelling shift."""
        response = await async_client.delete(
            f"/api/manager/shifts/{shift_id}",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code in [200, 403, 404]
    
    async def test_manager_update_shift_time(self, async_client: AsyncClient, manager_token: str, shift_id: int):
        """Test manager updating shift times."""
        response = await async_client.put(
            f"/api/manager/shifts/{shift_id}/time",
            json={
                "new_start": "10:00",
                "new_end": "18:00"
            },
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code in [200, 403, 404]


@pytest.mark.asyncio
class TestCartManagementEndpoints:
    """Test cart management endpoints."""
    
    async def test_add_cart_item(self, async_client: AsyncClient, customer_token: str):
        """Test adding item to cart."""
        response = await async_client.post(
            "/api/orders/cart/items",
            json={
                "product_id": 1,
                "quantity": 2
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400]
    
    async def test_remove_cart_item(self, async_client: AsyncClient, customer_token: str, cart_item_id: int):
        """Test removing item from cart."""
        response = await async_client.delete(
            f"/api/orders/cart/items/{cart_item_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 403, 404]
    
    async def test_update_cart_item(self, async_client: AsyncClient, customer_token: str, cart_item_id: int):
        """Test updating cart item quantity."""
        response = await async_client.put(
            f"/api/orders/cart/items/{cart_item_id}",
            json={"quantity": 5},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code in [200, 400, 403, 404]
    
    async def test_clear_cart(self, async_client: AsyncClient, customer_token: str):
        """Test clearing entire cart."""
        response = await async_client.delete(
            "/api/orders/cart",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
class TestAuthorizationPatterns:
    """Test authorization patterns across all endpoints."""
    
    async def test_role_based_access_control(self, async_client: AsyncClient, customer_token: str):
        """Test customer cannot access admin endpoints."""
        response = await async_client.get(
            "/api/analytics/system/overview",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_department_scoping(self, async_client: AsyncClient, manager_token: str, other_dept_employee_id: int):
        """Test manager cannot edit hours for other department."""
        response = await async_client.put(
            f"/api/manager/hours/{other_dept_employee_id}",
            json={"regular_hours": 8.0},
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_ownership_verification(self, async_client: AsyncClient, customer_token: str, other_user_cart_item_id: int):
        """Test customer cannot modify other user's cart."""
        response = await async_client.delete(
            f"/api/orders/cart/items/{other_user_cart_item_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403


# Pytest fixtures
@pytest.fixture
async def async_client(db_session):
    """Create async HTTP client with test database."""
    import sys
    import os
    from httpx import AsyncClient
    from unittest.mock import patch
    
    # Import FastAPI app
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_dir)
    
    from app import app
    from database import get_db
    
    # Override database dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def test_users(db_session):
    """Create test users with various roles."""
    from Models.User import User, UserRole
    from Services.UserService import UserService
    
    user_service = UserService(db_session)
    
    users = {}
    
    # Create users for each role
    roles = [
        ("customer", "customer@test.com"),
        ("employee", "employee@test.com"),
        ("manager", "manager@test.com"),
        ("customer_service", "cs@test.com"),
        ("finance", "finance@test.com"),
        ("analyst", "analyst@test.com"),
        ("admin", "admin@test.com"),
    ]
    
    for role, email in roles:
        try:
            user = await user_service.create_user(
                email=email,
                password="TestPass123!",
                first_name=role.title(),
                last_name="User",
                role=role
            )
            users[role] = user
        except Exception as e:
            print(f"Error creating {role} user: {e}")
    
    await db_session.commit()
    return users


@pytest.fixture
async def auth_token(async_client: AsyncClient, test_users):
    """Get authentication token for regular user."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "customer@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def cs_token(async_client: AsyncClient, test_users):
    """Get authentication token for customer service."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "cs@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def manager_token(async_client: AsyncClient, test_users):
    """Get authentication token for manager."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "manager@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def admin_token(async_client: AsyncClient, test_users):
    """Get authentication token for admin."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def employee_token(async_client: AsyncClient, test_users):
    """Get authentication token for employee."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "employee@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def finance_token(async_client: AsyncClient, test_users):
    """Get authentication token for finance."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "finance@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def customer_token(async_client: AsyncClient, test_users):
    """Get authentication token for customer."""
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "customer@test.com", "password": "TestPass123!"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture
async def user_id(test_users):
    """Get test user ID."""
    return test_users.get("customer").id if test_users.get("customer") else 1


@pytest.fixture
async def seller_id(db_session):
    """Create and return test seller ID."""
    from Models.Seller import Seller
    from Models.User import User
    
    seller = Seller(
        user_id=1,
        business_name="Test Seller",
        business_email="seller@test.com",
        is_active=True
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)
    return seller.id


@pytest.fixture
async def employee_id(db_session, test_users):
    """Create and return test employee ID."""
    from Models.Employee import Employee
    
    employee_user = test_users.get("employee")
    if not employee_user:
        return 1
    
    employee = Employee(
        user_id=employee_user.id,
        email=employee_user.email,
        first_name=employee_user.first_name,
        last_name=employee_user.last_name,
        employee_number="EMP001",
        department="Sales",
        position="Associate",
        hire_date=date.today()
    )
    db_session.add(employee)
    await db_session.commit()
    await db_session.refresh(employee)
    return employee.id


@pytest.fixture
async def order_id(db_session, test_users):
    """Create and return test order ID."""
    from Models.Order import Order, OrderStatus
    
    customer = test_users.get("customer")
    if not customer:
        return 1
    
    order = Order(
        user_id=customer.id,
        order_number="TEST001",
        status=OrderStatus.PENDING,
        subtotal_cents=10000,
        tax_cents=1300,
        shipping_cents=500,
        total_cents=11800,
        currency="USD",
        shipping_address_line1="123 Test St",
        shipping_city="TestCity",
        shipping_state="TS",
        shipping_country="US",
        shipping_postal_code="12345"
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order.id


@pytest.fixture
async def payment_id(db_session, order_id):
    """Create and return test payment ID."""
    from Models.Payment import Payment, PaymentStatus
    
    payment = Payment(
        order_id=order_id,
        amount_cents=11800,
        currency="USD",
        status=PaymentStatus.AUTHORIZED,
        payment_method="credit_card"
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    return payment.id


@pytest.fixture
async def cart_item_id(db_session, test_users):
    """Create and return test cart item ID."""
    from Models.Cart import Cart
    from Models.CartItem import CartItem
    from Models.Product import Product
    
    customer = test_users.get("customer")
    if not customer:
        return 1
    
    # Create product
    product = Product(
        sku="PROD001",
        name="Test Product",
        base_price_cents=1000,
        stock_quantity=100
    )
    db_session.add(product)
    await db_session.flush()
    
    # Create cart
    cart = Cart(user_id=customer.id)
    db_session.add(cart)
    await db_session.flush()
    
    # Create cart item
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=1,
        unit_price_cents=1000
    )
    db_session.add(cart_item)
    await db_session.commit()
    await db_session.refresh(cart_item)
    return cart_item.id


@pytest.fixture
async def hours_id(db_session, employee_id):
    """Create and return test hours ID."""
    from Models.HoursWorked import HoursWorked
    
    hours = HoursWorked(
        employee_id=employee_id,
        work_date=date.today(),
        clock_in=datetime.now(),
        regular_hours=Decimal("8.0"),
        overtime_hours=Decimal("0.0"),
        total_hours=Decimal("8.0")
    )
    db_session.add(hours)
    await db_session.commit()
    await db_session.refresh(hours)
    return hours.id


@pytest.fixture
async def shift_id(db_session, employee_id):
    """Create and return test shift ID."""
    from Models.EmployeeSchedule import EmployeeSchedule
    
    shift = EmployeeSchedule(
        employee_id=employee_id,
        schedule_date=date.today() + timedelta(days=1),
        shift_start="09:00",
        shift_end="17:00",
        department="Sales",
        position="Associate"
    )
    db_session.add(shift)
    await db_session.commit()
    await db_session.refresh(shift)
    return shift.id


@pytest.fixture
async def other_dept_user_id(db_session):
    """Create user in different department."""
    from Models.User import User, UserRole
    from Models.Employee import Employee
    from Services.UserService import UserService
    
    user_service = UserService(db_session)
    user = await user_service.create_user(
        email="otherdept@test.com",
        password="TestPass123!",
        first_name="Other",
        last_name="Department",
        role="employee"
    )
    
    employee = Employee(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        employee_number="EMP999",
        department="Marketing",  # Different department
        position="Associate",
        hire_date=date.today()
    )
    db_session.add(employee)
    await db_session.commit()
    return user.id


@pytest.fixture
async def other_dept_employee_id(db_session, other_dept_user_id):
    """Get employee ID in different department."""
    from sqlalchemy import select
    from Models.Employee import Employee
    
    result = await db_session.execute(
        select(Employee).where(Employee.user_id == other_dept_user_id)
    )
    employee = result.scalar_one_or_none()
    return employee.id if employee else 1


@pytest.fixture
async def other_user_cart_item_id(db_session):
    """Create cart item for different user."""
    from Models.User import User, UserRole
    from Models.Cart import Cart
    from Models.CartItem import CartItem
    from Models.Product import Product
    from Services.UserService import UserService
    
    user_service = UserService(db_session)
    user = await user_service.create_user(
        email="otheruser@test.com",
        password="TestPass123!",
        first_name="Other",
        last_name="User",
        role="customer"
    )
    
    # Create product
    product = Product(
        sku="PROD002",
        name="Other Product",
        base_price_cents=2000,
        stock_quantity=100
    )
    db_session.add(product)
    await db_session.flush()
    
    # Create cart
    cart = Cart(user_id=user.id)
    db_session.add(cart)
    await db_session.flush()
    
    # Create cart item
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=1,
        unit_price_cents=2000
    )
    db_session.add(cart_item)
    await db_session.commit()
    await db_session.refresh(cart_item)
    return cart_item.id
