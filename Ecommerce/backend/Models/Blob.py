from sqlalchemy import Column, Integer, String, DateTime, BigInteger, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class Blob(Base):
    """
    SQLAlchemy ORM model for blobs table.
    
    Provider-agnostic pointer to binary assets stored in external storage systems.
    Supports images, shipping labels, documents, and any file type with integrity
    verification via SHA-256 checksums.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Indexes: id (primary), storage_key (unique)
        
    Data Integrity:
        - Storage key must be unique and non-empty
        - Filename and content type required
        - Size must be positive (bytes)
        - Checksum exactly 64 characters (SHA-256 hex)
        - Storage provider must be: s3, gcs, azure, local, or cloudinary
        
    Storage Providers:
        - s3: Amazon S3 (default)
        - gcs: Google Cloud Storage
        - azure: Azure Blob Storage
        - local: Local filesystem (dev/testing only)
        - cloudinary: Cloudinary CDN (images/media)
        
    Design Notes:
        - storage_key: Provider-specific identifier (S3 key, GCS object name, etc.)
        - filename: Original filename from upload
        - content_type: MIME type (image/jpeg, application/pdf, etc.)
        - size_bytes: File size for quota management and billing
        - checksum: SHA-256 hash for integrity verification
        - storage_provider: Enables multi-cloud strategy and migration
        
    File Integrity:
        - Checksum calculated on upload
        - Verified on download/access
        - Detects corruption, tampering, incomplete transfers
        - Example: SHA-256(file_bytes).hexdigest() -> 64-char hex string
        
    Use Cases:
        - ProductImage: Product gallery photos
        - Shipment: Shipping labels (PDF)
        - ProductFeed: Import/export files (CSV, Excel)
        - User: Profile avatars
        - Return: Photo evidence of damaged items
        - Invoice: PDF invoices and receipts
        
    Lifecycle:
        1. Upload: Client uploads file
        2. Store: Save to provider (S3, etc.)
        3. Record: Create Blob with storage_key, checksum
        4. Reference: Link from ProductImage, Shipment, etc.
        5. Access: Retrieve via storage_key, verify checksum
        6. Delete: Remove blob (check for references first)
        
    Storage Key Examples:
        - S3: "products/images/2024/11/abc123.jpg"
        - GCS: "gs://bucket/path/to/file.pdf"
        - Cloudinary: "cloudinary://abc123/image.jpg"
        - Local: "/var/uploads/files/xyz789.png"
        
    Optimization:
        - CDN: Use CloudFront/Cloudflare for S3 blobs
        - Lazy loading: Generate signed URLs on-demand
        - Compression: Store compressed images (WebP, AVIF)
        - Deduplication: Check checksum before upload
        
    Failure Modes:
        - Orphaned blobs: No references (cleanup via periodic job)
        - Missing files: Blob record exists but file deleted from storage
        - Checksum mismatch: File corrupted (alert and re-upload)
        - Provider outage: Retry logic with exponential backoff
        
    Security:
        - Signed URLs for private content (expiring access)
        - Virus scanning on upload (ClamAV integration)
        - Content-Type validation (prevent malicious uploads)
        - Size limits enforced (prevent DoS via large files)
    """
    __tablename__ = "blobs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    storage_key = Column(String(500), nullable=False, unique=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    checksum = Column(String(64), nullable=False)
    storage_provider = Column(String(50), default="s3", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint("length(trim(storage_key)) > 0", name='check_storage_key_present'),
        CheckConstraint("length(trim(filename)) > 0", name='check_filename_present'),
        CheckConstraint("length(trim(content_type)) > 0", name='check_content_type_present'),
        CheckConstraint("size_bytes > 0", name='check_size_positive'),
        CheckConstraint("length(checksum) = 64", name='check_checksum_sha256'),
        CheckConstraint("storage_provider IN ('s3', 'gcs', 'azure', 'local', 'cloudinary')", name='check_storage_provider_valid'),
    )
    
    def __repr__(self):
        return f"<Blob(id={self.id}, filename={self.filename}, size={self.size_bytes})>"
