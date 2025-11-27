from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class APIKey(Base):
    """
    SQLAlchemy ORM model for api_keys table.
    
    Manages programmatic access credentials for third-party integrations
    and internal service-to-service authentication. Supports OAuth-like
    scopes for fine-grained permission control.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Key: user_id -> users.id (CASCADE delete)
        - Indexes: id (primary), key_hash (unique), user_id
        
    Data Integrity:
        - Key hash stored (never plain text)
        - Scopes array cannot be empty (at least one permission required)
        - Cannot be both active and revoked simultaneously
        - Expiration date must be after creation date
        - Revoked keys automatically become inactive
        
    Relationships:
        - Many-to-one with User (one user can have multiple API keys)
        
    Security Design:
        - key_hash: SHA-256 hash of actual API key (plain key shown once at creation)
        - scopes: JSON array of permissions (e.g., ["products:read", "orders:write"])
        - is_active: Manual enable/disable without revocation
        - is_revoked: Permanent invalidation (cannot be reactivated)
        - expires_at: Optional automatic expiration
        - last_used_at: Audit trail for unused key cleanup
        
    Lifecycle:
        1. Creation: Generate random key, hash it, store hash
        2. Active: Verify hash on each request, check scopes
        3. Expiration: Auto-deactivate after expires_at
        4. Revocation: Permanent invalidation (security incident)
        
    Design Notes:
        - Scopes follow resource:action pattern (products:read, orders:write)
        - Keys should be rotated periodically (30-90 days)
        - Revoked keys retained for audit history
        - Last used tracking enables security monitoring
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    scopes = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    
    __table_args__ = (
        # Name cannot be empty (for identification)
        CheckConstraint("length(trim(name)) > 0", name='check_name_present'),
        
        # Scopes array cannot be empty (API key must have at least one permission)
        CheckConstraint("json_array_length(scopes) > 0", name='check_scopes_not_empty'),
        
        # Cannot be both active and revoked
        CheckConstraint("NOT (is_active = true AND is_revoked = true)", 
                    name='check_not_active_and_revoked'),
        
        # If revoked, cannot be active
        CheckConstraint("is_revoked = false OR is_active = false", 
                    name='check_revoked_means_inactive'),
        
        # Expires_at must be in the future when set
        CheckConstraint("expires_at IS NULL OR expires_at > created_at", 
                    name='check_expires_after_created'),
    )
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.name}, is_active={self.is_active})>"
