from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class AuditLog(Base):
    """
    Append-only security and operational trail for auditing, compliance, and debugging.
    Captures who did what, when, and to which resource.
    
    CRITICAL: Never delete or modify audit logs. They're immutable for compliance.
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
