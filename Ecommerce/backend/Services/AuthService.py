from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING
from uuid import UUID
from Utilities.email import EmailService
if TYPE_CHECKING:
    from Ecommerce.backend.Classes.User import User as UserClass
else:
    UserClass = "User"

from Ecommerce.backend.Classes import Cart, User
from Ecommerce.backend.Repositories import CartRepository as CartRepo
class AuthService:
    """
    Authentication and Authorization Service
    Handles user registration, authentication, password reset, and access control
    """
    
    def __init__(self, user_repository, session_repository, audit_repository):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.audit_repository = audit_repository
        self.email_service = EmailService()
    def register_user(self, email: str, password: str, first_name: str | None, last_name: str | None):
        """
        Create a new User account.
        Responsibilities: normalize email, validate uniqueness, hash password securely,
        create user record, possibly create initial cart/session, and queue verification email.
        Do not auto-log the user in without verification unless policy allows.
        Emit audit log for account creation and return user object.
        """
        user=None
        
        try:
            user = self.user_repository.get_by_email(email)
        except Exception:
            pass
        
        if user is None:
            new_user = User(
                id=None,
                email=email.lower(),
                first_name=first_name,
                last_name=last_name or "",
                hashed_password=None,
                role="customer",
                is_active=True,
                email_verified=False,
                last_login_at=None,
                failed_login_attempts=0,
                locked_until=None,
                created_at=datetime.now(),
                updated_at=None
            )
            new_user.set_password(password)
            
            validated, errors = new_user.validate()
            if not validated:
                raise ValueError(f"User validation failed: {errors}")
            
            user = self.user_repository.create(new_user)
            self.audit_repository.create_audit_log({
                "actor_id": user.id,
                "action": "user.registered",
                "target_type": "user",
                "target_id": user.id,
                "metadata": {"email": user.email}
            })
            
            cart = Cart(user_id=user.id, created_at=datetime.now(), updated_at=datetime.now())
            cart_repo = CartRepo(self.user_repository.db_session)
            cart_repo.create(cart)
            self.email_service.send_account_created(
                to_email=user.email,
                first_name=user.first_name + (user.last_name or ""),
                verification_link=f"https://yourstore.com/verify/{user.id}"
            )
            return user
    
    def _verify_credentials(self, email: str, password: str) -> UserClass | None:
        """
        Internal helper to verify user credentials.
        Returns User object if valid, None if invalid.
        """
        user = None
        try:
            user = self.user_repository.get_by_email(email.lower())
        except Exception:
            return None
        
        if user is None:
            return None
        
        if not user.is_active:
            return None
        
        if user.locked_until and user.locked_until > datetime.now():
            return None
        
        if not user.check_password(password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now() + timedelta(minutes=30)
            self.user_repository.update(user)
            return None
        
        return user
    
    def authenticate(self, email: str, password: str) -> dict[str, Any]:
        """
        Verify credentials, perform rate-limiting checks, and issue tokens.
        Responsibilities: return {user, access_token, refresh_token} on success,
        update last_login_at, and record successful/failed attempts in audit/tracking systems.
        On multi-factor flows, return a state object indicating next steps.
        """
        user = self._verify_credentials(email, password)
        
        if user is None:
            self.audit_repository.create_audit_log({
                "actor_id": None,
                "action": "auth.failed",
                "target_type": "user",
                "target_id": None,
                "metadata": {"email": email.lower()}
            })
            raise ValueError("Invalid credentials")
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now()
        self.user_repository.update(user)
        
        # Create session (implement token generation as needed)
        session_token = self._generate_token()
        session = self.session_repository.create_session({
            "user_id": user.id,
            "token": session_token,
            "expires_at": datetime.now() + timedelta(days=7)
        })
        
        self.audit_repository.create_audit_log({
            "actor_id": user.id,
            "action": "auth.success",
            "target_type": "user",
            "target_id": user.id,
            "metadata": {"email": user.email}
        })
        
        return {
            "user": user,
            "access_token": session_token,
            "refresh_token": self._generate_token()
        }
    
    def _generate_token(self) -> str:
        """Generate a secure random token for sessions."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def forgot_password(self, email: str) -> None:
        """
        Start password reset flow by generating a secure single-use token,
        storing it with expiry, and enqueue a password reset email job.
        Must avoid response behavior that reveals whether email exists (mitigate enumeration).
        """
        user = None
        try:
            user = self.user_repository.get_by_email(email.lower())
        except Exception:
            return 
        
        if user is not None:
            reset_token = self._generate_token()
            
            # Store the reset token with expiration (1 hour)
            user.password_reset_token = reset_token
            user.password_reset_expires = datetime.now() + timedelta(hours=1)
            self.user_repository.update(user)
            
            self.audit_repository.create_audit_log({
                "actor_id": user.id,
                "action": "password.reset_requested",
                "target_type": "user",
                "target_id": user.id,
                "metadata": {"email": user.email}
            })
            
            self.email_service.send_password_reset(
                to_email=user.email, 
                first_name=user.first_name, 
                reset_link=f"https://yourstore.com/reset-password?token={reset_token}"
            )
        
        
            
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Complete password reset using the token from email.
        Returns True if successful, False if token invalid/expired.
        """
        user = self.user_repository.get_by_reset_token(token)
        
        if user is None:
            return False
        
        if user.password_reset_expires is None or user.password_reset_expires < datetime.now():
            return False
        
        # Reset password and clear token (single-use)
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.failed_login_attempts = 0
        user.locked_until = None
        self.user_repository.update(user)
        
        self.audit_repository.create_audit_log({
            "actor_id": user.id,
            "action": "password.reset_completed",
            "target_type": "user",
            "target_id": user.id,
            "metadata": {"email": user.email}
        })
        
        return True
    
    def validate_token(self, token: str) -> UserClass | None:
        """
        Validate a session token and return the associated user.
        Returns None if token is invalid or expired.
        """
        session = self.session_repository.get_by_token(token)
        
        if session is None:
            return None
        
        if session.expires_at < datetime.now():
            return None
        
        user = self.user_repository.get_by_id(session.user_id)
        
        if user is None or not user.is_active:
            return None
        
        return user
    
    def logout(self, token: str) -> bool:
        """
        Invalidate a session token (logout).
        Returns True if successful.
        """
        session = self.session_repository.get_by_token(token)
        
        if session is not None:
            self.session_repository.delete(session.id)
            
            self.audit_repository.create_audit_log({
                "actor_id": session.user_id,
                "action": "auth.logout",
                "target_type": "session",
                "target_id": session.id,
                "metadata": {}
            })
        
        return True
    
    def authorize(self, user: User, action: str, resource: str, resource_id: UUID | None = None) -> bool:
        """
        Authoritative access control decision combining role checks and resource ownership rules.
        Responsibilities: consult User.role, resource metadata, and object-level ownership where applicable.
        This method should be the gate used by controllers before sensitive actions.
        Return boolean and optionally raise standardized PermissionDenied exceptions for clarity.
        """
        if user is None or not user.is_active:
            return False
        
        # Check role-based permissions using User.can()
        if not user.can(action, resource):
            return False
        
        # TODO: Add resource ownership checks if resource_id provided
        # e.g., Check if user owns the order, cart item, etc.
        
        return True
