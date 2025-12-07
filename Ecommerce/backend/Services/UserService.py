"""User service for authentication and user management."""
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import Optional

from Repositories.UserRepository import UserRepository
from Models.User import User, UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    User service handling authentication and user management.
    
    Responsibilities:
    - User registration with role assignment
    - Authentication (login)
    - Password hashing and verification
    - Role-based access validation
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        role: str = "customer"
    ) -> User:
        """
        Create new user with role.
        
        Args:
            email: User email (unique)
            password: Plain text password (will be hashed)
            first_name: First name
            last_name: Last name
            phone: Phone number (optional)
            role: User role (customer, employee, seller, transfer, admin)
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If email exists or invalid role
        """
        # Validate role
        valid_roles = ["customer", "employee", "seller", "transfer", "admin"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role: {role}")
        
        # Check if email exists
        existing_user = await self.user_repo.get_by_email(email.lower())
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        # Create user
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=UserRole(role)
        )
        
        return await self.user_repo.create(user)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user by email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User object if authenticated, None otherwise
        """
        user = await self.user_repo.get_by_email(email.lower())
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        # Check if account is active
        if not user.is_active:
            return None
        
        # Check if account is locked
        if user.is_locked:
            return None
        
        # Update last login
        from datetime import datetime, timezone
        user.last_login_at = datetime.now(timezone.utc)
        user.failed_login_attempts = 0
        await self.user_repo.update(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repo.get_by_email(email.lower())
    
    async def update_user_role(self, user_id: int, new_role: str, admin_user_id: int) -> User:
        """
        Update user role (admin only).
        
        Args:
            user_id: User ID to update
            new_role: New role to assign
            admin_user_id: Admin performing the action
            
        Returns:
            Updated user
            
        Raises:
            ValueError: If admin not authorized or invalid role
        """
        # Verify admin
        admin = await self.user_repo.get_by_id(admin_user_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise ValueError("Only admins can change user roles")
        
        # Validate role
        valid_roles = ["customer", "employee", "seller", "transfer", "admin"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role: {new_role}")
        
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update role
        user.role = UserRole(new_role)
        return await self.user_repo.update(user)
    
    def check_permission(self, user: User, required_role: str) -> bool:
        """
        Check if user has required permission.
        
        Args:
            user: User object
            required_role: Required role
            
        Returns:
            True if user has permission
            
        Note:
            Admins have all permissions
        """
        # Admin has all permissions
        if user.role == UserRole.ADMIN:
            return True
        
        return user.role.value == required_role
    
    async def update_password(self, email: str, new_password: str) -> User:
        """
        Update user password.
        
        Args:
            email: User email
            new_password: New plain text password (will be hashed)
            
        Returns:
            Updated user
            
        Raises:
            ValueError: If user not found
        """
        user = await self.user_repo.get_by_email(email.lower())
        if not user:
            raise ValueError("User not found")
        
        # Hash new password
        user.hashed_password = self.hash_password(new_password)
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.is_locked = False
        
        return await self.user_repo.update(user)
    
    async def delete_user(self, user_id: int) -> None:
        """
        Delete user account.
        
        Args:
            user_id: User ID to delete
            
        Raises:
            ValueError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        await self.user_repo.delete(user)

