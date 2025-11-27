from typing import Any

class Blob:
    """
    Domain model representing a file stored in external storage (S3, Azure, etc.).
    
    This class manages metadata for uploaded files, providing a reference to files
    stored in external blob storage systems. It supports multiple storage providers
    and includes integrity checking via checksums.
    
    Key Responsibilities:
        - Store file metadata (name, type, size, checksum)
        - Reference external storage location (storage_key)
        - Track storage provider for multi-cloud scenarios
        - Generate download URLs for file access
        - Support file integrity verification
    
    Storage Strategy:
        - Actual file bytes stored externally (S3, Azure Blob, etc.)
        - Database stores only metadata and reference key
        - Separates concerns: blob storage for files, DB for metadata
        - Enables CDN integration and scalable storage
    
    Design Notes:
        - storage_key is provider-specific identifier (e.g., S3 object key)
        - checksum enables integrity verification (detect corruption)
        - storage_provider allows multi-cloud or migration scenarios
        - This is a domain object; persistence handled by BlobRepository
    """
    def __init__(self, id, storage_key, filename, content_type, size_bytes, checksum, storage_provider, created_at):
        """
        Initialize a Blob domain object.
        
        Args:
            id: Unique identifier (None for new blobs before persistence)
            storage_key: Provider-specific storage identifier (e.g., S3 object key)
            filename: Original filename from upload
            content_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            size_bytes: File size in bytes
            checksum: File hash for integrity verification (e.g., MD5, SHA256)
            storage_provider: Storage system identifier (e.g., 's3', 'azure', 'local')
            created_at: Upload timestamp
        """
        self.id = id
        self.storage_key = storage_key
        self.filename = filename
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.storage_provider = storage_provider
        self.created_at = created_at
    
    def get_url(self) -> str:
        """
        Generate the download URL for this blob.
        
        Returns:
            str: Relative API endpoint for downloading the file
            
        Design Notes:
            - Currently returns relative URL (requires API gateway)
            - Could be extended to generate signed URLs from storage provider
            - For production, consider pre-signed URLs with expiration
        """
        return f"/api/blobs/{self.id}/download"
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert blob metadata to dictionary for API responses.
        
        Returns:
            dict: Blob metadata with id, filename, content_type, size_bytes,
                  url, and created_at
                  
        Design Notes:
            - Excludes internal fields (storage_key, checksum, provider)
            - Includes URL for convenient client access
            - Suitable for public API responses
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "url": self.get_url(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }