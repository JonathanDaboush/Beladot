from typing import Any, Optional
from datetime import datetime, timezone, timedelta

class Job:
    """
    Domain model representing an asynchronous background job with retry logic and state tracking.
    
    This class manages background task execution, supporting job queuing, retry with exponential
    backoff, idempotency, failure tracking, and multi-worker coordination. It's the core of the
    async job processing system.
    
    Key Responsibilities:
        - Store job configuration (type, payload)
        - Track job lifecycle (queued, running, completed, failed)
        - Manage retry logic with exponential backoff
        - Ensure idempotency via idempotency_key
        - Coordinate multi-worker execution
        - Capture results and errors
    
    Job States:
        - queued: Waiting for worker to pick up
        - running: Currently being processed by a worker
        - completed: Successfully finished
        - failed: Permanently failed (max attempts exhausted)
    
    Retry Mechanism:
        - Exponential backoff: 2^attempts minutes (capped at 60 min)
        - Max attempts configurable per job
        - Failed jobs return to 'queued' if retries remain
        - retry_at timestamp controls when job becomes available
    
    Design Patterns:
        - State Machine: Explicit state transitions
        - Idempotency: Duplicate jobs detected by idempotency_key
        - Worker Coordination: worker_id tracks job ownership
    
    Design Notes:
        - payload stores job-specific data as dictionary
        - result stores job output for retrieval
        - error stores failure information
        - This is a domain object; persistence handled by JobRepository
    """
    def __init__(self, id, job_type, idempotency_key, payload, result, status, worker_id, attempts, max_attempts, error, created_at, started_at, completed_at, failed_at, retry_at):
        """
        Initialize a Job domain object.
        
        Args:
            id: Unique identifier (None for new jobs before persistence)
            job_type: Type of job (e.g., 'send_email', 'generate_report', 'process_order')
            idempotency_key: Unique key to prevent duplicate job creation
            payload: Job-specific data dictionary
            result: Job output dictionary (populated after completion)
            status: Job state ('queued', 'running', 'completed', 'failed')
            worker_id: ID of worker processing the job
            attempts: Number of execution attempts so far
            max_attempts: Maximum retry attempts before permanent failure
            error: Error information dictionary (populated on failure)
            created_at: Job creation timestamp
            started_at: When job execution began (most recent attempt)
            completed_at: When job completed successfully
            failed_at: When job permanently failed
            retry_at: When job should be retried (for exponential backoff)
        """
        self.id = id
        self.job_type = job_type
        self.idempotency_key = idempotency_key
        self.payload = payload
        self.result = result
        self.status = status
        self.worker_id = worker_id
        self.attempts = attempts
        self.max_attempts = max_attempts
        self.error = error
        self.created_at = created_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.failed_at = failed_at
        self.retry_at = retry_at
    
    def enqueue(self, repository=None, queue_service=None) -> None:
        """
        Enqueue the job for processing by a worker.
        
        Args:
            repository: Repository for persisting job (optional)
            queue_service: External queue service (Redis, RabbitMQ, etc.) (optional)
            
        Side Effects:
            - Sets status to 'queued' if not already
            - Persists job via repository (creates if new, updates if existing)
            - Assigns job.id from repository after creation
            - Publishes job to external queue service if provided
            
        Design Notes:
            - Idempotent (safe to call multiple times)
            - Queue service errors silently ignored (job in DB is sufficient)
            - Repository is source of truth; queue is notification mechanism
        """
        if self.status != "queued":
            self.status = "queued"
        
        if repository:
            if self.id:
                repository.update(self)
            else:
                saved_job = repository.create(self)
                self.id = saved_job.id
        
        if queue_service:
            try:
                queue_service.enqueue_job({
                    "job_id": self.id,
                    "job_type": self.job_type,
                    "payload": self.payload,
                    "idempotency_key": self.idempotency_key
                })
            except Exception as e:
                pass
    
    def start(self, worker_id: str, repository=None) -> None:
        """
        Mark job as started by a worker.
        
        Args:
            worker_id: Identifier of the worker processing this job
            repository: Repository for persisting state change (optional)
            
        Side Effects:
            - Sets status to 'running'
            - Sets worker_id for tracking
            - Sets started_at to current time
            - Increments attempts counter
            - Persists job via repository
            
        Design Notes:
            - Should be called when worker picks up job
            - Enables detection of stuck jobs (started but not completed)
        """
        self.status = "running"
        self.worker_id = worker_id
        self.started_at = datetime.now(timezone.utc)
        self.attempts += 1
        
        if repository:
            repository.update(self)
    
    def complete(self, result: dict, repository=None) -> None:
        """
        Mark job as successfully completed.
        
        Args:
            result: Job output data dictionary
            repository: Repository for persisting completion (optional)
            
        Side Effects:
            - Sets status to 'completed'
            - Stores result dictionary
            - Sets completed_at to current time
            - Persists job via repository
        """
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)
    
    def fail(self, error: dict, retry: bool = False, repository=None) -> None:
        """
        Mark job as failed with optional retry.
        
        Args:
            error: Error information dictionary (e.g., {'message': 'Connection timeout'})
            retry: Whether to retry job if attempts remain (default False)
            repository: Repository for persisting failure (optional)
            
        Side Effects:
            - Stores error dictionary
            - Sets failed_at to current time
            - If retry=True and attempts < max_attempts:
                - Sets status to 'queued' for retry
                - Calculates retry_at with exponential backoff
            - Otherwise:
                - Sets status to 'failed' (permanent)
            - Persists job via repository
            
        Exponential Backoff:
            - Delay = 2^attempts minutes (capped at 60 minutes)
            - Examples: 1st retry=2min, 2nd=4min, 3rd=8min, etc.
            
        Design Notes:
            - Caller chooses whether to retry (some errors shouldn't retry)
            - Backoff prevents hammering failing external services
        """
        self.error = error
        self.failed_at = datetime.now(timezone.utc)
        
        if retry and self.attempts < self.max_attempts:
            self.status = "queued"
            backoff_minutes = min(2 ** self.attempts, 60)
            self.retry_at = datetime.now(timezone.utc) + timedelta(minutes=backoff_minutes)
        else:
            self.status = "failed"
        
        if repository:
            repository.update(self)