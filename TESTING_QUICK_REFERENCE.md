# Testing Quick Reference

## 🚀 Quick Start

### Run All Tests
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

## 📁 Test File Locations

```
Backend Unit Tests:
  Ecommerce/backend/Tests/unit/
    ├── test_catalog_service.py    (20+ tests)
    └── test_cart_service.py       (15+ tests)

Backend Integration Tests:
  Ecommerce/backend/Tests/integration/
    ├── test_api_endpoints.py              (15+ tests)
    ├── test_order_payment_fulfillment.py  (20+ tests)
    └── test_edge_cases.py                 (25+ tests)

Frontend Component Tests:
  front-end/src/__tests__/
    ├── ProductCard.test.js        (8+ tests)
    ├── Cart.test.js              (12+ tests)
    └── Login.test.js             (11+ tests)
```

## 🎯 Common Test Commands

### Backend

```powershell
# Run specific test file
pytest Tests/unit/test_catalog_service.py

# Run specific test
pytest Tests/unit/test_catalog_service.py::TestCatalogServiceUnit::test_create_product_success

# Run with coverage
pytest Tests/ --cov=Services --cov-report=html

# Verbose output
pytest Tests/ -v

# Stop on first failure
pytest Tests/ -x

# Show print statements
pytest Tests/ -s

# Run only unit tests
pytest Tests/unit/

# Run only integration tests
pytest Tests/integration/
```

### Frontend

```powershell
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ProductCard.test.js

# Run tests matching pattern
npm test -- --testNamePattern="adds product to cart"

# Update snapshots
npm test -- -u

# No watch mode
npm test -- --watchAll=false
```

## 📊 Test Statistics

| Category | Files | Tests | Lines |
|----------|-------|-------|-------|
| Backend Unit | 2 | 35+ | 800+ |
| Backend Integration | 3 | 50+ | 1,400+ |
| Frontend Component | 3 | 31+ | 800+ |
| **Total** | **8** | **116+** | **3,000+** |

## 🧪 What's Tested

### Backend Services
- ✅ Product CRUD operations
- ✅ Product variants & options
- ✅ Cart management
- ✅ Order processing
- ✅ Payment handling
- ✅ Shipment tracking

### API Endpoints
- ✅ Authentication (register, login)
- ✅ Product endpoints
- ✅ Cart endpoints
- ✅ Order endpoints
- ✅ Payment endpoints
- ✅ Fulfillment endpoints

### Frontend Components
- ✅ Product display
- ✅ Cart management
- ✅ User authentication
- ✅ Form validation
- ✅ Error handling

### Test Scenarios
- ✅ Success paths (valid inputs)
- ✅ Failure paths (invalid inputs)
- ✅ Edge cases (boundaries)
- ✅ Validation rules
- ✅ Authorization checks
- ✅ Error messages

## 🔍 Test Patterns

### Backend Unit Test Pattern
```python
async def test_feature_name(self, service, mock_repos):
    # Arrange
    mock_repos.repo.method.return_value = expected_value
    
    # Act
    result = await service.method(input_data)
    
    # Assert
    assert result == expected_result
    mock_repos.repo.method.assert_called_once()
```

### Backend Integration Test Pattern
```python
async def test_api_endpoint(self, async_client):
    # Arrange - Create user and auth
    await async_client.post("/api/auth/register", json=user_data)
    login_response = await async_client.post("/api/auth/login", data=creds)
    token = login_response.json()["access_token"]
    
    # Act - Call API
    response = await async_client.post(
        "/api/endpoint",
        json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert - Check response
    assert response.status_code == 201
    assert response.json()["field"] == expected_value
```

### Frontend Component Test Pattern
```javascript
test('feature description', async () => {
  // Arrange
  const mockFunction = jest.fn();
  render(<Component prop={mockFunction} />);
  
  // Act
  const button = screen.getByRole('button', { name: /click me/i });
  fireEvent.click(button);
  
  // Assert
  await waitFor(() => {
    expect(mockFunction).toHaveBeenCalledWith(expected_arg);
  });
});
```

## 🐛 Debugging Tests

### Backend
```powershell
# Show full traceback
pytest Tests/ -vv

# Drop into debugger on failure
pytest Tests/ --pdb

# Show local variables
pytest Tests/ -l

# Run last failed tests
pytest Tests/ --lf
```

### Frontend
```powershell
# Debug mode
node --inspect-brk node_modules/.bin/jest --runInBand

# Verbose output
npm test -- --verbose

# Run in band (no parallel)
npm test -- --runInBand
```

## 📈 Coverage Reports

After running tests with coverage:

**Backend**: Open `Ecommerce/backend/coverage_report/index.html` in browser

**Frontend**: Open `front-end/coverage/lcov-report/index.html` in browser

## 🎓 Test Categories

| Category | Backend | Frontend |
|----------|---------|----------|
| Success Paths | ✅ | ✅ |
| Error Handling | ✅ | ✅ |
| Edge Cases | ✅ | ✅ |
| Validation | ✅ | ✅ |
| Authorization | ✅ | ✅ |
| Loading States | ✅ | ✅ |
| Empty States | ✅ | ✅ |

## 🔗 Key Assertions

### Backend
```python
# Status codes
assert response.status_code == 201

# Response data
assert "id" in response.json()
assert response.json()["name"] == "Expected Name"

# Mock calls
mock_repo.create.assert_called_once()
mock_repo.get.assert_called_with(expected_id)

# Exceptions
with pytest.raises(ValueError, match="Error message"):
    await service.method()
```

### Frontend
```javascript
// Element presence
expect(screen.getByText('Text')).toBeInTheDocument();

// Attributes
expect(element).toHaveAttribute('href', '/path');

// States
expect(button).toBeDisabled();
expect(input).toHaveValue('value');

// Mock calls
expect(mockFn).toHaveBeenCalledWith(arg);
expect(mockFn).toHaveBeenCalledTimes(2);
```

## 📚 Documentation

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)**: Comprehensive testing guide
- **[TEST_IMPLEMENTATION_SUMMARY.md](TEST_IMPLEMENTATION_SUMMARY.md)**: Implementation details
- **[conftest.py](Ecommerce/backend/Tests/conftest.py)**: Pytest configuration

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| Tests not found | Check file names start with `test_` |
| Import errors | Ensure virtual environment activated |
| Database errors | Check TEST_DATABASE_URL in conftest.py |
| Frontend timeouts | Increase timeout or use `waitFor` |
| Mock not called | Verify mock injection path |

## ✅ Pre-Commit Checklist

Before committing code:
- [ ] Run all tests: `.\run_all_tests.ps1`
- [ ] All tests pass
- [ ] Coverage maintained or improved
- [ ] New tests added for new features
- [ ] Edge cases covered

## 🚦 CI/CD Integration

Tests run automatically on:
- Every commit (unit tests)
- Pull requests (full suite)
- Before deployment (full suite + coverage)

## 📞 Getting Help

- Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed documentation
- Review existing tests for patterns
- Run tests in verbose mode for more details
- Check error messages carefully

---

**Quick Test**: `.\run_all_tests.ps1`  
**Quick Backend**: `cd Ecommerce\backend; pytest Tests/`  
**Quick Frontend**: `cd front-end; npm test`

**Total Tests**: 116+  
**Test Files**: 8  
**Coverage Goal**: 80%+
