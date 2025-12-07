# Service-Controller Integration Tests

Comprehensive test suite for all newly added service-controller integration endpoints.

## Test Coverage

- **40+ test cases** covering:
  - User authentication (logout, registration, password reset)
  - User management (Customer Service and Manager with department scoping)
  - Analytics endpoints (10 endpoints for analysts/admins)
  - Paycheck viewing (employee and finance)
  - Payment processing (intent, capture, stored method)
  - Order management (get all, checkout, cancel)
  - Time tracking (clock in/out, edit hours, shift management)
  - Cart management (CRUD operations)
  - Authorization patterns (RBAC, department-scoping, ownership verification)

## Setup

### 1. Install Test Dependencies

```bash
cd Ecommerce/backend/Tests
pip install -r test_requirements.txt
```

### 2. Configure Test Database

The tests use a separate test database to avoid affecting production data.

**Database URL**: `postgresql://postgres:password@localhost:5432/ecommerce_test`

Create the test database:

```bash
psql -U postgres
CREATE DATABASE ecommerce_test;
\q
```

### 3. Run Database Migrations

```bash
cd ../
python setup_test_db.py
```

Or manually apply migrations to the test database.

## Running Tests

### Run All Tests

```bash
pytest Tests/test_service_controller_integration.py -v
```

### Run Specific Test Class

```bash
# User authentication tests
pytest Tests/test_service_controller_integration.py::TestUserAuthenticationEndpoints -v

# Analytics tests
pytest Tests/test_service_controller_integration.py::TestAnalyticsEndpoints -v

# Payment tests
pytest Tests/test_service_controller_integration.py::TestPaymentProcessingEndpoints -v
```

### Run Single Test

```bash
pytest Tests/test_service_controller_integration.py::TestUserAuthenticationEndpoints::test_logout_success -v
```

### Run with Coverage

```bash
pytest Tests/test_service_controller_integration.py --cov=routers --cov=Services --cov-report=html
```

## Test Structure

```
Tests/
├── test_service_controller_integration.py  # Main integration tests (40+ tests)
├── test_requirements.txt                   # Test dependencies
├── conftest.py                             # Shared fixtures
└── README.md                               # This file
```

## Fixtures Available

The test suite uses these fixtures (defined in the test file):

- `async_client` - Async HTTP client with test database
- `test_users` - Pre-created users for all roles
- `auth_token` - Authentication token for regular user
- `cs_token` - Token for customer service user
- `manager_token` - Token for manager user
- `admin_token` - Token for admin user
- `employee_token` - Token for employee user
- `finance_token` - Token for finance user
- `customer_token` - Token for customer user
- `user_id`, `seller_id`, `employee_id` - Test entity IDs
- `order_id`, `payment_id`, `cart_item_id` - Test resource IDs
- `hours_id`, `shift_id` - Time tracking test IDs

## Test Classes

### 1. TestUserAuthenticationEndpoints
- Logout with audit logging
- Unauthorized access handling

### 2. TestUserManagementEndpoints
- Customer Service user CRUD operations
- Manager department-scoped user operations
- Department boundary enforcement

### 3. TestAnalyticsEndpoints
- System overview
- Revenue, expense, profit/loss reports
- Seller and product performance
- Inventory metrics
- Event tracking and conversion rates

### 4. TestPaycheckEndpoints
- Employee viewing own paycheck
- Finance viewing any employee's paycheck

### 5. TestPaymentProcessingEndpoints
- Creating payment intents
- Capturing authorized payments
- Charging stored payment methods

### 6. TestOrderManagementEndpoints
- Getting all orders (role-filtered)
- Creating orders from cart (checkout)
- Cancelling orders

### 7. TestTimeTrackingEndpoints
- Employee clock in/out
- Manager editing hours (department-scoped)
- Bulk and recurring shift creation
- Shift cancellation and time updates

### 8. TestCartManagementEndpoints
- Adding items to cart
- Removing and updating cart items
- Clearing entire cart

### 9. TestAuthorizationPatterns
- Role-based access control enforcement
- Department-scoping enforcement for managers
- Ownership verification for customers

## Common Test Patterns

### Testing Authenticated Endpoints

```python
async def test_endpoint(self, async_client, auth_token):
    response = await async_client.get(
        "/api/endpoint",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
```

### Testing Authorization Failures

```python
async def test_unauthorized_access(self, async_client, customer_token):
    response = await async_client.get(
        "/api/admin/endpoint",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == 403
```

### Testing Department Scoping

```python
async def test_department_scope(self, async_client, manager_token, other_dept_employee_id):
    response = await async_client.put(
        f"/api/manager/hours/{other_dept_employee_id}",
        json={"regular_hours": 8.0},
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 403  # Different department
```

## Expected Outcomes

All tests should pass if:
- ✅ Database migrations are applied
- ✅ Test dependencies are installed
- ✅ Test database is accessible
- ✅ All service layer methods are properly implemented
- ✅ All controller endpoints are correctly defined
- ✅ Authorization middleware is working

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the backend directory
cd Ecommerce/backend

# Install dependencies
pip install -r Tests/test_requirements.txt
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
pg_isready

# Verify test database exists
psql -U postgres -l | grep ecommerce_test

# Create if missing
psql -U postgres -c "CREATE DATABASE ecommerce_test"
```

### Authentication Errors

If tokens are not being generated:
- Check that test users are being created in fixtures
- Verify password hashing is working
- Ensure JWT secret is configured

### Test Isolation Issues

Tests should be isolated and not affect each other. The `db_session` fixture truncates tables before each test.

If tests are interfering:
```bash
# Run tests one at a time
pytest Tests/test_service_controller_integration.py -v -x
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run integration tests
  run: |
    pip install -r Tests/test_requirements.txt
    pytest Tests/test_service_controller_integration.py -v --tb=short
```

## Next Steps

1. **Run the tests**: `pytest Tests/test_service_controller_integration.py -v`
2. **Fix any failures**: Review error messages and fix implementation
3. **Add more tests**: Expand coverage for edge cases
4. **Integrate with CI**: Add to your deployment pipeline

## Contact

For questions about these tests, refer to:
- `FINAL_SERVICE_CONTROLLER_INTEGRATION.md` - Implementation details
- `API_QUICK_REFERENCE.md` - API documentation
