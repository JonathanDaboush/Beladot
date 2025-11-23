# Tracks bulk import/export of products from CSV/Excel files
# Monitors progress and errors when uploading hundreds or thousands of products at once
class ProductFeed:
    def __init__(self, id, blob_id, filename, feed_type, format, status, total_rows, processed_rows, success_rows, error_rows, errors, job_id, created_by_user_id, created_at, started_at, completed_at):
        self.id = id  # Unique identifier for this feed
        self.blob_id = blob_id  # Reference to the uploaded file in storage
        self.filename = filename  # Original name of the uploaded file (e.g., "products.csv")
        self.feed_type = feed_type  # Type of feed: "import" or "export"
        self.format = format  # File format: "csv", "json", "xml"
        self.status = status  # Processing status: "pending", "processing", "completed", "failed"
        self.total_rows = total_rows  # Total number of products in the file
        self.processed_rows = processed_rows  # How many products have been processed so far
        self.success_rows = success_rows  # How many products were successfully imported/exported
        self.error_rows = error_rows  # How many products failed to process
        self.errors = errors  # JSON list of error messages for failed rows
        self.job_id = job_id  # Reference to background job processing this feed
        self.created_by_user_id = created_by_user_id  # ID of user who uploaded this feed
        self.created_at = created_at  # When the feed was uploaded
        self.started_at = started_at  # When processing started
        self.completed_at = completed_at  # When processing finished
