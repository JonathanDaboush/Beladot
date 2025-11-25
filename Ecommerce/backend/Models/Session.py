from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Session(Base):
    """
    Guest session for anonymous browsing and cart persistence.
    Links anonymous users to carts before they register/login.
    When user logs in, their session cart can be merged with their user cart.
    
    Security:
    - Tokens should be stored in HTTPOnly cookies
    - Rotate tokens on login/privilege escalation
    - Keep minimal PII in sessions
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
