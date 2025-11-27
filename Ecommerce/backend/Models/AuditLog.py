from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class AuditLog(Base):
    """
    SQLAlchemy ORM model for audit_logs table.
    
    Append-only immutable security and operational trail for auditing, compliance,
    forensics, and debugging. Captures who did what, when, and to which resource
    with contextual metadata.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Indexes: id (primary), actor_id, action, target_type, target_id, created_at
        
    Data Integrity:
        - Actor type must be: user, api_key, system, or admin
        - Action, target_type, and target_id cannot be empty
        - IP address max length 45 chars (supports IPv6)
        - CRITICAL: Records are IMMUTABLE - no updates or deletes (compliance requirement)
        
    Actor Types:
        - user: End-user actions (login, purchase, update profile)
        - api_key: Third-party integration actions (API calls)
        - system: Automated system actions (cron jobs, scheduled tasks)
        - admin: Administrative actions (manual overrides, support interventions)
        
    Design Notes:
        - actor_id: User ID or API key ID (nullable for system/anonymous actions)
        - actor_email: Snapshot of email at action time (denormalized for audit trail)
        - action: Verb describing action (e.g., "user.login", "order.created", "product.updated")
        - target_type: Entity type affected (e.g., "order", "product", "user")
        - target_id: Entity ID as string (supports composite keys)
        - item_metadata: JSON containing before/after state, request details, etc.
        - ip_address: Source IP for security analysis
        - user_agent: Browser/client info for session tracking
        
    Compliance:
        - GDPR: Track data access and modifications
        - SOX: Financial transaction audit trail
        - PCI DSS: Payment data access logging
        - HIPAA: Protected health information access
        - Retention: Typically 7+ years for financial/healthcare
        
    Query Patterns:
        - User activity: SELECT * WHERE actor_id = X ORDER BY created_at DESC
        - Entity history: SELECT * WHERE target_type = 'order' AND target_id = '123'
        - Admin actions: SELECT * WHERE actor_type = 'admin' AND created_at > '2024-01-01'
        - Security audit: SELECT * WHERE action LIKE '%.delete' OR action LIKE '%.update'
        
    Example Actions:
        - Authentication: "user.login", "user.logout", "user.password_reset"
        - Orders: "order.created", "order.cancelled", "order.refunded"
        - Products: "product.created", "product.updated", "product.deleted"
        - Admin: "admin.user_impersonation", "admin.price_override"
        
    Failure Modes:
        - High volume: Partition by created_at (monthly/yearly tables)
        - Storage cost: Archive old logs to cold storage (S3 Glacier)
        - Query performance: Use created_at + actor_id composite indexes
        
    Security:
        - Never expose raw logs to end users (sensitive data)
        - Encrypt item_metadata if contains PII
        - Monitor for suspicious patterns (mass deletions, privilege escalations)
        - Alert on admin actions outside business hours
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actor_id = Column(Integer, nullable=True, index=True)
    actor_type = Column(String(50), nullable=False)
    actor_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    target_type = Column(String(50), nullable=False, index=True)
    target_id = Column(String(100), nullable=False, index=True)
    item_metadata = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        CheckConstraint("actor_type IN ('user', 'api_key', 'system', 'admin')", name='check_actor_type_valid'),
        CheckConstraint("length(trim(action)) > 0", name='check_action_present'),
        CheckConstraint("length(trim(target_type)) > 0", name='check_target_type_present'),
        CheckConstraint("length(trim(target_id)) > 0", name='check_target_id_present'),
        CheckConstraint("length(ip_address) <= 45", name='check_ip_length'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor_id={self.actor_id}, target={self.target_type}:{self.target_id})>"
