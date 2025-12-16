# Test Runner Script for Beladot E-commerce Platform
# This script runs all tests and generates coverage reports

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Beladot E-commerce Test Suite Runner" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-CommandExists {
    param($command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $command) { return $true }
    }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

# Check Python
if (-not (Test-CommandExists python)) {
    Write-Host "ERROR: Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Check Node
if (-not (Test-CommandExists node)) {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python version: " -NoNewline -ForegroundColor Green
python --version

Write-Host "✓ Node version: " -NoNewline -ForegroundColor Green
node --version

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Running Backend Tests" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Push-Location "Ecommerce\backend"

Write-Host "→ Running backend unit tests..." -ForegroundColor Yellow
pytest Tests/unit/ -v --tb=short
$backendUnitResult = $LASTEXITCODE

Write-Host ""
Write-Host "→ Running backend integration tests..." -ForegroundColor Yellow
pytest Tests/integration/ -v --tb=short
$backendIntegrationResult = $LASTEXITCODE

Write-Host ""
Write-Host "→ Generating backend coverage report..." -ForegroundColor Yellow
pytest Tests/ --cov=Services --cov-report=term --cov-report=html:coverage_report
$backendCoverageResult = $LASTEXITCODE

Pop-Location

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Running Frontend Tests" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Push-Location "front-end"

Write-Host "→ Running frontend component tests..." -ForegroundColor Yellow
npm test -- --watchAll=false --coverage
$frontendResult = $LASTEXITCODE

Pop-Location

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Test Results Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Display results
if ($backendUnitResult -eq 0) {
    Write-Host "✓ Backend Unit Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Backend Unit Tests: FAILED" -ForegroundColor Red
}

if ($backendIntegrationResult -eq 0) {
    Write-Host "✓ Backend Integration Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Backend Integration Tests: FAILED" -ForegroundColor Red
}

if ($frontendResult -eq 0) {
    Write-Host "✓ Frontend Component Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend Component Tests: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "Coverage Reports:" -ForegroundColor Cyan
Write-Host "  Backend: Ecommerce\backend\coverage_report\index.html" -ForegroundColor Gray
Write-Host "  Frontend: front-end\coverage\lcov-report\index.html" -ForegroundColor Gray

Write-Host ""

# Exit with error if any tests failed
if ($backendUnitResult -ne 0 -or $backendIntegrationResult -ne 0 -or $frontendResult -ne 0) {
    Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "All tests passed! 🎉" -ForegroundColor Green
    exit 0
}
