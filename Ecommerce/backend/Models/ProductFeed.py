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
    SQLAlchemy ORM model for product_feeds table.
    
    Manages bulk product catalog import/export operations from files (CSV, Excel, JSON).
    Tracks processing progress, row-level errors, and integrates with Job queue for
    asynchronous processing.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Foreign Keys: blob_id -> blobs.id (SET NULL), job_id -> jobs.id (SET NULL),
                       created_by_user_id -> users.id (SET NULL)
        - Indexes: id (primary), feed_type, status, job_id, created_at
        
    Data Integrity:
        - Filename cannot be empty
        - Feed type: import or export
        - Format: csv, xlsx, json, or xml
        - Row counts must be non-negative
        - Processed rows cannot exceed total rows
        - Success + error rows must equal processed rows
        - Timestamp ordering: created_at <= started_at <= completed_at
        
    Relationships:
        - Many-to-one with Blob (feed file storage)
        - Many-to-one with Job (async processing job)
        - Many-to-one with User (creator for audit trail)
        
    Feed Types:
        - import: Upload products to catalog (create/update)
        - export: Download products from catalog (reporting, backup)
        
    File Formats:
        - csv: Comma-separated values (most common)
        - xlsx: Excel spreadsheet (includes formatting)
        - json: JSON array of product objects
        - xml: XML product feed (for integrations)
        
    Feed Status Lifecycle:
        1. PENDING: File uploaded, awaiting processing
        2. PROCESSING: Job running, rows being processed
        3. COMPLETED: All rows processed successfully
        4. FAILED: Processing failed (file parse error, system error)
        5. PARTIALLY_COMPLETED: Some rows succeeded, some failed
        
    Row Tracking:
        - total_rows: Total rows in file (excluding header)
        - processed_rows: Rows attempted so far
        - success_rows: Rows successfully imported/exported
        - error_rows: Rows that failed validation or processing
        - Progress: (processed_rows / total_rows) * 100%
        
    Error Reporting:
        - errors: JSON array of error objects
        - Example: [{"row": 5, "sku": "ABC123", "error": "Invalid price", "field": "price"}]
        - Enables: Admin review and correction of failed rows
        - Downloadable: Generate error report CSV for re-upload
        
    Import Workflow:
        1. Admin uploads file (CSV/Excel)
        2. Create Blob record with file
        3. Create ProductFeed with status=PENDING
        4. Create Job for async processing
        5. Worker picks up Job:
           a. Parse file (pandas, csv module)
           b. Validate each row (schema, business rules)
           c. For each valid row: Create/update Product
           d. Track success/error counts
           e. Save errors JSON for failed rows
        6. Update ProductFeed: status=COMPLETED/PARTIALLY_COMPLETED/FAILED
        
    Idempotent Import:
        - Match by SKU: If product with SKU exists, update; else create
        - External ID: Use external_id field for supplier integration
        - Duplicate detection: Skip/update duplicates within same file
        
    Validation Rules:
        - Required fields: SKU, name, price
        - Price validation: Must be numeric, positive
        - Category: Must exist in categories table
        - Stock: Must be non-negative integer
        - Images: Validate URLs or uploaded files
        
    Export Workflow:
        1. Admin requests product export (filters, date range)
        2. Create ProductFeed with feed_type=export, status=PENDING
        3. Create Job for async generation
        4. Worker generates file:
           a. Query products with filters
           b. Serialize to CSV/Excel/JSON
           c. Upload to Blob storage
           d. Link blob_id to ProductFeed
        5. Update status=COMPLETED
        6. Admin downloads file via blob_id
        
    Batch Processing:
        - Process in chunks (100-1000 rows per batch)
        - Commit after each batch (partial progress saved)
        - Transaction rollback: Only failed batch, not entire import
        - Memory efficient: Stream large files, don't load all at once
        
    Performance:
        - Bulk insert: Use SQLAlchemy bulk_insert_mappings()
        - Database: Disable triggers/indexes during large imports
        - Caching: Preload categories, suppliers for faster lookups
        - Parallel: Process multiple feeds concurrently (separate workers)
        
    Monitoring:
        - Processing time: completed_at - started_at
        - Throughput: success_rows / (processing_time_seconds)
        - Error rate: error_rows / total_rows
        - Feed history: Track imports over time
        
    Failure Recovery:
        - Partial import: Resume from processed_rows (checkpointing)
        - Retry failed rows: Generate CSV of errors, fix, re-import
        - Full rollback: Delete all products from feed_id (optional)
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
