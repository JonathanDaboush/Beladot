from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Session import Session


class SessionRepository:
    """
    Data access layer for Session entities (user login sessions).
    
    This repository manages user session persistence, tracking active login
    sessions with token-based authentication and expiration.
    
    Responsibilities:
        - Session CRUD operations
        - Track session lifecycle (active, expired)
        - Support token-based lookups
    
    Design Patterns:
        - Repository Pattern: Isolates session data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = SessionRepository(db_session)
        await repository.update(session)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Session
    
    async def create(self, session: Session) -> Session:
        """
        Create a new session.
        
        Args:
            session: Session object to create
            
        Returns:
            Created session with database ID
        """
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session
    
    async def update(self, session: Session):
        """
        Update session data (last activity, expiration).
        
        Args:
            session: Session object with modifications
            
        Side Effects:
            - Updates session timestamps
            - Commits transaction immediately
            
        Common Updates:
            - Activity timestamp refresh
            - Session extension/expiration
        """
        await self.db.merge(session)
        await self.db.commit()
        await self.db.refresh(session)
