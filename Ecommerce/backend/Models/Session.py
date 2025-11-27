from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Session(Base):
    """
    SQLAlchemy ORM model for sessions table.
    
    Manages guest and authenticated user sessions for cart persistence, activity
    tracking, and anonymous browsing. Enables seamless guest-to-authenticated
    transitions with cart merging.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: cart_id -> carts.id (SET NULL), user_id -> users.id (SET NULL)
        - Indexes: id (primary), session_token (unique), cart_id, user_id, expires_at
        
    Data Integrity:
        - Session token must be unique and non-empty
        - Expiration date must be after creation
        - Last activity must be after or equal to creation
        - Authenticated sessions must have user_id
        - Unauthenticated sessions must have user_id = NULL
        
    Relationships:
        - Many-to-one with User (user can have multiple sessions across devices)
        - Many-to-one with Cart (session linked to shopping cart)
        
    Session Types:
        - Guest session: user_id = NULL, is_authenticated = false
        - Authenticated session: user_id set, is_authenticated = true
        
    Session Lifecycle:
        1. Guest visits site
        2. Create Session with random token, is_authenticated=false
        3. Store token in HTTPOnly cookie
        4. Guest adds items to cart (link cart_id)
        5. Guest registers/logs in:
           a. Set user_id, is_authenticated=true
           b. Merge session cart with user's existing cart
           c. Rotate session token (security best practice)
        6. Session expires after timeout or user logs out
        
    Token Generation:
        - Format: 64+ character random string (base64 encoded)
        - Source: secrets.token_urlsafe(48) -> ~64 chars
        - Collision: Unique constraint prevents duplicates
        - Example: "kF3xQ7mN9pL2vR8sT6wY4zU1hJ5gD0cB"
        
    Security:
        - HTTPOnly cookies: Prevent JavaScript access (XSS protection)
        - Secure flag: HTTPS only transmission
        - SameSite: Lax/Strict (CSRF protection)
        - Token rotation: Generate new token on privilege change (login, role escalation)
        - Minimal PII: Don't store sensitive data (payment info, full address)
        - IP tracking: Detect session hijacking (IP address changes)
        - User agent: Fingerprint device/browser
        
    Expiration:
        - Guest sessions: 30 days (long for cart persistence)
        - Authenticated sessions: 7 days (remember me) or session duration
        - Rolling expiration: Update expires_at on activity
        - Cleanup job: DELETE WHERE expires_at < NOW()
        
    Cart Merging:
        - Scenario: Guest cart has items, user logs in with existing cart
        - Strategy 1: Merge carts (combine items, keep unique product+variant)
        - Strategy 2: Replace guest cart with user cart
        - Strategy 3: Ask user preference (show both carts)
        - Implementation: CartService.merge_carts(guest_cart_id, user_cart_id)
        
    Activity Tracking:
        - last_activity_at: Updated on each request (sliding window)
        - Idle timeout: Log out if last_activity_at > 30 min ago
        - Analytics: Track active users (last_activity_at within 15 min)
        
    Multi-Device:
        - One user can have multiple active sessions
        - Separate session per device/browser
        - Session list: Show user their active sessions ("Logged in devices")
        - Logout all: Revoke all sessions except current
        
    IP Address:
        - IPv4: "192.168.1.1" (max 15 chars)
        - IPv6: "2001:0db8:85a3:0000:0000:8a2e:0370:7334" (max 45 chars)
        - Uses: Geolocation, fraud detection, rate limiting
        
    User Agent:
        - Browser: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
        - Mobile: "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
        - Bot detection: Identify scrapers/crawlers
        
    Privacy:
        - GDPR: Sessions count as personal data (if linked to user_id)
        - Deletion: Cascade delete when user deleted (SET NULL)
        - Anonymization: Clear user_id, cart_id on user account deletion
        
    Performance:
        - Index on session_token: Fast lookup on each request
        - Index on expires_at: Efficient cleanup queries
        - Cache: Store active sessions in Redis (reduce DB load)
        - TTL: Expire Redis sessions automatically
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_authenticated = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    user = relationship("User", back_populates="sessions")
    cart = relationship("Cart")
    
    __table_args__ = (
        CheckConstraint("length(trim(session_token)) > 0", name='check_session_token_present'),
        CheckConstraint("expires_at > created_at", name='check_expires_after_created'),
        CheckConstraint("last_activity_at >= created_at", name='check_activity_after_created'),
        CheckConstraint("(user_id IS NULL AND is_authenticated = false) OR (user_id IS NOT NULL)", name='check_authenticated_has_user'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
