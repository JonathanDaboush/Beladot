from typing import Any, Optional
from datetime import datetime, timezone

class Shipment:
    def __init__(self, id, order_id, tracking_number, carrier, status, idempotency_key, label_blob_id, cost_cents, failure_reason, shipped_at, estimated_delivery, delivered_at, notes, created_at, updated_at):
        self.id = id
        self.order_id = order_id
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.status = status
        self.idempotency_key = idempotency_key
        self.label_blob_id = label_blob_id
        self.cost_cents = cost_cents
        self.failure_reason = failure_reason
        self.shipped_at = shipped_at
        self.estimated_delivery = estimated_delivery
        self.delivered_at = delivered_at
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at
        self._items = []
    
    def create_label(self, shipping_address: dict, package_spec: dict, carrier_service, blob_service, repository) -> dict[str, Any]:
        if self.label_blob_id and self.tracking_number:
            return {
                "success": True,
                "label_blob_id": self.label_blob_id,
                "tracking_number": self.tracking_number,
                "cost_cents": self.cost_cents,
                "message": "Label already exists"
            }
        
        required_fields = ['line1', 'city', 'state', 'country', 'postal_code']
        for field in required_fields:
            if not shipping_address.get(field):
                return {"success": False, "error": f"Missing required field: {field}"}
        
        if shipping_address.get('country') and len(shipping_address['country']) != 2:
            return {"success": False, "error": "Country must be ISO-2 code"}
        
        if not package_spec.get('weight') or package_spec['weight'] <= 0:
            return {"success": False, "error": "Invalid package weight"}
        
        if not carrier_service:
            return {"success": False, "error": "Carrier service not available"}
        
        try:
            label_response = carrier_service.create_shipping_label(
                carrier=self.carrier,
                shipping_address=shipping_address,
                package_spec=package_spec,
                idempotency_key=self.idempotency_key
            )
            
            if not label_response.get('success'):
                self.status = "failed"
                self.failure_reason = label_response.get('error', 'Unknown error')
                if repository:
                    repository.update(self)
                return label_response
            
            if blob_service and label_response.get('label_data'):
                blob = blob_service.create_blob(
                    data=label_response['label_data'],
                    filename=f"label_{self.order_id}_{datetime.now().timestamp()}.pdf",
                    content_type="application/pdf"
                )
                self.label_blob_id = blob.id
            
            self.tracking_number = label_response.get('tracking_number')
            self.cost_cents = label_response.get('cost_cents', 0)
            self.status = "label_created"
            self.updated_at = datetime.now(timezone.utc)
            
            if repository:
                repository.update(self)
            
            return {
                "success": True,
                "label_blob_id": self.label_blob_id,
                "tracking_number": self.tracking_number,
                "cost_cents": self.cost_cents
            }
            
        except Exception as e:
            self.status = "failed"
            self.failure_reason = str(e)
            if repository:
                repository.update(self)
            return {"success": False, "error": str(e)}
    
    def update_tracking(self, tracking_update: dict, repository=None) -> None:
        if not tracking_update:
            return
        
        new_status = tracking_update.get('status')
        if new_status and new_status != self.status:
            valid_statuses = ['pending', 'label_created', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'exception']
            if new_status in valid_statuses:
                self.status = new_status
        
        if tracking_update.get('estimated_delivery'):
            self.estimated_delivery = tracking_update['estimated_delivery']
        
        if tracking_update.get('delivered_at') and not self.delivered_at:
            self.delivered_at = tracking_update['delivered_at']
            self.status = "delivered"
        
        if tracking_update.get('notes'):
            existing_notes = self.notes or ""
            self.notes = f"{existing_notes}\n[{datetime.now(timezone.utc).isoformat()}] {tracking_update['notes']}"
        
        self.updated_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)
    
    def to_dict(self, blob_service=None) -> dict[str, Any]:
        result = {
            "id": self.id,
            "order_id": self.order_id,
            "tracking_number": self.tracking_number,
            "carrier": self.carrier,
            "status": self.status,
            "cost_cents": self.cost_cents,
            "failure_reason": self.failure_reason,
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "estimated_delivery": self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if self.label_blob_id and blob_service:
            try:
                blob = blob_service.get_by_id(self.label_blob_id)
                if blob:
                    result["label_url"] = blob.get_signed_url(ttl_seconds=3600)
            except:
                result["label_url"] = None
        
        return result