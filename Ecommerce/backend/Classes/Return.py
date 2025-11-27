from typing import Any, Optional
from datetime import datetime, timezone

class Return:
    """
    Domain model representing a customer return request with inspection and refund orchestration.
    
    This class manages the return merchandise authorization (RMA) process, from customer
    request through inspection, restocking, and refund processing. It coordinates with
    inventory and payment services for complete return handling.
    
    Key Responsibilities:
        - Track return lifecycle (requested, approved, received, inspected, completed)
        - Store return reason and item condition assessments
        - Manage return items list (what's being returned)
        - Link to customer-provided photos
        - Approve/reject returns with notifications
        - Inspect received items and calculate refund amounts
        - Coordinate inventory restocking
        - Initiate refund processing
    
    Return Lifecycle:
        requested → approved → shipped_back → received → inspected → completed
                  → rejected (terminal)
    
    Item Condition Grading:
        - good: Full refund, restock as new
        - acceptable: 80% refund, 20% restocking fee
        - damaged: No refund, not restocked
    
    Design Notes:
        - return_items is list of dicts with item details
        - photos is list of blob IDs for customer evidence
        - admin_notes and inspection_notes separated for access control
        - This is a domain object; persistence handled by ReturnRepository
    """
    def __init__(self, id, order_id, reason, item_condition, status, return_items, photos, tracking_number, inspection_notes, admin_notes, requested_at, approved_at, rejected_at, shipped_back_at, received_at, inspected_at, completed_at):
        """
        Initialize a Return domain object.
        
        Args:
            id: Unique identifier (None for new returns before persistence)
            order_id: Foreign key to the original order
            reason: Customer's reason for return
            item_condition: Condition assessment dict after inspection
            status: Return status (requested, approved, rejected, received, completed)
            return_items: List of dicts with item details being returned
            photos: List of blob IDs for customer-provided photos
            tracking_number: Carrier tracking number for return shipment
            inspection_notes: Inspector's assessment notes
            admin_notes: Internal notes (not visible to customer)
            requested_at: When customer requested return
            approved_at: When admin approved return
            rejected_at: When admin rejected return
            shipped_back_at: When customer shipped items back
            received_at: When warehouse received items
            inspected_at: When inspector assessed condition
            completed_at: When return fully processed (refund issued)
        """
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
        """
        Approve the return request and notify the customer.
        
        Args:
            actor_id: ID of user approving the return
            repository: Repository for persisting changes and audit log (optional)
            notification_service: Service for customer notification (optional)
            
        Raises:
            ValueError: If return status is not 'requested'
            
        Side Effects:
            - Changes status to 'approved'
            - Sets approved_at to current time
            - Appends approval note to admin_notes with timestamp
            - Creates audit log entry
            - Sends approval notification to customer
            - Persists return via repository
            
        Design Notes:
            - Only 'requested' returns can be approved (guards state transitions)
            - Notification failures silently ignored (logged elsewhere)
            - Admin notes accumulate with timestamps for full history
        """
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
        """
        Process received return items, inspect condition, restock, and issue refund.
        
        Args:
            items_condition: Dict mapping item_id to condition ('good', 'acceptable', 'damaged')
            actor_id: ID of user receiving/inspecting the return
            payment_service: Service for payment operations (currently unused)
            inventory_service: Service for restocking items
            repository: Repository for persisting changes and creating refund
            
        Returns:
            Refund: Created refund object if refund amount > 0, None otherwise
            
        Raises:
            ValueError: If return status is not 'approved' or 'shipped_back'
            
        Side Effects:
            - Changes status to 'received', then 'completed' if refund issued
            - Sets received_at and inspected_at to current time
            - Stores items_condition assessment
            - Creates inspection_notes with actor and timestamp
            - Restocks items with 'good' or 'acceptable' condition
            - Creates Refund record with calculated amounts
            - Sets completed_at timestamp
            - Persists return and refund via repository
            
        Refund Calculation:
            - 'good': Full refund (100%), restock as new
            - 'acceptable': 80% refund, 20% restocking fee
            - 'damaged': No refund, not restocked
            
        Design Notes:
            - Restocking failures silently ignored (logged elsewhere)
            - Refund only created if total amount > 0
            - Restocking fee tracked separately in Refund
        """
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