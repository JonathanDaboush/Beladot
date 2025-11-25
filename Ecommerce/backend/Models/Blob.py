from sqlalchemy import Column, Integer, String, DateTime, BigInteger, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class Blob(Base):
    """
    Provider-agnostic pointer to binary assets (images, shipping labels, documents).
    Stores storage keys and metadata (checksum) for file integrity.
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
