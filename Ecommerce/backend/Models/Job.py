from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum, CheckConstraint
from sqlalchemy.sql import func
from database import Base
import enum


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    """
    SQLAlchemy ORM model for jobs table.
    
    Durable background job queue for asynchronous task processing. Supports
    retries, idempotency, worker coordination, and failure tracking. Used for
    long-running operations that shouldn't block HTTP requests.
    
    Database Schema:
        - Primary Key: id (auto-increment)
        - Indexes: id (primary), job_type, idempotency_key (unique), status,
                   created_at, retry_at
        
    Data Integrity:
        - Job type cannot be empty
        - Attempts must be non-negative
        - Max attempts must be positive
        - Attempts cannot exceed max_attempts
        - Timestamp ordering: created_at <= started_at <= completed_at/failed_at
        - Retry timestamp must be after creation
        
    Job Lifecycle:
        1. QUEUED: Job created, waiting for worker
        2. RUNNING: Worker processing job
        3. COMPLETED: Job finished successfully
        4. FAILED: All retry attempts exhausted
        5. CANCELLED: Manually cancelled by admin
        
    Job Types (Examples):
        - email.send: Transactional emails (order confirmation, shipping)
        - shipment.label_generate: Create shipping labels via carrier API
        - feed.import_products: Bulk product import from CSV
        - order.payment_capture: Delayed payment capture
        - inventory.reconciliation: Stock count reconciliation
        - report.generate: Complex report generation
        - image.resize: Batch image processing
        
    Retry Strategy:
        - attempts: Current attempt count (0 = first attempt)
        - max_attempts: Retry limit (default 3)
        - retry_at: Scheduled retry timestamp (exponential backoff)
        - Backoff formula: retry_at = now() + (2^attempts * 60 seconds)
        - Examples: 1 min, 2 min, 4 min, 8 min...
        
    Idempotency:
        - idempotency_key: Unique identifier to prevent duplicate execution
        - Example: "shipment_label_{order_id}_{timestamp}"
        - Worker checks: If job with same key exists and COMPLETED, skip
        - Protects against: Network retries, duplicate webhooks, race conditions
        
    Worker Coordination:
        - worker_id: Identifies which worker claimed the job
        - Prevents: Multiple workers processing same job
        - Heartbeat: Worker updates started_at/last_activity periodically
        - Stale job detection: started_at > 30 min ago, status = RUNNING
        
    Payload & Result:
        - payload: JSON with job inputs (order_id, user_id, options, etc.)
        - result: JSON with job outputs (label_url, processed_count, etc.)
        - error: JSON with error details for failed jobs
        
    Design Notes:
        - Single-purpose: Each job type does one thing
        - Retryable: Jobs can be safely retried (idempotent)
        - Checkpointing: Long jobs save progress to payload/result
        - Observability: Timestamps enable performance monitoring
        
    Worker Pattern:
        1. SELECT * WHERE status = QUEUED AND (retry_at IS NULL OR retry_at <= NOW())
           ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED
        2. UPDATE status = RUNNING, worker_id = self, started_at = NOW()
        3. Execute job logic
        4. On success: UPDATE status = COMPLETED, completed_at = NOW(), result = ...
        5. On failure: INCREMENT attempts, UPDATE status = QUEUED/FAILED, retry_at = ...
        
    Monitoring:
        - Queue depth: COUNT(*) WHERE status = QUEUED
        - Processing time: AVG(completed_at - started_at) GROUP BY job_type
        - Failure rate: COUNT(*) WHERE status = FAILED / COUNT(*)
        - Stale jobs: SELECT * WHERE status = RUNNING AND started_at < NOW() - INTERVAL 30 MINUTE
        
    Failure Handling:
        - Transient errors: Retry (network timeouts, rate limits)
        - Permanent errors: Mark FAILED (invalid data, missing resources)
        - Dead letter queue: Move FAILED jobs to separate table for investigation
        - Alerting: Slack/PagerDuty for critical job failures
        
    Scaling:
        - Horizontal: Run multiple worker processes/containers
        - Sharding: Partition by job_type (dedicated workers per type)
        - Priority: Add priority column for urgent jobs
        - Rate limiting: Throttle jobs per type (respect API limits)
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_type = Column(String(100), nullable=False, index=True)
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True)
    worker_id = Column(String(100), nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    error = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    retry_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    __table_args__ = (
        CheckConstraint("length(trim(job_type)) > 0", name='check_job_type_present'),
        CheckConstraint("attempts >= 0", name='check_attempts_non_negative'),
        CheckConstraint("max_attempts > 0", name='check_max_attempts_positive'),
        CheckConstraint("attempts <= max_attempts", name='check_attempts_within_max'),
        CheckConstraint("started_at IS NULL OR started_at >= created_at", name='check_started_after_created'),
        CheckConstraint("completed_at IS NULL OR (started_at IS NOT NULL AND completed_at >= started_at)", name='check_completed_after_started'),
        CheckConstraint("failed_at IS NULL OR (started_at IS NOT NULL AND failed_at >= started_at)", name='check_failed_after_started'),
        CheckConstraint("retry_at IS NULL OR retry_at >= created_at", name='check_retry_after_created'),
    )
    
    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status}, attempts={self.attempts})>"
