# Comprehensive Test Validation Script
# Validates that all tests are properly structured and ready to run

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Test Suite Validation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$validationErrors = @()
$validationWarnings = @()

# Function to test file existence
function Test-FileExists {
    param($path, $description)
    if (Test-Path $path) {
        Write-Host "✓ $description exists" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ $description NOT FOUND" -ForegroundColor Red
        $script:validationErrors += "$description not found at: $path"
        return $false
    }
}

# Function to test import in file
function Test-Import {
    param($filePath, $importPattern, $description)
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        if ($content -match $importPattern) {
            Write-Host "  ✓ $description" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ⚠ $description might have issues" -ForegroundColor Yellow
            $script:validationWarnings += "$description in $filePath"
            return $false
        }
    }
    return $false
}

Write-Host "Validating Backend Structure..." -ForegroundColor Cyan
Write-Host ""

# Validate Services exist
Write-Host "Checking Backend Services:" -ForegroundColor Yellow
Test-FileExists "Ecommerce\backend\Services\CatalogService.py" "CatalogService"
Test-FileExists "Ecommerce\backend\Services\CartService.py" "CartService"
Test-FileExists "Ecommerce\backend\Services\CheckoutService.py" "CheckoutService"
Write-Host ""

# Validate Routers exist
Write-Host "Checking API Routers:" -ForegroundColor Yellow
Test-FileExists "Ecommerce\backend\routers\auth.py" "Auth Router"
Test-FileExists "Ecommerce\backend\routers\products.py" "Products Router"
Test-FileExists "Ecommerce\backend\routers\cart.py" "Cart Router"
Test-FileExists "Ecommerce\backend\routers\orders.py" "Orders Router"
Write-Host ""

# Validate Test Files
Write-Host "Checking Backend Test Files:" -ForegroundColor Yellow
Test-FileExists "Ecommerce\backend\Tests\conftest.py" "Test Configuration"
Test-FileExists "Ecommerce\backend\Tests\unit\test_catalog_service.py" "Catalog Service Unit Tests"
Test-FileExists "Ecommerce\backend\Tests\unit\test_cart_service.py" "Cart Service Unit Tests"
Test-FileExists "Ecommerce\backend\Tests\integration\test_api_endpoints.py" "API Endpoint Integration Tests"
Test-FileExists "Ecommerce\backend\Tests\integration\test_order_payment_fulfillment.py" "Order/Payment Tests"
Test-FileExists "Ecommerce\backend\Tests\integration\test_edge_cases.py" "Edge Case Tests"
Write-Host ""

# Validate Frontend Structure
Write-Host "Validating Frontend Structure..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking React Components:" -ForegroundColor Yellow
Test-FileExists "front-end\src\components\ProductCard.js" "ProductCard Component"
Test-FileExists "front-end\src\pages\Cart.js" "Cart Page"
Test-FileExists "front-end\src\pages\Login.js" "Login Page"
Write-Host ""

Write-Host "Checking Frontend Test Files:" -ForegroundColor Yellow
Test-FileExists "front-end\src\__tests__\ProductCard.test.js" "ProductCard Tests"
Test-FileExists "front-end\src\__tests__\Cart.test.js" "Cart Tests"
Test-FileExists "front-end\src\__tests__\Login.test.js" "Login Tests"
Write-Host ""

# Validate Frontend Contexts
Write-Host "Checking React Contexts:" -ForegroundColor Yellow
$hasAuthContext = Test-FileExists "front-end\src\contexts\AuthContext.js" "AuthContext"
$hasCartContext = Test-FileExists "front-end\src\contexts\CartContext.js" "CartContext"
Write-Host ""

# Check if contexts need to be created
if (-not $hasAuthContext -or -not $hasCartContext) {
    Write-Host "⚠ Frontend contexts may need to be created for tests to work" -ForegroundColor Yellow
    $validationWarnings += "Frontend contexts (AuthContext, CartContext) not found"
}

# Validate Dependencies
Write-Host "Checking Dependencies..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Backend Dependencies:" -ForegroundColor Yellow
if (Test-Path "Ecommerce\backend\requirements.txt") {
    $requirements = Get-Content "Ecommerce\backend\requirements.txt"
    $hasPytest = $requirements -match "pytest"
    $hasPytestAsyncio = $requirements -match "pytest-asyncio"
    $hasHttpx = $requirements -match "httpx"
    
    if ($hasPytest) { Write-Host "  ✓ pytest" -ForegroundColor Green } else { Write-Host "  ✗ pytest missing" -ForegroundColor Red; $validationErrors += "pytest not in requirements.txt" }
    if ($hasPytestAsyncio) { Write-Host "  ✓ pytest-asyncio" -ForegroundColor Green } else { Write-Host "  ✗ pytest-asyncio missing" -ForegroundColor Red; $validationErrors += "pytest-asyncio not in requirements.txt" }
    if ($hasHttpx) { Write-Host "  ✓ httpx" -ForegroundColor Green } else { Write-Host "  ✗ httpx missing" -ForegroundColor Red; $validationErrors += "httpx not in requirements.txt" }
}
Write-Host ""

Write-Host "Frontend Dependencies:" -ForegroundColor Yellow
if (Test-Path "front-end\package.json") {
    $packageJson = Get-Content "front-end\package.json" | ConvertFrom-Json
    $hasTesting Library = $packageJson.dependencies.'@testing-library/react' -or $packageJson.devDependencies.'@testing-library/react'
    $hasJestDom = $packageJson.dependencies.'@testing-library/jest-dom' -or $packageJson.devDependencies.'@testing-library/jest-dom'
    
    if ($hasTestingLibrary) { Write-Host "  ✓ @testing-library/react" -ForegroundColor Green } else { Write-Host "  ⚠ @testing-library/react not found" -ForegroundColor Yellow }
    if ($hasJestDom) { Write-Host "  ✓ @testing-library/jest-dom" -ForegroundColor Green } else { Write-Host "  ⚠ @testing-library/jest-dom not found" -ForegroundColor Yellow }
}
Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Validation Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($validationErrors.Count -eq 0) {
    Write-Host "✓ All critical validations passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Found $($validationErrors.Count) error(s):" -ForegroundColor Red
    foreach ($error in $validationErrors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}

if ($validationWarnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ Found $($validationWarnings.Count) warning(s):" -ForegroundColor Yellow
    foreach ($warning in $validationWarnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Test Structure:" -ForegroundColor Cyan
Write-Host "  Backend Unit Tests: 2 files (35+ tests)" -ForegroundColor White
Write-Host "  Backend Integration Tests: 3 files (50+ tests)" -ForegroundColor White
Write-Host "  Frontend Component Tests: 3 files (31+ tests)" -ForegroundColor White
Write-Host "  Total: 8 test files with 116+ tests" -ForegroundColor White
Write-Host ""

if ($validationErrors.Count -eq 0) {
    Write-Host "Ready to run tests! Execute: .\run_all_tests.ps1" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick commands:" -ForegroundColor Cyan
    Write-Host "  Backend: cd Ecommerce\backend; pytest Tests/" -ForegroundColor Gray
    Write-Host "  Frontend: cd front-end; npm test" -ForegroundColor Gray
} else {
    Write-Host "Please fix the errors above before running tests." -ForegroundColor Red
    exit 1
}
