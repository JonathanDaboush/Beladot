#!/bin/bash
# Quick Start Script for Beladot E-Commerce Platform
# This script sets up and runs both backend and frontend

echo "🚀 Beladot E-Commerce Platform - Quick Start"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python and Node.js are installed${NC}"

# ============================================================================
# BACKEND SETUP
# ============================================================================
echo ""
echo "📦 Setting up Backend..."
cd Ecommerce/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/beladot_db

# JWT Secret
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
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
EOF
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual credentials${NC}"
fi

# Create uploads directory
mkdir -p uploads/products/thumbnails

# Run database migrations
echo "Running database migrations..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
else
    echo -e "${YELLOW}⚠️  Alembic not found. Skipping migrations.${NC}"
fi

# ============================================================================
# FRONTEND SETUP
# ============================================================================
echo ""
echo "📦 Setting up Frontend..."
cd ../../front-end

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_BASE_URL=http://localhost:8000/api
EOF
fi

# ============================================================================
# FINAL INSTRUCTIONS
# ============================================================================
echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "To start the application:"
echo ""
echo "1️⃣  Start Backend (Terminal 1):"
echo "   cd Ecommerce/backend"
echo "   source venv/bin/activate"
echo "   uvicorn app:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2️⃣  Start Frontend (Terminal 2):"
echo "   cd front-end"
echo "   npm start"
echo ""
echo "3️⃣  Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}⚠️  Remember to:${NC}"
echo "   - Configure PostgreSQL database"
echo "   - Update .env with your SMTP credentials"
echo "   - Run database migrations if needed"
echo ""
echo "🎉 Happy coding!"
