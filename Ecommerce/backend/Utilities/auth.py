"""Authentication and authorization utilities for FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from database import get_db

settings = Settings()
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data (typically {"sub": user_id})
        expires_delta: Token expiration time (default from settings)
        
    Returns:
        Encoded JWT token
        
    Example:
        >>> token = create_access_token({"sub": str(user.id)})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token (longer expiration).
    
    Args:
        data: Payload data
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate JWT token and return current user.
    
    Use as dependency in protected routes:
        @app.get("/api/profile")
        async def get_profile(current_user = Depends(get_current_user)):
            return current_user
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # Decode and validate token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Check token type (access vs refresh)
        token_type = payload.get("type")
        if token_type == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot use refresh token for authentication"
            )
        
    except JWTError as e:
        raise credentials_exception
    
    # Fetch user from database
    from Repositories.UserRepository import UserRepository
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Get current user and verify they are active.
    
    Use for routes that require active account:
        @app.get("/api/orders")
        async def get_orders(user = Depends(get_current_active_user)):
            ...
    """
    # Add any additional checks here (e.g., user.is_active)
    # if hasattr(current_user, 'is_active') and not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


def require_role(*allowed_roles: str):
    """
    Decorator to require specific user roles.
    
    Usage:
        @app.get("/admin/users")
        @require_role("admin", "employee")
        async def list_users(current_user = Depends(get_current_user)):
            ...
    
    Args:
        allowed_roles: Roles that can access this endpoint
    """
    async def role_checker(current_user = Depends(get_current_user)):
        if not hasattr(current_user, 'role'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not defined"
            )
        
        # Admin has access to everything
        if current_user.role == "admin":
            return current_user
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


async def get_current_admin_user(current_user = Depends(get_current_user)):
    """
    Shorthand for admin-only routes.
    
    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(user_id: int, admin = Depends(get_current_admin_user)):
            ...
    """
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_customer_service(current_user = Depends(get_current_user)):
    """
    Require customer_service or admin.
    
    Use for handling customer inquiries and support.
    
    Usage:
        @app.get("/api/customer-service/inquiries")
        async def get_inquiries(cs_user = Depends(get_current_customer_service)):
            ...
    """
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not defined"
        )
    
    if current_user.role not in ["customer_service", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer service access required"
        )
    
    return current_user


async def get_current_finance(current_user = Depends(get_current_user)):
    """
    Require finance or admin.
    
    Use for payroll processing, payments, and financial operations.
    
    Usage:
        @app.post("/api/finance/payroll")
        async def process_payroll(finance_user = Depends(get_current_finance)):
            ...
    """
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not defined"
        )
    
    if current_user.role not in ["finance", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance access required"
        )
    
    return current_user


async def get_current_seller(current_user = Depends(get_current_user)):
    """
    Require seller or admin.
    
    Use for product management and sales tracking.
    
    Usage:
        @app.get("/api/seller/sales")
        async def get_sales(seller = Depends(get_current_seller)):
            ...
    """
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not defined"
        )
    
    if current_user.role not in ["seller", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller access required"
        )
    
    return current_user


async def get_current_transfer_user(current_user = Depends(get_current_user)):
    """
    Require transfer role or admin.
    
    Use for inventory import/export operations.
    
    Usage:
        @app.post("/api/transfer/import")
        async def import_products(transfer_user = Depends(get_current_transfer_user)):
            ...
    """
    if not hasattr(current_user, 'role'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role not defined"
        )
    
    if current_user.role not in ["transfer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transfer access required"
        )
    
    return current_user


def check_permission(user, required_role: str) -> bool:
    """
    Helper function to check if user has required permission.
    
    Args:
        user: User object with role attribute
        required_role: Role name to check
        
    Returns:
        True if user has permission
        
    Usage in services:
        if not check_permission(user, "seller"):
            raise ValueError("Insufficient permissions")
    """
    if not hasattr(user, 'role'):
        return False
    
    # Admin has all permissions
    if user.role == "admin":
        return True
    
    return user.role == required_role


def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token without database lookup.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user if authenticated, None otherwise.
    
    Use for optional authentication:
        @app.get("/api/products")
        async def list_products(user = Depends(get_optional_user)):
            # user is None if not authenticated
            if user:
                # Show personalized recommendations
            else:
                # Show generic products
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
