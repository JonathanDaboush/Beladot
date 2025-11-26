from typing import Any

class Blob:
    def __init__(self, id, storage_key, filename, content_type, size_bytes, checksum, storage_provider, created_at):
        self.id = id
        self.storage_key = storage_key
        self.filename = filename
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.storage_provider = storage_provider
        self.created_at = created_at
    
    def get_url(self) -> str:
        return f"/api/blobs/{self.id}/download"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "url": self.get_url(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }