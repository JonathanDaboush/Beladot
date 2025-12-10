"""
Authentication Routes
Handles user authentication and account management:
- Sign up (register new account)
- Log in (authenticate)
- Token refresh
- Forgot password / Password recovery
- Delete account (recursively delete seller account if exists)
- CSRF token generation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse, RefreshTokenRequest, MessageResponse
from Services.UserService import UserService
from Services.SellerService import SellerService
from Services.NotificationService import NotificationService
from Utilities.auth import create_access_token, create_refresh_token, get_current_user, verify_token
from Utilities.csrf_protection import generate_csrf_token
from Utilities.rate_limiting import rate_limiter_auth, rate_limiter_register, rate_limiter_moderate
from Utilities.email_service import send_password_reset, send_order_confirmation
from Models.PasswordResetToken import PasswordResetToken
from datetime import datetime, timedelta, timezone
import secrets

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================================
# REGISTRATION & LOGIN
# ============================================================================

@router.post("/signup", response_model=UserResponse, dependencies=[Depends(rate_limiter_register)])
async def signup(user_data: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Sign up - Register a new user account"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await user_service.create_user(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role
    )
    
    return user


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limiter_auth)])
async def login(credentials: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """Log in - Authenticate user and return JWT tokens"""
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse, dependencies=[Depends(rate_limiter_auth)])
async def refresh_access_token(token_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        payload = verify_token(token_data.refresh_token)
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user to include role in new token
        user_service = UserService(db)
        user = await user_service.get_user_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Generate new tokens
        access_token = create_access_token(data={"sub": email, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


# ============================================================================
# PASSWORD RECOVERY
# ============================================================================

@router.post("/forgot-password", response_model=MessageResponse, dependencies=[Depends(rate_limiter_auth)])
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    """Forgot password - Send password recovery email"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_email(email)
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate secure random token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Save token to database
    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        is_used=False
    )
    db.add(token_record)
    await db.commit()
    
    # Send password reset email
    try:
        await send_password_reset(
            to_email=email,
            reset_data={
                "user_name": f"{user.first_name} {user.last_name}",
                "reset_token": reset_token,
                "reset_url": f"http://localhost:3000/reset-password?token={reset_token}"
            }
        )
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", response_model=MessageResponse, dependencies=[Depends(rate_limiter_auth)])
async def reset_password(
    reset_token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """Reset password using recovery token"""
    from sqlalchemy import select
    
    # Find token in database
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == reset_token,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.now(timezone.utc)
        )
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user_service = UserService(db)
    user = await user_service.get_user_by_id(token_record.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await user_service.update_password(user.email, new_password)
    
    # Mark token as used
    token_record.is_used = True
    await db.commit()
    
    return {"message": "Password reset successfully"}


# ============================================================================
# ACCOUNT MANAGEMENT
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@router.delete("/account", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def delete_account(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account (recursively deletes seller account if exists)"""
    user_service = UserService(db)
    seller_service = SellerService(db)
    
    # Check if user has a seller account
    seller = await seller_service.get_seller_by_user_id(current_user.id)
    
    if seller:
        # Recursively delete seller account first
        await seller_service.delete_seller(seller.id)
    
    # Delete user account
    await user_service.delete_user(current_user.id)
    
    return {"message": "Account deleted successfully (including seller account if existed)"}


# ============================================================================
# CSRF PROTECTION
# ============================================================================

@router.get("/csrf-token")
async def get_csrf_token(current_user=Depends(get_current_user)):
    """Get CSRF token for state-changing operations"""
    csrf_token = generate_csrf_token(current_user.id)
    return {"csrf_token": csrf_token}


@router.post("/logout", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def logout(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Logout - Invalidate user session.
    
    In a stateless JWT system, this primarily serves to:
    - Log the logout event
    - Provide a clean logout endpoint for the client
    
    Note: Client should discard tokens after logout.
    """
    from datetime import datetime, timezone
    from Services.AuditLogService import AuditLogService
    
    # Log the logout event
    audit_service = AuditLogService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        action="LOGOUT",
        entity_type="User",
        entity_id=current_user.id,
        details={"timestamp": datetime.now(timezone.utc).isoformat()}
    )
    
    return {"message": "Logged out successfully"}

