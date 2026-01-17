"""
domain_event.py

Domain event types and model for event-driven operations.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

class DomainEventType(Enum):
    REFUND_APPROVED = 'refund_approved'
    REFUND_DENIED = 'refund_denied'
    SHIPMENT_STATUS_CHANGED = 'shipment_status_changed'
    SHIPMENT_ITEM_STATUS_CHANGED = 'shipment_item_status_changed'
    SHIPMENT_EVENT_STATUS_CHANGED = 'shipment_event_status_changed'

@dataclass(slots=True)
class DomainEvent:
    event_type: DomainEventType
    entity_id: int
    actor: str
    payload: Dict
    timestamp: Optional[datetime] = None
