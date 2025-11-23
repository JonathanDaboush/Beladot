# Represents a file stored in cloud storage (images, PDFs, documents, etc.).
# Tracks metadata about uploaded files - actual file data lives in external storage like S3, Azure Blob, or local filesystem.
class Blob:
    def __init__(self, id, storage_key, filename, content_type, size_bytes, checksum, storage_provider, created_at):
        self.id = id  # Unique blob record identifier in database
        self.storage_key = storage_key  # Unique path/key where file is stored in cloud (e.g., "products/2024/image-abc123.jpg")
        self.filename = filename  # Original filename when uploaded (e.g., "tshirt-front.jpg")
        self.content_type = content_type  # MIME type of file (e.g., "image/jpeg", "application/pdf") for proper browser handling
        self.size_bytes = size_bytes  # File size in bytes (for storage tracking and upload limits)
        self.checksum = checksum  # Hash of file contents (MD5/SHA256) to verify integrity and detect duplicates
        self.storage_provider = storage_provider  # Where file is stored: "s3", "azure", "local", "cloudinary"
        self.created_at = created_at  # When file was uploaded
