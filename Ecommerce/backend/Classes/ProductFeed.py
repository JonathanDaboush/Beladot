from datetime import datetime, timezone
from typing import Optional

class ProductFeed:
    """
    Domain model representing a bulk product import/update feed with processing tracking.
    
    This class manages asynchronous processing of product data files (CSV, XML, JSON)
    for bulk catalog operations. It tracks processing progress, errors, and links to
    the uploaded file and processing job.
    
    Key Responsibilities:
        - Store feed metadata (filename, type, format)
        - Track processing state and progress (rows processed, succeeded, failed)
        - Initiate async job for feed processing
        - Accumulate errors for user feedback
        - Link to uploaded file (blob) and processing job
    
    Feed Types:
        - import: Create new products
        - update: Update existing products
        - inventory_sync: Update stock quantities
    
    Supported Formats:
        - csv: Comma-separated values
        - xml: XML feed (Google Shopping, etc.)
        - json: JSON array of products
    
    Processing States:
        - pending: Feed uploaded, awaiting processing
        - processing: Job actively processing feed
        - completed: All rows processed successfully
        - partial_success: Some rows failed
        - failed: Processing job failed
    
    Design Notes:
        - Processing handled by async Job (enables long-running imports)
        - Errors stored as list for detailed feedback
        - Progress tracked for UI updates
        - This is a domain object; persistence handled by ProductFeedRepository
    """
    def __init__(self, id, blob_id, filename, feed_type, format, status, total_rows, processed_rows, success_rows, error_rows, errors, job_id, created_by_user_id, created_at, started_at, completed_at):
        """
        Initialize a ProductFeed domain object.
        
        Args:
            id: Unique identifier (None for new feeds before persistence)
            blob_id: Foreign key to uploaded file blob
            filename: Original filename
            feed_type: Type of feed ('import', 'update', 'inventory_sync')
            format: File format ('csv', 'xml', 'json')
            status: Processing status (pending, processing, completed, failed)
            total_rows: Total number of rows in feed
            processed_rows: Number of rows processed so far
            success_rows: Number of successfully processed rows
            error_rows: Number of rows with errors
            errors: List of error dictionaries for failed rows
            job_id: Foreign key to async processing job
            created_by_user_id: User who uploaded the feed
            created_at: Feed creation timestamp
            started_at: When processing began
            completed_at: When processing finished
        """
        self.id = id
        self.blob_id = blob_id
        self.filename = filename
        self.feed_type = feed_type
        self.format = format
        self.status = status
        self.total_rows = total_rows
        self.processed_rows = processed_rows
        self.success_rows = success_rows
        self.error_rows = error_rows
        self.errors = errors
        self.job_id = job_id
        self.created_by_user_id = created_by_user_id
        self.created_at = created_at
        self.started_at = started_at
        self.completed_at = completed_at
    
    def start(self, repository=None, job_service=None) -> Optional['Job']:
        """
        Create and enqueue a job to process this feed asynchronously.
        
        Args:
            repository: Repository for creating job and updating feed (optional)
            job_service: Service for enqueueing job (optional)
            
        Returns:
            Job: Created job object, or None if feed not in pending status
            
        Side Effects:
            - Creates Job record with feed payload
            - Sets self.job_id to created job ID
            - Changes status to 'processing'
            - Sets started_at to current time
            - Persists feed via repository
            - Enqueues job via job_service
            
        Design Notes:
            - Only starts feeds in 'pending' status (guards against duplicate processing)
            - Job configured with 3 max attempts and exponential backoff
            - Idempotency key includes timestamp to allow reprocessing
        """
        if self.status != "pending":
            return None
        
        from Classes.Job import Job
        job = Job(
            id=None,
            job_type="product_feed_processing",
            idempotency_key=f"feed_{self.id}_{datetime.now().timestamp()}",
            payload={
                "feed_id": self.id,
                "blob_id": self.blob_id,
                "feed_type": self.feed_type,
                "format": self.format
            },
            result=None,
            status="queued",
            worker_id=None,
            attempts=0,
            max_attempts=3,
            error=None,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            completed_at=None,
            failed_at=None,
            retry_at=None
        )
        
        if repository:
            job = repository.create_job(job)
            self.job_id = job.id
            self.status = "processing"
            self.started_at = datetime.now(timezone.utc)
            repository.update(self)
        
        if job_service:
            job_service.enqueue(job)
        
        return job