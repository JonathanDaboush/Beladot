# Represents a background task that runs separately from the main application
# Used for long-running operations like bulk imports, email sending, or report generation
# Prevents duplicate work through idempotency keys and supports automatic retries on failure
class Job:
    def __init__(self, id, job_type, idempotency_key, payload, result, status, worker_id, attempts, max_attempts, error, created_at, started_at, completed_at, failed_at, retry_at):
        self.id = id
        self.job_type = job_type #type of job, e.g., "product_feed_processing"
        self.idempotency_key = idempotency_key #to prevent duplicate jobs ,be sure to hash to check request.
        self.payload = payload #input data for the job
        self.result = result #output data from the job
        self.status = status #"pending", "in_progress", "completed", "failed"
        self.worker_id = worker_id #which worker is processing this job
        self.attempts = attempts #number of attempts made
        self.max_attempts = max_attempts #maximum allowed attempts
        self.error = error #error message if failed
        self.created_at = created_at #when job was created
        self.started_at = started_at #when job processing started
        self.completed_at = completed_at #when job processing completed
        self.failed_at = failed_at #when job processing failed
        self.retry_at = retry_at #when job should be retried if failed