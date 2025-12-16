# Running Tests - Complete Guide

## ✅ Pre-Flight Check

Before running tests, validate your setup:

```powershell
.\validate_tests.ps1
```

This will check:
- ✅ All required files exist
- ✅ Dependencies are installed
- ✅ Test structure is correct
- ✅ Components are in place

## 🚀 Quick Start

### Run ALL Tests
```powershell
.\run_all_tests.ps1
```

### Run Backend Tests Only
```powershell
cd Ecommerce\backend
pytest Tests/ -v
```

### Run Frontend Tests Only
```powershell
cd front-end
npm test -- --watchAll=false
```

## 📋 Prerequisites

### Backend Requirements
1. **Python 3.12+** installed
2. **PostgreSQL** running on localhost:5432
3. **Test Database** created: `ecommerce_test`
4. **Dependencies installed**:
   ```powershell
   cd Ecommerce\backend
   pip install -r requirements.txt
   pip install pytest pytest-asyncio httpx pytest-cov
   ```

### Frontend Requirements
1. **Node.js 18+** installed
2. **Dependencies installed**:
   ```powershell
   cd front-end
   npm install
   ```

## 🗄️ Database Setup

Create the test database (one-time setup):

```sql
CREATE DATABASE ecommerce_test;
```

Or using PowerShell:

```powershell
psql -U postgres -c "CREATE DATABASE ecommerce_test;"
```

The test database should match your main database schema. Run migrations if needed:

```powershell
cd Ecommerce\backend
# Run your migration script or alembic
```

## 🎯 Running Specific Tests

### Backend - Specific Test File
```powershell
cd Ecommerce\backend

# Unit tests only
pytest Tests/unit/ -v

# Integration tests only
pytest Tests/integration/ -v

# Specific file
pytest Tests/unit/test_catalog_service.py -v

# Specific test
pytest Tests/unit/test_catalog_service.py::TestCatalogServiceUnit::test_create_product_success -v
```

### Frontend - Specific Test File
```powershell
cd front-end

# Specific file
npm test -- ProductCard.test.js

# Tests matching pattern
npm test -- --testNamePattern="renders product card"

# With coverage
npm test -- --coverage --watchAll=false
```

## 📊 Coverage Reports

### Backend Coverage
```powershell
cd Ecommerce\backend
pytest Tests/ --cov=Services --cov=routers --cov-report=html --cov-report=term

# View report
start coverage_report\index.html
```

### Frontend Coverage
```powershell
cd front-end
npm test -- --coverage --watchAll=false

# View report
start coverage\lcov-report\index.html
```

## 🐛 Troubleshooting

### Issue: "Import could not be resolved"
**Solution**: Ensure you're in the correct directory and virtual environment

```powershell
# Backend
cd Ecommerce\backend
# Activate your venv if using one

# Frontend
cd front-end
npm install
```

### Issue: "Database connection failed"
**Solution**: Check PostgreSQL is running and test database exists

```powershell
# Check PostgreSQL status
Get-Service postgresql*

# Test connection
psql -U postgres -d ecommerce_test -c "SELECT 1;"
```

### Issue: "Tests hang or timeout"
**Solution**: 
- Check database is not locked
- Ensure no other processes are using the test database
- Restart PostgreSQL if needed

### Issue: "Module not found" in frontend tests
**Solution**: Clear cache and reinstall

```powershell
cd front-end
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
npm test
```

### Issue: pytest fixtures not working
**Solution**: Ensure pytest-asyncio is installed

```powershell
pip install pytest-asyncio
```

## 🔧 Test Configuration

### Backend (conftest.py)
- **Test Database**: `postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_test`
- **Fixtures**: `db_session`, `async_client`, test data fixtures
- **Cleanup**: Tables truncated before each test

### Frontend (setupTests.js)
- **Testing Library**: React Testing Library
- **Jest DOM**: Custom matchers
- **Mocks**: axios, contexts, router

## 📁 Test Structure

```
Ecommerce/backend/Tests/
├── conftest.py                    # Pytest config
├── unit/                          # Unit tests (mocked)
│   ├── test_catalog_service.py    # 20+ tests
│   └── test_cart_service.py       # 15+ tests
└── integration/                   # Integration tests (full stack)
    ├── test_api_endpoints.py              # 15+ tests
    ├── test_order_payment_fulfillment.py  # 20+ tests
    └── test_edge_cases.py                 # 25+ tests

front-end/src/__tests__/
├── ProductCard.test.js            # 8+ tests
├── Cart.test.js                   # 12+ tests
└── Login.test.js                  # 11+ tests
```

## ✨ Test Features

### What's Tested

#### Backend (85+ tests)
- ✅ Service layer logic (CatalogService, CartService)
- ✅ API endpoints (Products, Cart, Orders, Payments, Fulfillment)
- ✅ Authentication and authorization
- ✅ Validation and error handling
- ✅ Edge cases and boundary conditions
- ✅ Database constraints
- ✅ Business logic rules

#### Frontend (31+ tests)
- ✅ Component rendering
- ✅ User interactions (clicks, input)
- ✅ Form validation
- ✅ API call mocking
- ✅ Error handling
- ✅ Loading states
- ✅ Conditional rendering

### Test Categories
- ✅ **Success Paths**: Valid inputs, expected behavior
- ✅ **Failure Paths**: Invalid inputs, error handling
- ✅ **Edge Cases**: Boundary conditions, limits
- ✅ **Validation**: Input validation, format checking
- ✅ **Authorization**: Permission enforcement
- ✅ **Business Logic**: Cart calculations, order flows

## 🎓 Writing New Tests

### Backend Unit Test Template
```python
@pytest.mark.asyncio
async def test_feature_name(self, service, mock_repos):
    # Arrange
    mock_repos.repo.method.return_value = expected_value
    
    # Act
    result = await service.method(input_data)
    
    # Assert
    assert result == expected_result
    mock_repos.repo.method.assert_called_once()
```

### Backend Integration Test Template
```python
async def test_api_endpoint(self, async_client):
    # Register and login
    await async_client.post("/api/auth/signup", json=user_data)
    login_response = await async_client.post("/api/auth/login", data=credentials)
    token = login_response.json()["access_token"]
    
    # Make API call
    response = await async_client.post(
        "/api/endpoint",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["field"] == expected_value
```

### Frontend Test Template
```javascript
test('feature description', async () => {
  const mockFn = jest.fn();
  
  render(
    <BrowserRouter>
      <AuthProvider>
        <Component prop={mockFn} />
      </AuthProvider>
    </BrowserRouter>
  );
  
  const button = screen.getByRole('button', { name: /click me/i });
  fireEvent.click(button);
  
  await waitFor(() => {
    expect(mockFn).toHaveBeenCalledWith(expected_arg);
  });
});
```

## 📈 CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
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
          pip install pytest pytest-asyncio httpx pytest-cov
      - name: Run tests
        run: |
          cd Ecommerce/backend
          pytest Tests/ --cov=Services --cov-report=xml
  
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

## 🎯 Success Criteria

Tests should be run before:
- ✅ Committing code
- ✅ Creating pull requests
- ✅ Deploying to production
- ✅ Major refactoring

All tests should pass with:
- ✅ 100% success rate
- ✅ No skipped tests
- ✅ No warnings or errors
- ✅ Coverage maintained or improved

## 📞 Getting Help

- **Test Guide**: See [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Quick Reference**: See [TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md)
- **Implementation Details**: See [TEST_IMPLEMENTATION_SUMMARY.md](TEST_IMPLEMENTATION_SUMMARY.md)

## 🎉 Next Steps

After all tests pass:
1. Review coverage reports
2. Add tests for any uncovered code
3. Update documentation if needed
4. Commit with message: "test: Add comprehensive test suite"
5. Push to repository

---

**Quick Commands**:
- Validate: `.\validate_tests.ps1`
- Run All: `.\run_all_tests.ps1`
- Backend: `cd Ecommerce\backend; pytest Tests/`
- Frontend: `cd front-end; npm test`
