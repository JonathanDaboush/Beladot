from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.APIKey import APIKey
from Models.AuditLog import AuditLog


class APIKeyRepository:
    """
    Data access layer for APIKey entities.
    
    This repository manages API key persistence and audit logging for
    programmatic API access with scope-based authorization.
    
    Responsibilities:
        - API key CRUD operations
        - Track key usage (last_used_at)
        - Audit log generation for API key operations
    
    Design Patterns:
        - Repository Pattern: Isolates API key data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = APIKeyRepository(db_session)
        await repository.update(api_key)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = APIKey
    
    async def update(self, api_key: APIKey):
        """
        Update API key status and usage tracking.
        
        Args:
            api_key: APIKey object with modifications
            
        Side Effects:
            - Updates last_used_at timestamp
            - Commits transaction immediately
            
        Common Updates:
            - Revocation (is_active = False)
            - Usage timestamp updates
            - Scope modifications
        """
        await self.db.merge(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
    
