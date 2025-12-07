# Security Implementation Guide

## ✅ SQL Injection Protection (Current Status: EXCELLENT)

Your application is **already protected** from SQL injection attacks because you're using SQLAlchemy ORM with parameterized queries throughout the codebase.

### What You're Doing Right:
```python
# ✅ SAFE - All your repositories use this pattern
result = await self.db.execute(select(User).where(User.id == user_id))
result = await self.db.execute(select(User).where(User.email == email))
```

### Rules to Maintain:
1. **NEVER concatenate user input into SQL strings**
2. **ALWAYS use SQLAlchemy ORM or parameterized queries**
3. **Avoid `text()` with f-strings** (only use in admin scripts, never with user input)

---

## 🔒 Additional Security Measures to Implement

### 1. **Input Validation & Sanitization** (HIGH PRIORITY)

#### Implement Pydantic Models for All Endpoints:
```python
# Add to your app.py for each endpoint
from pydantic import BaseModel, EmailStr, constr, conint, validator

class CreateUserRequest(BaseModel):
    email: EmailStr  # Validates email format
    password: constr(min_length=8, max_length=128)  # Length constraints
    first_name: constr(min_length=1, max_length=50)
    last_name: constr(min_length=1, max_length=50)
    
    @validator('email')
    def email_lowercase(cls, v):
        return v.lower()
    
    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        # Remove any potential XSS characters
        return v.strip()

class AddToCartRequest(BaseModel):
    product_id: conint(gt=0)  # Must be positive
    quantity: conint(gt=0, le=100)  # Between 1-100
    
class CreateOrderRequest(BaseModel):
    cart_id: conint(gt=0)
    shipping_address: dict
    payment_method: dict
    idempotency_key: Optional[constr(max_length=255)]
```

#### Add Input Sanitization Utility:
```python
# Create: Utilities/input_sanitization.py
import re
import html
from typing import Any

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string safe for storage and display
    """
    if not value:
        return ""
    
    # Trim to max length
    value = value[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # HTML escape to prevent XSS
    value = html.escape(value)
    
    # Strip leading/trailing whitespace
    return value.strip()

def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifiers (table/column names) for dynamic queries.
    Use ONLY in admin scripts, NEVER with user input.
    """
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")
    return identifier
```

---

### 2. **Authentication & Authorization** (HIGH PRIORITY)

#### Create Auth Middleware:
```python
# Create: Utilities/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import settings

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate JWT token and return current user.
    Use as dependency in protected routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    from Repositories.UserRepository import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    
    return user

def require_role(*allowed_roles: str):
    """
    Decorator to require specific user roles.
    Usage: @require_role("admin", "support")
    """
    def decorator(func):
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

---

### 3. **Rate Limiting** (MEDIUM PRIORITY - Application Level)

```python
# Create: Utilities/rate_limiter.py
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, use Redis-based solution.
    """
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        """
        Check if identifier has exceeded rate limit.
        
        Args:
            identifier: IP address or user ID
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window_seconds)
            
            # Remove old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]
            
            # Check limit
            if len(self.requests[identifier]) >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {window_seconds} seconds."
                )
            
            # Add current request
            self.requests[identifier].append(now)

# Global instance
rate_limiter = RateLimiter()

# Middleware
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting based on IP address."""
    client_ip = request.client.host
    
    # Skip rate limiting for health checks
    if request.url.path == "/health":
        return await call_next(request)
    
    # Check rate limit (more lenient limits)
    await rate_limiter.check_rate_limit(
        identifier=client_ip,
        max_requests=100,  # 100 requests
        window_seconds=60   # per minute
    )
    
    return await call_next(request)
```

---

### 4. **CSRF Protection** (HIGH PRIORITY for Web Forms)

```python
# Create: Utilities/csrf.py
from fastapi import HTTPException, Request, Response
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta

class CSRFProtection:
    """CSRF token generation and validation."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        timestamp = str(int(datetime.utcnow().timestamp()))
        message = f"{session_id}:{timestamp}".encode()
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        return f"{timestamp}.{signature}"
    
    def validate_token(self, token: str, session_id: str, max_age_seconds: int = 3600) -> bool:
        """Validate CSRF token."""
        try:
            timestamp_str, signature = token.split('.')
            timestamp = int(timestamp_str)
            
            # Check age
            now = int(datetime.utcnow().timestamp())
            if now - timestamp > max_age_seconds:
                return False
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}".encode()
            expected_sig = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(signature, expected_sig)
        except (ValueError, AttributeError):
            return False

async def csrf_protect(request: Request):
    """Middleware to validate CSRF tokens on state-changing requests."""
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            raise HTTPException(status_code=403, detail="CSRF token missing")
        
        # Validate token (get session from cookie/header)
        session_id = request.cookies.get("session_id", "")
        csrf = CSRFProtection(settings.SECRET_KEY)
        
        if not csrf.validate_token(csrf_token, session_id):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")
```

---

### 5. **XSS Protection** (HIGH PRIORITY)

```python
# Already handled by:
# 1. Input sanitization (html.escape in sanitize_string)
# 2. Pydantic validation
# 3. Content-Security-Policy headers (add in app.py)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add to app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    return response
```

---

### 6. **Sensitive Data Protection**

```python
# Create: Utilities/encryption.py
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    """Encrypt sensitive data at rest."""
    
    def __init__(self, key: bytes = None):
        self.key = key or base64.urlsafe_b64encode(os.urandom(32))
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive string data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Use for:
# - Credit card numbers (if storing - better to use tokens from payment gateway)
# - SSN/Tax IDs
# - Personal health information
```

---

### 7. **Audit Logging** (MEDIUM PRIORITY)

```python
# Enhance existing AuditLog model usage
async def log_security_event(
    db: AsyncSession,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: int = None,
    ip_address: str = None,
    details: dict = None
):
    """Log security-relevant events."""
    from Models.AuditLog import AuditLog
    from Repositories.AuditLogRepository import AuditLogRepository
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        details=details or {}
    )
    
    repo = AuditLogRepository(db)
    await repo.create(audit_log)

# Log these events:
# - Failed login attempts (brute force detection)
# - Password changes
# - Permission changes
# - Financial transactions
# - Data exports
# - Admin actions
```

---

### 8. **Password Security Enhancements**

```python
# Add to Utilities/hashing.py

def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password too long (max 128 characters)"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    # Check against common passwords
    common_passwords = ["password", "123456", "qwerty", "admin"]
    if password.lower() in common_passwords:
        return False, "Password is too common"
    
    return True, ""

def check_password_breach(password: str) -> bool:
    """
    Check if password has been in a data breach (using k-anonymity).
    Uses Have I Been Pwned API safely.
    """
    import hashlib
    import requests
    
    # Hash password
    sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]
    
    # Check against HIBP API (k-anonymity - only send first 5 chars)
    response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    
    if response.status_code == 200:
        hashes = response.text.split('\r\n')
        for hash_line in hashes:
            hash_suffix, count = hash_line.split(':')
            if hash_suffix == suffix:
                return True  # Password found in breach
    
    return False  # Password not found
```

---

### 9. **Session Security**

```python
# Update config.py
class Settings(BaseSettings):
    # ... existing ...
    
    # Session security
    SESSION_COOKIE_SECURE: bool = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY: bool = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE: str = "lax"  # CSRF protection
    SESSION_MAX_AGE: int = 3600  # 1 hour
    
    # Security
    ALLOWED_HOSTS: List[str] = ["yourdomain.com"]
    ENABLE_RATE_LIMITING: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
```

---

### 10. **API Security Checklist**

```python
# Add to app.py startup
@app.on_event("startup")
async def security_check():
    """Verify security configuration on startup."""
    if settings.DEBUG and os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("DEBUG mode enabled in production!")
    
    if settings.SECRET_KEY == "your-secret-key-change-this-in-production":
        raise RuntimeError("Default SECRET_KEY detected!")
    
    if len(settings.SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY too short (min 32 characters)")
    
    print("✅ Security checks passed")
```

---

## 📋 Implementation Priority

### Critical (Implement Before Production):
1. ✅ SQL Injection Protection (Already done)
2. ⚠️ Input validation with Pydantic models
3. ⚠️ Authentication middleware (JWT)
4. ⚠️ Authorization (role-based access)
5. ⚠️ HTTPS enforcement
6. ⚠️ Security headers
7. ⚠️ Password strength requirements
8. ⚠️ CSRF protection

### Important (Implement Soon):
9. Rate limiting (application level)
10. Audit logging for sensitive operations
11. Input sanitization
12. Failed login tracking
13. Session security

### Nice to Have:
14. Password breach checking
15. Data encryption at rest
16. Advanced rate limiting (Redis-based)
17. 2FA support

---

## 🔍 Code Review Checklist

Before deploying:
- [ ] All user input validated with Pydantic
- [ ] All sensitive routes require authentication
- [ ] Role-based authorization on admin routes
- [ ] DEBUG=False in production
- [ ] Secure SECRET_KEY (32+ chars, random)
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Audit logging on financial operations
- [ ] Password requirements enforced
- [ ] CSRF tokens on forms
- [ ] No secrets in code (use environment variables)

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
