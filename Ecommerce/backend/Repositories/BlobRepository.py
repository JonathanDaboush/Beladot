from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Blob import Blob


class BlobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Blob
    
    async def create_blob(self, data: bytes, filename: str, content_type: str, **kwargs) -> Blob:
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
        result = await self.db.execute(select(Blob).where(Blob.id == blob_id))
        return result.scalar_one_or_none()
