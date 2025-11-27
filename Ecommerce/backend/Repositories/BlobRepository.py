from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Blob import Blob


class BlobRepository:
    """
    Data access layer for Blob entities (file storage metadata).
    
    This repository manages file metadata and handles file upload processing,
    including checksum calculation for integrity verification.
    
    Responsibilities:
        - Blob metadata CRUD operations
        - Calculate file checksums (SHA-256)
        - Track storage provider details
    
    Design Patterns:
        - Repository Pattern: Isolates blob metadata access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = BlobRepository(db_session)
        blob = await repository.create_blob(file_data, 'image.jpg', 'image/jpeg')
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Blob
    
    async def create_blob(self, data: bytes, filename: str, content_type: str, **kwargs) -> Blob:
        """
        Create a new blob record with automatic checksum calculation.
        
        Args:
            data: File bytes
            filename: Original filename
            content_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            **kwargs: Additional fields (storage_key, storage_provider, created_at)
            
        Returns:
            Blob: Created blob metadata with database-generated ID
            
        Side Effects:
            - Calculates SHA-256 checksum of file data
            - Sets size_bytes from data length
            - Commits transaction immediately
            
        Note:
            This method stores metadata only. Actual file bytes must be
            stored separately in S3, Azure, or local filesystem.
        """
        """Create a new blob record"""
        import hashlib
        checksum = hashlib.sha256(data).hexdigest()
        
        blob = Blob(
            storage_key=kwargs.get('storage_key', filename),
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            checksum=checksum,
            storage_provider=kwargs.get('storage_provider', 'local'),
            created_at=kwargs.get('created_at')
        )
        self.db.add(blob)
        await self.db.commit()
        await self.db.refresh(blob)
        return blob
    
    async def get_by_id(self, blob_id: int) -> Blob:
        """
        Retrieve blob metadata by ID.
        
        Args:
            blob_id: The unique ID of the blob
            
        Returns:
            Blob: The blob metadata object if found, None otherwise
        """
        result = await self.db.execute(select(Blob).where(Blob.id == blob_id))
        return result.scalar_one_or_none()
