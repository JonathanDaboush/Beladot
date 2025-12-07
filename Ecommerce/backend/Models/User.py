from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    """
    Role-based access control for e-commerce and employee management.
    
    Hierarchy:
    - customer: Default role for shoppers (orders, cart, reviews)
    - customer_service: Staff handling customer inquiries and support
    - manager: Department managers (approve time tracking, scheduling, manage team)
    - analyst: Data analysis, metrics tracking, performance reporting (read-only access to analytics)
    - seller: Product management and sales tracking
    - transfer: Inventory management (import/export operations)
    - finance: Payment processing, employee payroll, financial operations
    - admin: Full system access (inherits all permissions)
    
    Permission model:
    - Admins can do everything
    - Finance handles payroll, payments, and financial data
    - Analysts have read-only access to all analytics, metrics, and reporting data
    - Managers approve time tracking, scheduling, leave requests for their department
    - Customer Service handles customer inquiries and basic support
    - Sellers manage products and view their sales
    - Transfer role handles inventory movements
    - Customers can only interact with shopping features
    """
    CUSTOMER = "customer"
    CUSTOMER_SERVICE = "customer_service"
    MANAGER = "manager"
    ANALYST = "analyst"
    SELLER = "seller"
    TRANSFER = "transfer"
    FINANCE = "finance"
    ADMIN = "admin"


class User(Base):
    """
    Identity anchor for all business activity.
    
    Responsibilities:
    - Guarantee identity uniqueness (email, normalized)
    - Secure credential storage (hashed_password)
    - Stable reference for audit trails
    - Basic profile data (identification only)
    
    Invariants:
    - email must be unique and normalized (lowercase)
    - created_at must be set
    - is_active must be checked before privileged operations
    
    Failure modes mitigated in AuthService:
    - Credential theft → bcrypt hashing, salt rounds
    - Brute-force attempts → rate-limiting
    - Account enumeration → sign-up/login throttles
    
    Permission model: User exposes role only.
    Complex access checks belong to AuthService.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Identity (unique, normalized email)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Profile (minimal, stable)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Credentials (secure storage)
    hashed_password = Column(String(255), nullable=False)
    
    # Authorization (minimal role, complex checks in AuthService)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.CUSTOMER, nullable=False, index=True)
    
    # Account status (checked before privileged operations)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Account security tracking
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset tokens (single-use, time-limited)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps (created_at is immutable anchor)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # User preferences
    preferred_currency = Column(String(3), default="USD", nullable=False)  # ISO 4217 currency code (USD, EUR, GBP, etc.)
    
    # Relationships (business activity anchored to User)
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    seller_profile = relationship("Seller", back_populates="user", uselist=False, cascade="all, delete-orphan")
    stored_payment_methods = relationship("StoredPaymentMethod", back_populates="user", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        # Email normalization: must be lowercase
        CheckConstraint("email = LOWER(email)", name="ck_user_email_lowercase"),
        
        # Email format: basic validation (contains @)
        CheckConstraint("email LIKE '%@%'", name="ck_user_email_format"),
        
        # Name fields: non-empty
        CheckConstraint("LENGTH(TRIM(first_name)) > 0", name="ck_user_first_name_nonempty"),
        CheckConstraint("LENGTH(TRIM(last_name)) > 0", name="ck_user_last_name_nonempty"),
        
        # Hashed password: must be set (never store plaintext)
        CheckConstraint("LENGTH(hashed_password) > 0", name="ck_user_password_nonempty"),
        
        # Failed login attempts: non-negative
        CheckConstraint("failed_login_attempts >= 0", name="ck_user_failed_attempts_nonnegative"),
        
        # Preferred currency: valid ISO 4217 code (3 uppercase letters)
        CheckConstraint("LENGTH(preferred_currency) = 3", name="ck_user_currency_length"),
        CheckConstraint("preferred_currency = UPPER(preferred_currency)", name="ck_user_currency_uppercase"),
        
        # Locked account: locked_until must be in the future when set
        # (Application enforces: unlock when locked_until < now())
        
        # Last login: must be after account creation
        CheckConstraint("last_login_at IS NULL OR last_login_at >= created_at", name="ck_user_last_login_after_created"),
        
        # Timestamps: updated_at >= created_at
        CheckConstraint("updated_at >= created_at", name="ck_user_updated_after_created"),
        
        # Index for active user queries (most common)
        Index("ix_user_active_role", "is_active", "role"),
        
        # Index for email verification status
        Index("ix_user_email_verified", "email_verified"),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role}, is_active={self.is_active})>"
    
    @property
    def full_name(self) -> str:
        """Basic helper for display purposes."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_locked(self) -> bool:
        """
        Check if account is temporarily locked.
        Application-level: AuthService enforces this before authentication.
        """
        if self.locked_until is None:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.locked_until
