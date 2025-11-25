from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class FeedStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class ProductFeed(Base):
    """
    Bulk import/export facility for catalog data.
    Tracks the processing of CSV/Excel files containing product data.
    
    Design principles:
    - Validate input rows before processing
    - Support idempotent imports by SKU/external_id
    - Provide row-level error reporting for admin review
    - Run as asynchronous Jobs
    - Support transactional batches and rollback options
    """
    __tablename__ = "product_feeds"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    blob_id = Column(Integer, ForeignKey("blobs.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    feed_type = Column(String(50), nullable=False, index=True)
    format = Column(String(20), nullable=False)
    status = Column(SQLEnum(FeedStatus), default=FeedStatus.PENDING, nullable=False, index=True)
    total_rows = Column(Integer, default=0, nullable=False)
    processed_rows = Column(Integer, default=0, nullable=False)
    success_rows = Column(Integer, default=0, nullable=False)
    error_rows = Column(Integer, default=0, nullable=False)
    errors = Column(JSON, nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    blob = relationship("Blob")
    job = relationship("Job")
    created_by = relationship("User")
    
    __table_args__ = (
        CheckConstraint("length(trim(filename)) > 0", name='check_filename_present'),
        CheckConstraint("feed_type IN ('import', 'export')", name='check_feed_type_valid'),
        CheckConstraint("format IN ('csv', 'xlsx', 'json', 'xml')", name='check_format_valid'),
        CheckConstraint("total_rows >= 0", name='check_total_rows_non_negative'),
        CheckConstraint("processed_rows >= 0", name='check_processed_rows_non_negative'),
        CheckConstraint("success_rows >= 0", name='check_success_rows_non_negative'),
        CheckConstraint("error_rows >= 0", name='check_error_rows_non_negative'),
        CheckConstraint("processed_rows <= total_rows", name='check_processed_within_total'),
        CheckConstraint("success_rows + error_rows = processed_rows", name='check_success_plus_error_equals_processed'),
        CheckConstraint("started_at IS NULL OR started_at >= created_at", name='check_started_after_created'),
        CheckConstraint("completed_at IS NULL OR (started_at IS NOT NULL AND completed_at >= started_at)", name='check_completed_after_started'),
    )
    
    def __repr__(self):
        return f"<ProductFeed(id={self.id}, filename={self.filename}, status={self.status}, {self.success_rows}/{self.total_rows} success)>"
