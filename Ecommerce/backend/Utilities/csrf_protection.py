"""CSRF (Cross-Site Request Forgery) protection utilities."""
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException, status

from config import Settings

settings = Settings()

# In-memory CSRF token store (use Redis in production)
csrf_tokens = {}


def generate_csrf_token(session_id: str) -> str:
    """
    Generate CSRF token for session.
    
    Args:
        session_id: User session identifier
        
    Returns:
        CSRF token string
        
    Example:
        >>> token = generate_csrf_token(str(user.id))
    """
    # Generate random token
    token = secrets.token_urlsafe(32)
    
    # Store with expiration (1 hour)
    expiration = datetime.utcnow() + timedelta(hours=1)
    csrf_tokens[session_id] = {
        'token': token,
        'expires': expiration
    }
    
    return token


def validate_csrf_token(session_id: str, token: str) -> bool:
    """
    Validate CSRF token for session.
    
    Args:
        session_id: User session identifier
        token: CSRF token to validate
        
    Returns:
        True if valid, False otherwise
    """
    if session_id not in csrf_tokens:
        return False
    
    stored = csrf_tokens[session_id]
    
    # Check expiration
    if datetime.utcnow() > stored['expires']:
        del csrf_tokens[session_id]
        return False
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(stored['token'], token)


def get_csrf_token_from_request(request: Request) -> Optional[str]:
    """
    Extract CSRF token from request.
    
    Checks in order:
    1. X-CSRF-Token header
    2. csrf_token form field
    3. csrf_token query parameter
    
    Args:
        request: FastAPI request object
        
    Returns:
        CSRF token or None
    """
    # Check header
    token = request.headers.get('X-CSRF-Token')
    if token:
        return token
    
    # Check form data (for multipart/form-data)
    if hasattr(request, '_form'):
        token = request._form.get('csrf_token')
        if token:
            return token
    
    # Check query params
    token = request.query_params.get('csrf_token')
    return token


async def verify_csrf_token(request: Request, user_id: int):
    """
    Verify CSRF token from request.
    
    Use as dependency for state-changing operations:
        @app.post("/api/orders")
        async def create_order(
            order: CreateOrderRequest,
            user = Depends(get_current_user),
            csrf_check = Depends(verify_csrf_token)
        ):
            ...
    
    Args:
        request: FastAPI request
        user_id: Current user ID
        
    Raises:
        HTTPException: 403 if CSRF token invalid or missing
    """
    token = get_csrf_token_from_request(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    if not validate_csrf_token(str(user_id), token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )


def cleanup_expired_tokens():
    """
    Remove expired CSRF tokens from store.
    
    Call this periodically (e.g., with FastAPI background tasks):
        @app.on_event("startup")
        @repeat_every(seconds=3600)  # Every hour
        async def cleanup_csrf():
            cleanup_expired_tokens()
    """
    now = datetime.utcnow()
    expired = [
        session_id for session_id, data in csrf_tokens.items()
        if now > data['expires']
    ]
    
    for session_id in expired:
        del csrf_tokens[session_id]


def create_signed_token(data: str) -> str:
    """
    Create HMAC-signed token for additional security.
    
    Use for sensitive operations like password reset links.
    
    Args:
        data: Data to sign (e.g., user_id:timestamp)
        
    Returns:
        Signed token
    """
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{data}:{signature}"


def verify_signed_token(token: str, max_age_seconds: int = 3600) -> Optional[str]:
    """
    Verify HMAC-signed token.
    
    Args:
        token: Signed token to verify
        max_age_seconds: Maximum token age in seconds
        
    Returns:
        Original data if valid, None otherwise
    """
    try:
        parts = token.split(':')
        if len(parts) != 3:  # data:timestamp:signature
            return None
        
        data, timestamp, signature = parts
        
        # Verify signature
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            f"{data}:{timestamp}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Check age
        token_time = datetime.fromtimestamp(int(timestamp))
        if datetime.utcnow() - token_time > timedelta(seconds=max_age_seconds):
            return None
        
        return data
        
    except (ValueError, OverflowError):
        return None
