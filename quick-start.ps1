# Quick Start Script for Beladot E-Commerce Platform (Windows)
# This script sets up and runs both backend and frontend

Write-Host "🚀 Beladot E-Commerce Platform - Quick Start" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3 is not installed. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# ============================================================================
# BACKEND SETUP
# ============================================================================
Write-Host ""
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
Set-Location -Path "Ecommerce\backend"

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..."
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    @"
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/beladot_db

# JWT Secret
SECRET_KEY=$secretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@beladot.com
SMTP_FROM_NAME=Beladot Marketplace

# Upload Directory
UPLOAD_DIR=./uploads

# Environment
ENVIRONMENT=development
"@ | Out-File -FilePath ".env" -Encoding UTF8

    Write-Host "⚠️  Please edit .env file with your actual credentials" -ForegroundColor Yellow
}

# Create uploads directory
if (!(Test-Path "uploads\products\thumbnails")) {
    New-Item -ItemType Directory -Force -Path "uploads\products\thumbnails" | Out-Null
    Write-Host "✅ Created uploads directory" -ForegroundColor Green
}

# Run database migrations
Write-Host "Running database migrations..."
try {
    alembic upgrade head
    Write-Host "✅ Database migrations complete" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Alembic not found or migration failed. You may need to run migrations manually." -ForegroundColor Yellow
}

# ============================================================================
# FRONTEND SETUP
# ============================================================================
Write-Host ""
Write-Host "📦 Setting up Frontend..." -ForegroundColor Yellow
Set-Location -Path "..\..\front-end"

# Install dependencies
if (!(Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies..."
    npm install
}

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating frontend .env file..."
    @"
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_BASE_URL=http://localhost:8000/api
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

# ============================================================================
# FINAL INSTRUCTIONS
# ============================================================================
Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Start Backend (Terminal 1):" -ForegroundColor White
Write-Host "   cd Ecommerce\backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn app:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Start Frontend (Terminal 2):" -ForegroundColor White
Write-Host "   cd front-end" -ForegroundColor Gray
Write-Host "   npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Remember to:" -ForegroundColor Yellow
Write-Host "   - Configure PostgreSQL database" -ForegroundColor Gray
Write-Host "   - Update .env with your SMTP credentials" -ForegroundColor Gray
Write-Host "   - Run database migrations if needed" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Happy coding!" -ForegroundColor Cyan

# Return to original directory
Set-Location -Path ".."
