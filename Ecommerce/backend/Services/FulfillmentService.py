from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Shipment as shipment, ShipmentItem as shipmentitem, Order as order, Blob as blob
from Ecommerce.backend.Repositories import ShipmentRepository as shipmentrepository, ShipmentItemRepository as shipmentitemrepository, BlobRepository as blobrepository

class FulfillmentService:
    """
    Shipping and Fulfillment Service
    Handles packaging decisions, label generation, carrier integrations, and shipment tracking.
    Builds shipment payloads, calls carrier APIs (idempotently), produces shipping labels,
    stores label blobs, and provides tracking updates to customers.
    Supports multi-carrier, service-level rates and address validation.
    """
    
    def __init__(self, shipment_repository, carrier_provider, blob_service):
        self.shipment_repository = shipment_repository
        self.carrier_provider = carrier_provider
        self.blob_service = blob_service
    
    def create_shipment(self, order_id: UUID, items: list[dict], carrier: str | None = None):
        """
        Build a shipment for the order (or part of it), compute package specs,
        call carrier to create label, store label blob, and return a Shipment record with tracking.
        Must be idempotent and ensure labels are not double-created for the same items.
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
            action='create_shipment',
            target_type='order',
            target_id=str(order_id),
            item_metadata={
                'order_id': str(order_id),
                'items': items,
                'carrier': carrier
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
    
    def track_shipment(self, shipment_id: UUID) -> dict:
        """
        Query carrier APIs for current tracking state and return normalized tracking info.
        Cache results briefly to avoid excessive carrier API load.
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
            action='track_shipment',
            target_type='shipment',
            target_id=str(shipment_id),
            item_metadata={
                'shipment_id': str(shipment_id)
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
    
    def handle_tracking_update(self, shipment_id: UUID, update: dict) -> None:
        """
        Ingest webhook updates from carriers, update shipment status, notify customers,
        and forward to WebhookService or other integrations.
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
            action='handle_tracking_update',
            target_type='shipment',
            target_id=str(shipment_id),
            item_metadata={
                'shipment_id': str(shipment_id),
                'update': update
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
