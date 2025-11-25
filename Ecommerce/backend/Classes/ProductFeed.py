from datetime import datetime, timezone
from typing import Optional

class ProductFeed:
    def __init__(self, id, blob_id, filename, feed_type, format, status, total_rows, processed_rows, success_rows, error_rows, errors, job_id, created_by_user_id, created_at, started_at, completed_at):
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