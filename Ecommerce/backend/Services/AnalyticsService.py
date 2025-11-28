from typing import Any
from uuid import UUID
from datetime import date

from Ecommerce.backend.Classes import AuditLog, User as user, Session as session
from datetime import datetime, timezone, timedelta
from Ecommerce.backend.Repositories import AuditLogRepository , OrderRepository
from Ecommerce.backend.Classes import Order as order
class AnalyticsService:
    """
    Event Tracking and Analytics Service
    Event ingestion and light aggregation for conversion funnels, A/B testing,
    and feature telemetry. Accepts high volumes of events from front-end and backend,
    tags them for user/session context, and provides near-real-time aggregates for dashboards.
    Analytics must be decoupled from checkout latency paths and should use sampling or batching.
    """
    
    def __init__(self):
        pass
    
    def track_event(self, user_id: UUID | None, session_id: str | None, event: str, properties: dict) -> None:
        """
        Enqueue or write event into analytics store; include timestamps and context.
        Ensure privacy controls for PII.
        """
        
        user=user.UserRepository.get_by_id(user_id) if user_id else None
        session=session.SessionRepository.get_by_id(session_id) if session_id else None
        
        #security measure to check ids are identitcal
        if user and session and user.id != session.user_id:
            raise ValueError("User ID does not match Session's User ID")
        
        auditlog=AuditLog(
            id=None,
            actor_id=user.id if user else None,
            actor_type='user' if user else 'guest',
            actor_email=user.email if user else None,
            action=event,
            target_type='analytics_event',
            target_id=None,
            item_metadata=properties,
            ip_address=session.ip_address if session else None,
            user_agent=session.user_agent if session else None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditlog)
        
    
    def get_conversion_rate(self,user_id: UUID, start: date, end: date) -> float:
        """
        Compute and return conversion rate (purchases/sessions) for given window;
        used in dashboards.
        """
        orders = OrderRepository.get_orders_in_date_range(user_id, start, end)
        completed_statuses = {'delivered', 'shipped', 'paid'}
        pending_statuses = {'pending', 'processing'}
        completedOrders = [i for i in orders if i.status in completed_statuses]
        pendingOrders = [i for i in orders if i.status in pending_statuses]
        return pendingOrders, completedOrders