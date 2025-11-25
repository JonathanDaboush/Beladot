from typing import Any, Optional
from datetime import datetime, timezone, timedelta

class Job:
    def __init__(self, id, job_type, idempotency_key, payload, result, status, worker_id, attempts, max_attempts, error, created_at, started_at, completed_at, failed_at, retry_at):
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
        self.status = "running"
        self.worker_id = worker_id
        self.started_at = datetime.now(timezone.utc)
        self.attempts += 1
        
        if repository:
            repository.update(self)
    
    def complete(self, result: dict, repository=None) -> None:
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)
    
    def fail(self, error: dict, retry: bool = False, repository=None) -> None:
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