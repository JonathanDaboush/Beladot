"""
domain_event.py

Defines domain event types and the DomainEvent model for event-driven operations.
Used for tracking and handling business events such as refunds and shipment status changes.
"""

from enum import Enum
from datetime import datetime

class DomainEventType(Enum):
    REFUND_APPROVED = 'refund_approved'
    REFUND_DENIED = 'refund_denied'
    SHIPMENT_STATUS_CHANGED = 'shipment_status_changed'
    SHIPMENT_ITEM_STATUS_CHANGED = 'shipment_item_status_changed'
    SHIPMENT_EVENT_STATUS_CHANGED = 'shipment_event_status_changed'
    # Add more as needed

class DomainEvent:
    def __init__(self, event_type, entity_id, actor, payload, timestamp=None):
        """
        Initialize DomainEvent.
        Args:
            event_type (DomainEventType): Type of the event.
            entity_id (int): ID of the affected entity.
            actor (str): Actor who triggered the event.
            payload (dict): Event-specific data.
            timestamp (datetime, optional): Event timestamp.
        """
        self.event_type = event_type
        self.entity_id = entity_id
        self.actor = actor
        self.payload = payload  # dict of event-specific data
        self.timestamp = timestamp or datetime.utcnow()
