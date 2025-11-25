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
    Durable descriptor for background work: email sends, shipping label generation,
    feed processing, reconciliation, etc.
    
    Design principles:
    - Jobs are single-purpose and retryable
    - Use idempotency_key to prevent duplicate execution
    - Support exponential backoff for retries
    - Long-running jobs should implement checkpointing
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
