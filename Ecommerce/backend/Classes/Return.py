from typing import Any, Optional
from datetime import datetime, timezone

class Return:
    def __init__(self, id, order_id, reason, item_condition, status, return_items, photos, tracking_number, inspection_notes, admin_notes, requested_at, approved_at, rejected_at, shipped_back_at, received_at, inspected_at, completed_at):
        self.id = id
        self.order_id = order_id
        self.reason = reason
        self.item_condition = item_condition
        self.status = status
        self.return_items = return_items
        self.photos = photos
        self.tracking_number = tracking_number
        self.inspection_notes = inspection_notes
        self.admin_notes = admin_notes
        self.requested_at = requested_at
        self.approved_at = approved_at
        self.rejected_at = rejected_at
        self.shipped_back_at = shipped_back_at
        self.received_at = received_at
        self.inspected_at = inspected_at
        self.completed_at = completed_at
    
    def approve(self, actor_id: str, repository=None, notification_service=None) -> None:
        if self.status != "requested":
            raise ValueError(f"Cannot approve return with status: {self.status}")
        
        self.status = "approved"
        self.approved_at = datetime.now(timezone.utc)
        self.admin_notes = f"{self.admin_notes or ''}\n[{datetime.now(timezone.utc).isoformat()}] Approved by {actor_id}"
        
        if repository:
            repository.update(self)
            repository.create_audit_log({
                "actor_id": actor_id,
                "action": "return.approved",
                "target_type": "return",
                "target_id": self.id,
                "metadata": {"order_id": self.order_id}
            })
        
        if notification_service:
            try:
                notification_service.send_return_approved_notification(self)
            except:
                pass
    
    def receive(self, items_condition: dict, actor_id: str, payment_service, inventory_service, repository) -> Optional['Refund']:
        if self.status not in ["approved", "shipped_back"]:
            raise ValueError(f"Cannot receive return with status: {self.status}")
        
        self.status = "received"
        self.received_at = datetime.now(timezone.utc)
        self.inspected_at = datetime.now(timezone.utc)
        self.item_condition = items_condition
        
        total_refund_cents = 0
        restocking_fee_cents = 0
        
        for item_id, condition in items_condition.items():
            if condition == "good":
                item = next((i for i in self.return_items if i.get('id') == item_id), None)
                if item:
                    total_refund_cents += item.get('unit_price_cents', 0) * item.get('quantity', 0)
            elif condition == "acceptable":
                item = next((i for i in self.return_items if i.get('id') == item_id), None)
                if item:
                    refund = int(item.get('unit_price_cents', 0) * item.get('quantity', 0) * 0.8)
                    total_refund_cents += refund
                    restocking_fee_cents += int(item.get('unit_price_cents', 0) * item.get('quantity', 0) * 0.2)
        
        self.inspection_notes = f"Inspected by {actor_id} at {datetime.now(timezone.utc).isoformat()}"
        
        if repository:
            repository.update(self)
        
        if inventory_service and items_condition:
            for item_id, condition in items_condition.items():
                if condition in ["good", "acceptable"]:
                    item = next((i for i in self.return_items if i.get('id') == item_id), None)
                    if item and item.get('variant_id'):
                        try:
                            inventory_service.restock_variant(
                                variant_id=item['variant_id'],
                                quantity=item.get('quantity', 0),
                                reason=f"Return {self.id} accepted"
                            )
                        except:
                            pass
        
        if total_refund_cents > 0 and payment_service:
            from Classes.Refund import Refund
            refund = Refund(
                id=None,
                order_id=self.order_id,
                payment_id=None,
                return_id=self.id,
                amount_cents=total_refund_cents,
                restocking_fee_cents=restocking_fee_cents,
                reason=f"Return {self.id} processed",
                status="pending",
                gateway_transaction_id=None,
                idempotency_key=None,
                admin_notes=f"Processed by {actor_id}",
                requested_at=datetime.now(timezone.utc),
                approved_at=None,
                processed_at=None
            )
            
            if repository:
                refund = repository.create_refund(refund)
            
            self.status = "completed"
            self.completed_at = datetime.now(timezone.utc)
            
            if repository:
                repository.update(self)
            
            return refund
        
        return None