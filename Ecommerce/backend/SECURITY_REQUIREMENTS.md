# Backend Security Requirements

## Critical Security Measures Needed

Since you're not making external API calls to carriers or banks, you still need comprehensive security for your backend system. Here are the essential measures:

---

## 1. **Authentication & Authorization**

### Currently Missing:
- JWT token generation and validation
- Password hashing (bcrypt/argon2)
- Session management
- Role-based access control (RBAC)

### Required Implementation:
```python
# Add to requirements.txt
bcrypt==4.1.2
PyJWT==2.8.0
python-jose[cryptography]==3.3.0

# Create Utilities/auth.py
- hash_password()
- verify_password()
- create_access_token()
- decode_token()
- require_auth() decorator
- require_role() decorator
```

### Critical for:
- Employee data access (payroll, schedules)
- User accounts and orders
- Admin/manager functions
- Sensitive financial data

---

## 2. **Data Encryption**

### Currently Missing:
- Database field encryption for sensitive data
- Encryption at rest

### Critical Fields Requiring Encryption:
```python
# Employee table
- tax_id_number (SIN/SSN)
- bank_account_number
- routing_number

# User table
- payment_method_details
- address information (optional but recommended)

# CompanyBankAccount table
- account_number
- routing_number
```

### Required Implementation:
```python
# Add to requirements.txt
cryptography==41.0.7

# Create Utilities/encryption.py
- encrypt_field()
- decrypt_field()
- generate_encryption_key()
```

---

## 3. **Input Validation & Sanitization**

### Currently Missing:
- Request validation schemas
- SQL injection prevention (using SQLAlchemy ORM helps but not complete)
- XSS prevention
- Input sanitization

### Required Implementation:
```python
# Add to requirements.txt
pydantic==2.5.0  # For request/response validation

# Create schemas for all endpoints
- UserSchema
- EmployeeSchema
- OrderSchema
- etc.

# Validation rules:
- Email format validation
- Phone number format
- Employee number format
- Numeric ranges (pay rates, prices)
- String length limits
- Allowed characters only
```

---

## 4. **Rate Limiting**

### Currently Missing:
- Request rate limiting per user/IP
- Brute force protection for login attempts

### Required Implementation:
```python
# Add to requirements.txt
slowapi==0.1.9

# Apply to:
- Login endpoints (max 5 attempts per 15 minutes)
- Password reset (max 3 per hour)
- API endpoints (general rate limiting)
```

---

## 5. **CORS (Cross-Origin Resource Sharing)**

### Required if frontend is separate domain:
```python
# Add to requirements.txt
fastapi-cors==0.0.6

# Configure allowed origins
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

---

## 6. **HTTPS/TLS**

### Required:
- All traffic must use HTTPS
- TLS 1.2 or higher
- Valid SSL certificate

### Implementation:
```bash
# Production deployment (not in code)
- Use reverse proxy (Nginx/Apache)
- Configure SSL certificates (Let's Encrypt)
- Force HTTPS redirects
```

---

## 7. **Environment Variables & Secrets Management**

### Currently Missing:
- Secure storage of secrets
- Environment-specific configurations

### Required:
```python
# Create .env file (NEVER commit to git)
DATABASE_URL=postgresql://...
SECRET_KEY=your-super-secret-jwt-key
ENCRYPTION_KEY=your-encryption-key
SMTP_PASSWORD=your-email-password

# Add to .gitignore
.env
*.key
secrets/

# Load with python-dotenv
from dotenv import load_dotenv
load_env()
```

---

## 8. **Database Security**

### Required:
- Database connection encryption (SSL)
- Least privilege database user (not root/admin)
- Regular backups
- Audit logging

### Implementation:
```python
# In database.py
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://user:pass@host:5432/db"
    f"?sslmode=require"  # Force SSL
)

# Create separate DB users:
- app_user (read/write to specific tables)
- readonly_user (for reports)
- admin_user (migrations only)
```

---

## 9. **Audit Logging**

### Currently Have: AuditLog model ✓

### Need to Implement:
- Log all sensitive operations
- Track who accessed what data
- Compliance logging (GDPR, SOX, etc.)

### Critical Events to Log:
```python
- User login/logout
- Password changes
- Employee data access (especially payroll)
- Order creation/modifications
- Payment processing
- Schedule changes
- Failed authentication attempts
- Permission changes
```

---

## 10. **Session Management**

### Required:
- Secure session tokens
- Session expiration (30 min - 2 hours)
- Token refresh mechanism
- Logout/revoke capability

### Implementation:
```python
# JWT token with:
- Short expiration (15-30 minutes for access token)
- Longer refresh token (7 days)
- Token blacklist for logout
- Store in HTTP-only cookies (not localStorage)
```

---

## 11. **Error Handling**

### Currently Missing:
- Proper error responses (don't leak stack traces)
- Sanitized error messages

### Required:
```python
# Never expose:
- Database schema details
- Internal file paths
- Stack traces in production
- Sensitive configuration

# Return generic messages:
"An error occurred" 
not 
"DatabaseError: duplicate key violates unique constraint users_email_key"
```

---

## 12. **File Upload Security**

### If you have file uploads (images, documents):
```python
# Required:
- File type validation (whitelist only)
- File size limits
- Virus scanning
- Store outside web root
- Randomize filenames
- Prevent path traversal attacks
```

---

## 13. **API Security Headers**

### Required Headers:
```python
# In FastAPI middleware
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000
- Content-Security-Policy: default-src 'self'
```

---

## 14. **Dependency Security**

### Required:
```bash
# Regular security audits
pip install safety
safety check

# Keep dependencies updated
pip list --outdated

# Pin versions in requirements.txt
sqlalchemy==2.0.23  # Not >=2.0.0
```

---

## 15. **Access Control for Sensitive Operations**

### Role-Based Access Control (RBAC):

**Admin:**
- Full system access
- User management
- Company settings

**Manager:**
- Employee schedules (own department)
- Approve time off
- View department reports

**HR:**
- Employee data access
- Payroll processing
- Hiring/termination

**Employee:**
- Own schedule view
- Time off requests
- Own paycheck history

**Customer:**
- Own orders
- Own profile
- Own addresses

### Implementation:
```python
@app.get("/api/payroll")
@require_role(["admin", "hr"])
async def get_payroll():
    # Only admin and HR can access
    pass

@app.get("/api/employee/{id}/financial")
@require_auth()
async def get_employee_financial(id: int, current_user: User):
    # Can only view own data unless HR/admin
    if current_user.id != id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(403, "Access denied")
```

---

## 16. **Payroll-Specific Security**

### Critical for Your Payroll System:
- Separate encryption key for financial data
- Audit log all payroll access
- Two-factor approval for payroll runs
- Separate database permissions for payroll tables
- Pay stub access control (employees can only see own)
- Mask account numbers (show last 4 digits only)

---

## 17. **Schedule/Shift Security**

### Access Control:
- Employees can view own schedules
- Managers can view/edit department schedules
- Employees cannot see other employees' pay rates
- Shift swaps require manager approval

---

## Implementation Priority

### Phase 1 (Critical - Do First):
1. ✅ Password hashing (bcrypt)
2. ✅ JWT authentication
3. ✅ Environment variables for secrets
4. ✅ HTTPS enforcement
5. ✅ Database encryption for sensitive fields

### Phase 2 (High Priority):
6. ✅ Role-based access control
7. ✅ Input validation (Pydantic)
8. ✅ Rate limiting
9. ✅ Audit logging implementation
10. ✅ Error handling cleanup

### Phase 3 (Important):
11. ✅ CORS configuration
12. ✅ Security headers
13. ✅ Session management
14. ✅ Database SSL
15. ✅ Regular security audits

---

## Recommended Libraries

```txt
# Add to requirements.txt

# Authentication
bcrypt==4.1.2
PyJWT==2.8.0
python-jose[cryptography]==3.3.0

# Encryption
cryptography==41.0.7

# Validation
pydantic==2.5.0
email-validator==2.1.0

# Rate Limiting
slowapi==0.1.9

# Security
python-dotenv==1.0.0

# Monitoring
sentry-sdk==1.39.0  # Error tracking

# Security scanning
safety==2.3.5
bandit==1.7.5  # Security linting
```

---

## Files to Create

```
backend/
├── Utilities/
│   ├── auth.py          # Authentication functions
│   ├── encryption.py    # Field encryption
│   ├── validators.py    # Input validation
│   └── security.py      # Security utilities
├── Middleware/
│   ├── auth_middleware.py
│   ├── rate_limit.py
│   └── error_handler.py
├── Schemas/            # Pydantic validation schemas
│   ├── user.py
│   ├── employee.py
│   ├── order.py
│   └── ...
└── .env               # Secret keys (git-ignored)
```

---

## What You DON'T Need (Since No External APIs):

❌ API key management for external services
❌ OAuth2 provider integration (unless you want social login)
❌ Webhook signature verification
❌ IP whitelisting for external services
❌ API gateway/proxy configuration
❌ Third-party rate limiting

---

## Summary

Your backend needs standard web application security even without external APIs because:

1. **User data is sensitive** (passwords, emails, addresses)
2. **Employee data is highly sensitive** (SIN, bank accounts, salaries)
3. **Financial data requires protection** (orders, payments, payroll)
4. **Compliance requirements** (GDPR, labor laws, financial regulations)
5. **Internal threats exist** (unauthorized employee access)

The fact that you're NOT calling external APIs actually simplifies security (fewer attack vectors), but the internal data protection requirements remain critical.
