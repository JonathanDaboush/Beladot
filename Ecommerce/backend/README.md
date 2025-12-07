# E-Commerce Backend API

A production-ready e-commerce backend built with FastAPI, featuring comprehensive business logic separation, role-based access control, and complete order fulfillment workflows.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Deployment](#deployment)

## ✨ Features

### Core Functionality
- **User Management**: Registration, authentication, role-based access (Customer, Employee, Manager, Admin, Seller, Analyst, CS, Finance, Transfer)
- **Product Catalog**: Multi-level categories, variants, images, inventory tracking
- **Shopping Cart**: Persistent carts with pricing calculations
- **Checkout & Payments**: Secure payment processing with stored payment methods
- **Order Management**: Order tracking, fulfillment, shipment creation
- **Seller Portal**: Product management, sales analytics, payout tracking
- **Employee Management**: Scheduling, time tracking, payroll, leave management
- **Analytics**: Comprehensive metrics for business intelligence

### Technical Features
- **Async/Await**: Full asynchronous operation using AsyncIO
- **Clean Architecture**: Service layer pattern with proper separation of concerns
- **Security**: JWT authentication, CSRF protection, rate limiting, input validation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Multi-Currency**: Support for international transactions
- **Audit Logging**: Complete audit trail for all operations
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 🏗️ Architecture

```
Backend/
├── app.py                    # FastAPI application & middleware
├── config.py                 # Configuration management
├── database.py               # Database connection & session handling
├── schemas.py                # Pydantic request/response models
│
├── routers/                  # HTTP endpoint handlers (31 routers)
│   ├── auth.py              # Authentication & registration
│   ├── catalog.py           # Product catalog management
│   ├── checkout.py          # Order checkout
│   ├── fulfillment.py       # Shipment tracking
│   └── ...
│
├── Services/                 # Business logic layer (20 services)
│   ├── UserService.py       # User operations
│   ├── CatalogService.py    # Product management
│   ├── CheckoutService.py   # Order processing
│   ├── FulfillmentService.py # Shipping operations
│   └── ...
│
├── Repositories/             # Data access layer
│   └── *Repository.py       # Database CRUD operations
│
├── Models/                   # SQLAlchemy ORM models
│   ├── User.py              # User table definition
│   ├── Product.py           # Product table
│   ├── Order.py             # Order table
│   └── ...
│
├── Classes/                  # Domain objects (business entities)
│   └── *.py                 # Rich domain models
│
├── Utilities/               # Helper functions
│   ├── auth.py              # JWT token handling
│   ├── rate_limiting.py     # Request rate limiting
│   └── csrf_protection.py   # CSRF token management
│
└── Tests/                   # Test suite
    └── test_*.py            # Unit & integration tests
```

### Request Flow
```
Client Request
    ↓
FastAPI App (app.py)
    ↓
Middleware (Auth, CORS, Rate Limiting)
    ↓
Router (routers/*.py) - Validates input, checks authorization
    ↓
Service (Services/*.py) - Implements business logic
    ↓
Repository (Repositories/*.py) - Database operations
    ↓
Model (Models/*.py) - ORM mapping
    ↓
PostgreSQL Database
```

## 📋 Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **PostgreSQL**: 14 or higher
- **Redis**: 6 or higher (for caching & rate limiting)
- **Git**: For version control

### Optional
- **Docker**: For containerized deployment
- **AWS Account**: For S3 blob storage (images, documents)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/JonathanDaboush/Beladot.git
cd Beladot/Ecommerce/backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import fastapi; import sqlalchemy; print('✓ Dependencies installed successfully')"
```

## ⚙️ Configuration

### 1. Environment File Setup

Create a `.env` file in the backend directory:

```bash
# Copy the example file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your settings:

```env
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# Async database URL for FastAPI (asyncpg driver)
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/ecommerce

# Sync database URL for migrations (psycopg2 driver)
DATABASE_URL_SYNC=postgresql://postgres:your_password@localhost:5432/ecommerce

# ============================================================================
# SECURITY
# ============================================================================
# Generate secret key: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-super-secret-key-change-this-in-production

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development

# ============================================================================
# CORS (Cross-Origin Resource Sharing)
# ============================================================================
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# ============================================================================
# REDIS (Caching & Rate Limiting)
# ============================================================================
REDIS_URL=redis://localhost:6379/0

# ============================================================================
# EMAIL (Optional - for notifications)
# ============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# ============================================================================
# PAYMENT GATEWAY (Optional)
# ============================================================================
PAYMENT_GATEWAY_API_KEY=your-payment-gateway-key

# ============================================================================
# SHIPPING CONFIGURATION
# ============================================================================
DEFAULT_CARRIER=purolator
AVAILABLE_CARRIERS=purolator,fedex,dhl,ups,canadapost

# ============================================================================
# AWS S3 (Optional - for file storage)
# ============================================================================
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

### 3. Generate Secret Key

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Copy the generated key to your `.env` file.

## 💾 Database Setup

### 1. Install PostgreSQL

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Install with default settings
- Remember the password you set for the `postgres` user

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

### 2. Create Database

```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecommerce;

# Create test database (for running tests)
CREATE DATABASE ecommerce_test;

# Exit psql
\q
```

### 3. Initialize Database Schema

Run the setup script to create all tables:

```bash
python setup_production_db.py
```

This will:
- Create all tables from Models/
- Set up enum types (user roles, order status, etc.)
- Create indexes and constraints
- Initialize default data if needed

### 4. Verify Database Setup

```bash
# Check tables were created
psql -U postgres -d ecommerce -c "\dt"

# You should see tables like:
# users, products, orders, carts, payments, shipments, etc.
```

## 🏃 Running the Application

### Development Mode

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
# Run with Gunicorn (Linux/macOS)
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build image
docker build -t ecommerce-backend .

# Run container
docker run -d -p 8000:8000 --env-file .env ecommerce-backend
```

## 🧪 Testing

### Setup Test Database

```bash
python setup_test_db.py
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest Tests/test_catalog_endpoints.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_catalog"
```

### Test Coverage

View coverage report:
```bash
# Generate HTML report
pytest --cov=. --cov-report=html

# Open in browser (Windows)
start htmlcov/index.html

# Open in browser (Linux/macOS)
open htmlcov/index.html
```

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Reference

See `API_QUICK_REFERENCE.md` for common API patterns and examples.

### Authentication

Most endpoints require authentication. To access protected endpoints:

1. **Register a user**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

2. **Login to get token**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

3. **Use token in requests**:
```bash
curl -X GET http://localhost:8000/api/catalog/categories \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📁 Project Structure

### Services (Business Logic)
All business rules and workflows are implemented in the Service layer:

- **AnalyticsService**: Metrics, reports, business intelligence
- **CartService**: Shopping cart operations
- **CatalogService**: Product catalog management
- **CheckoutService**: Order creation and checkout flow
- **FulfillmentService**: Shipment creation and tracking
- **InventoryService**: Stock management
- **OrderService**: Order processing
- **PaymentService**: Payment processing
- **PayrollService**: Employee payroll calculations
- **SchedulingService**: Employee shift scheduling
- **UserService**: User authentication and management

### Models (Database Schema)
SQLAlchemy ORM models define the database structure:

- **User**: User accounts with roles
- **Product**: Products with variants and images
- **Order**: Customer orders
- **Payment**: Payment records
- **Shipment**: Shipping information
- **Employee**: Employee data
- **Seller**: Seller accounts

### Routers (API Endpoints)
31 routers organize endpoints by domain:

- `auth.py`: Authentication & registration
- `catalog.py`: Product catalog (admin & sellers)
- `fulfillment.py`: Shipment tracking
- `checkout.py`: Order checkout
- `analytics.py`: Business metrics
- `manager.py`: Manager operations

## 🔐 Security Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- Department-scoped authorization for managers
- Refresh token rotation

### Input Validation
- Pydantic models for request validation
- SQL injection prevention (SQLAlchemy parameterized queries)
- XSS protection

### Rate Limiting
- Per-endpoint rate limits
- IP-based throttling
- Burst protection

### Security Headers
- HSTS (HTTP Strict Transport Security)
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure PostgreSQL with SSL
- [ ] Set up Redis with authentication
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS/TLS certificates
- [ ] Set up database backups
- [ ] Configure logging to external service
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Configure email service
- [ ] Set up payment gateway
- [ ] Review and test all security settings

### Environment-Specific Configuration

**Development**:
```env
ENVIRONMENT=development
DEBUG=True
```

**Staging**:
```env
ENVIRONMENT=staging
DEBUG=False
```

**Production**:
```env
ENVIRONMENT=production
DEBUG=False
```

### Database Migrations

When updating models:

```bash
# After modifying Models/*.py files, restart the application
# The changes will be reflected on next database connection

# For complex migrations, use alembic:
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
Application logs are written to stdout. Configure log aggregation in production:

```python
# Example: Sending logs to external service
logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'sentry': {
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        }
    }
})
```

## 🤝 Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Keep functions small and focused
- Service layer for business logic only

### Commit Messages
```
feat: Add catalog management endpoints
fix: Resolve shipment tracking authorization
docs: Update API documentation
test: Add fulfillment service tests
refactor: Extract payment processing logic
```

## 📝 License

Copyright © 2025 Jonathan Daboush. All rights reserved.

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Contact: JonathanDaboush@github.com

## 🙏 Acknowledgments

Built with:
- FastAPI - Modern Python web framework
- SQLAlchemy - Python SQL toolkit and ORM
- PostgreSQL - Advanced open source database
- Pydantic - Data validation using Python type hints
- pytest - Testing framework

---

**Version**: 2.0.0  
**Last Updated**: December 7, 2025
