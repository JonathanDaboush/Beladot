from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.AuditLog import AuditLog
from typing import List


class AuditLogRepository:
    """
    Data access layer for AuditLog entities.
    
    This repository manages immutable audit trail creation and queries,
    supporting compliance, security investigations, and debugging.
    
    Responsibilities:
        - Create audit log entries (immutable)
        - Query logs by target (what was changed)
        - Support chronological reconstruction
    
    Design Patterns:
        - Append-Only: Audit logs are never updated or deleted
        - Repository Pattern: Isolates audit data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = AuditLogRepository(db_session)
        log = await repository.create(log_data)
        history = await repository.get_by_target('order', order_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = AuditLog
    
    async def create(self, log_data: dict) -> AuditLog:
        """
        Create an immutable audit log entry.
        
        Args:
            log_data: Dictionary with fields (actor_id, action, target_type, target_id, metadata)
            
        Returns:
            AuditLog: Created audit log entry
            
        Side Effects:
            - Creates permanent audit record
            - Commits transaction immediately
            
        Immutability:
            Audit logs cannot be updated or deleted (compliance requirement)
        """
        audit_log = AuditLog(**log_data)
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log
    
    async def create_audit_log(self, log_data: dict) -> AuditLog:
        """
        Generic method to create an audit log entry.
        
        Args:
            log_data: Dictionary with fields (actor_id, action, target_type, target_id, metadata)
            
        Returns:
            AuditLog: Created audit log entry
            
        Side Effects:
            - Creates permanent audit record
            - Commits transaction immediately
            
        Immutability:
            Audit logs cannot be updated or deleted (compliance requirement)
        """
        return self.create(log_data)
    
    async def get_by_id(self, log_id: int) -> AuditLog:
        """
        Retrieve an audit log entry by its ID.
        
        Args:
            log_id: ID of the audit log entry
            
        Returns:
            AuditLog: The retrieved audit log entry or None if not found
        """
        result = await self.db.execute(select(self.model).where(self.model.id == log_id))
        return result.scalar_one_or_none()
    
    async def get_by_target(self, target_type: str, target_id: int, limit: int = 50) -> List[AuditLog]:
        """
        Retrieve audit trail for a specific target entity.
        
        Args:
            target_type: Type of entity ('user', 'order', 'product', etc.)
            target_id: ID of the target entity
            limit: Maximum number of logs to return (default 50)
            
        Returns:
            List[AuditLog]: Audit logs in reverse chronological order (newest first)
            
        Use Cases:
            - Display order history timeline
            - Security investigation (user activity)
            - Debugging state changes
        """
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.target_type == target_type)
            .where(AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
