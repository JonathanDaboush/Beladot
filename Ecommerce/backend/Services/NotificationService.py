from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Job as job, User as user
from Ecommerce.backend.Repositories import JobRepository as jobrepository
from Ecommerce.backend.Utilities.email import EmailService as emailservice

class NotificationService:
    """
    Messaging and Notification Service
    Asynchronous messaging backbone for emails, SMS, and outbound webhooks.
    Queues messages as Jobs, provides templating with safe context rendering,
    and ensures reliable delivery via retries and DLQs (dead-letter queues).
    Notifications must be idempotent and keep delivery logs for audit.
    """
    
    def __init__(self, job_repository, email_provider=None, sms_provider=None):
        self.job_repository = job_repository
        self.email_provider = email_provider
        self.sms_provider = sms_provider
    
    def enqueue_email(self, template: str, to: str, context: dict):
        """
        Create durable job to render and send email; do not perform immediate external calls.
        Return job handle for tracking. Ensure template rendering is safe (escape input)
        and that sensitive information is not included.
        """
        # Audit log
        from datetime import datetime, timezone
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        auditLog_entry = auditLog(
            id=None,
            actor_id=None,
            actor_type=None,
            actor_email=None,
            action='enqueue_email',
            target_type='email',
            target_id=to,
            item_metadata={
                'template': template,
                'to': to,
                'context': context
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
    
    def send_sms(self, number: str, message: str):
        """
        Queue an outbound SMS job; validate number format.
        """
        # Audit log
        from datetime import datetime, timezone
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        auditLog_entry = auditLog(
            id=None,
            actor_id=None,
            actor_type=None,
            actor_email=None,
            action='send_sms',
            target_type='sms',
            target_id=number,
            item_metadata={
                'number': number,
                'message': message
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
    
    def send_webhook(self, url: str, event: str, payload: dict):
        """
        Queue webhooks with signature and retry metadata;
        provide admin insight into failures.
        """
        # Audit log
        from datetime import datetime, timezone
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        auditLog_entry = auditLog(
            id=None,
            actor_id=None,
            actor_type=None,
            actor_email=None,
            action='send_webhook',
            target_type='webhook',
            target_id=url,
            item_metadata={
                'url': url,
                'event': event,
                'payload': payload
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
