from typing import Any, Optional
from datetime import datetime, timezone

class Shipment:
    """
    Domain model representing a shipment with carrier integration and tracking.
    
    This class manages the shipping lifecycle from label creation through delivery,
    integrating with carrier APIs for label generation and tracking updates. It supports
    split shipments (multiple packages per order).
    
    Key Responsibilities:
        - Create shipping labels via carrier APIs
        - Store tracking information (number, carrier, status)
        - Track shipment lifecycle (pending, shipped, in_transit, delivered)
        - Link to label PDF (blob)
        - Calculate shipping costs
        - Process tracking updates from carriers
        - Support idempotency for label creation
    
    Shipment States:
        - pending: Awaiting label creation
        - label_created: Label generated, ready to ship
        - picked_up: Carrier picked up package
        - in_transit: Package en route
        - out_for_delivery: Package on delivery vehicle
        - delivered: Package delivered
        - exception: Delivery exception (delay, address issue, etc.)
        - failed: Label creation failed
    
    Carrier Integration:
        - Supports multiple carriers (UPS, FedEx, USPS, etc.)
        - Label creation with address validation
        - Tracking webhook updates
        - Cost calculation
    
    Design Notes:
        - idempotency_key prevents duplicate label charges
        - label_blob_id links to printable PDF
        - notes field accumulates tracking history
        - This is a domain object; persistence handled by ShipmentRepository
    """
    def __init__(self, id, order_id, tracking_number, carrier, status, idempotency_key, label_blob_id, cost_cents, failure_reason, shipped_at, estimated_delivery, delivered_at, notes, created_at, updated_at):
        """
        Initialize a Shipment domain object.
        
        Args:
            id: Unique identifier (None for new shipments before persistence)
            order_id: Foreign key to the order
            tracking_number: Carrier tracking number
            carrier: Shipping carrier (e.g., 'ups', 'fedex', 'usps')
            status: Shipment status (pending, label_created, delivered, etc.)
            idempotency_key: Unique key to prevent duplicate label creation
            label_blob_id: Foreign key to shipping label PDF blob
            cost_cents: Shipping cost in cents
            failure_reason: Error message if label creation failed
            shipped_at: When package was shipped
            estimated_delivery: Carrier's estimated delivery date
            delivered_at: When package was delivered
            notes: Accumulating notes (tracking updates, exceptions)
            created_at: Shipment creation timestamp
            updated_at: Last modification timestamp
        """
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
        """
        Generate a shipping label via carrier API and store the label PDF.
        
        Args:
            shipping_address: Address dict with line1, city, state, country, postal_code
            package_spec: Package details dict with weight, dimensions
            carrier_service: Service for carrier API integration
            blob_service: Service for storing label PDF
            repository: Repository for persisting changes (optional)
            
        Returns:
            dict: Result with 'success' (bool), 'label_blob_id', 'tracking_number',
                  'cost_cents', and 'error' on failure
                  
        Validation:
            - Shipping address must have required fields (line1, city, state, country, postal_code)
            - Country must be ISO-2 code
            - Package weight must be positive
            
        Side Effects:
            - Calls carrier API to generate label
            - Stores label PDF as blob
            - Sets tracking_number from carrier response
            - Sets cost_cents from carrier response
            - Changes status to 'label_created' on success or 'failed' on error
            - Sets failure_reason on error
            - Updates updated_at timestamp
            - Persists shipment via repository
            
        Idempotency:
            - Returns existing label if already created (checks label_blob_id and tracking_number)
            - Uses idempotency_key to prevent duplicate charges with carrier
            
        Design Notes:
            - Label PDF stored as blob for printing
            - Carrier API errors captured in failure_reason
            - Returns structured result (not exceptions) for caller handling
        """
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
        """
        Process a tracking update from carrier webhook or poll.
        
        Args:
            tracking_update: Update dict with 'status', 'estimated_delivery',
                            'delivered_at', 'notes'
            repository: Repository for persisting changes (optional)
            
        Side Effects:
            - Updates status if new status is valid
            - Updates estimated_delivery if provided
            - Sets delivered_at and status='delivered' if delivery confirmed
            - Appends notes with timestamp
            - Updates updated_at timestamp
            - Persists shipment via repository
            
        Design Notes:
            - Status transitions validated against allowed states
            - Notes accumulate with timestamps for full history
            - delivered_at only set once (first delivery event wins)
            - Gracefully handles partial updates (missing fields ignored)
        """
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
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert shipment to dictionary for API responses.
        
        Returns:
            dict: Shipment data with label download URL if available
            
        Design Notes:
            - Label URL included for convenient access
            - failure_reason included for debugging
        """
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
        
        if self.label_blob_id:
            result["label_url"] = f"/api/blobs/{self.label_blob_id}/download"
        
        return result