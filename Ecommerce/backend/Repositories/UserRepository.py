from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.User import User


class UserRepository:
    """
    Data access layer for User entities.
    
    This repository provides async database operations for User records using SQLAlchemy.
    All methods are async to support non-blocking database I/O in async web frameworks.
    
    Responsibilities:
        - CRUD operations for User entities
        - Query methods for common user lookups (by ID, email, reset token)
        - Database session management
        - Translating between domain objects and ORM models
    
    Design Patterns:
        - Repository Pattern: Isolates data access logic from business logic
        - Async/Await: All methods are async for scalability
        - Session Injection: Database session injected via constructor for flexibility
        
    Usage:
        repository = UserRepository(db_session)
        user = await repository.get_by_email("user@example.com")
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
            
        Note:
            The session should be managed by the caller (typically via dependency injection).
            Repository does not create or close sessions.
        """
        self.db = db
        self.model = User
    
    async def get_by_id(self, user_id: int) -> User:
        """
        Retrieve a user by their unique identifier.
        
        Args:
            user_id: The unique ID of the user to retrieve
            
        Returns:
            User: The user object if found, None otherwise
            
        Database:
            Executes: SELECT * FROM users WHERE id = ?
            Index: Uses primary key index for O(1) lookup
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email address.
        
        Args:
            email: The email address to search for (case-insensitive)
            
        Returns:
            User: The user object if found, None otherwise
            
        Database:
            Executes: SELECT * FROM users WHERE email = ?
            Index: Uses unique index on email column for fast lookup
            
        Note:
            Email should be lowercase as per data constraints.
            The database enforces email uniqueness.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """
        Persist a new user to the database.
        
        Args:
            user: User object to create (id should be None)
            
        Returns:
            User: The created user with ID assigned by database
            
        Database Operations:
            1. Add user to session
            2. Commit transaction (assigns ID)
            3. Refresh object to load generated fields
            
        Side Effects:
            - Sets user.id to database-generated value
            - Sets user.created_at and updated_at via database defaults
            - Commits transaction immediately
            
        Errors:
            Raises SQLAlchemy exception if:
            - Email already exists (unique constraint violation)
            - Validation constraints fail
            - Database connection issues
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User):
        """
        Update an existing user in the database.
        
        Args:
            user: User object with modifications to persist
            
        Database Operations:
            1. Merge user state into session (handles detached objects)
            2. Commit transaction
            3. Refresh object to load any database-generated values
            
        Side Effects:
            - Updates user.updated_at via database trigger
            - Commits transaction immediately
            
        Design:
            Uses merge() instead of update() to handle both attached and
            detached objects gracefully. This is safer when objects are passed
            between service layers.
            
        Note:
            Assumes the user.id exists and matches a database record.
            Does not create new records - use create() for that.
        """
