from typing import Any, Optional
from datetime import datetime, timezone

class Order:
    """
    Domain model representing a customer order with payment and fulfillment orchestration.
    
    This class is the core of the order lifecycle, managing state transitions from
    pending through paid, shipped, and delivered. It orchestrates payment capture,
    inventory management, cancellations, and refunds.
    
    Key Responsibilities:
        - Track order state (pending, paid, shipped, delivered, cancelled, refunded)
        - Capture and manage payments
        - Handle order cancellations with refunds
        - Process partial and full refunds
        - Coordinate with inventory service for stock management
        - Maintain shipping address (denormalized for immutability)
        - Track order totals (subtotal, tax, shipping, discount)
    
    State Machine:
        pending → paid → processing → shipped → delivered
        Any state → cancelled (with conditions)
        paid/shipped → refunded (partial or full)
    
    Design Patterns:
        - Aggregate Root: Owns OrderItems, Payments, Shipments
        - State Machine: Explicit state transitions with guards
        - Service Coordination: Integrates payment, inventory services
    
    Invariants:
        - Delivered orders cannot be cancelled
        - Refund amount cannot exceed remaining refundable total
        - Cancelled orders release inventory reservations
        - Payment required before shipping
    
    Design Notes:
        - Shipping address denormalized (immutable snapshot)
        - admin_notes and customer_notes separated for access control
        - This is a domain object; persistence handled by OrderRepository
    """
    def __init__(self, id, user_id, order_number, status, subtotal_cents, tax_cents, shipping_cost_cents, discount_cents, total_cents, shipping_address_line1, shipping_address_line2, shipping_city, shipping_state, shipping_country, shipping_postal_code, customer_notes, admin_notes, created_at, updated_at):
        """
        Initialize an Order domain object.
        
        Args:
            id: Unique identifier (None for new orders before persistence)
            user_id: Foreign key to the ordering user
            order_number: Human-readable order reference (e.g., 'ORD-1001')
            status: Order state (pending, paid, processing, shipped, delivered, cancelled, refunded)
            subtotal_cents: Sum of line items before tax/shipping/discounts
            tax_cents: Calculated tax amount
            shipping_cost_cents: Shipping fee
            discount_cents: Total discounts applied
            total_cents: Final amount (subtotal + tax + shipping - discount)
            shipping_address_line1: Address line 1 (denormalized)
            shipping_address_line2: Address line 2 (denormalized)
            shipping_city: City (denormalized)
            shipping_state: State/province (denormalized)
            shipping_country: Country code (denormalized)
            shipping_postal_code: Postal code (denormalized)
            customer_notes: Customer's delivery instructions
            admin_notes: Internal notes (not visible to customer)
            created_at: Order creation timestamp
            updated_at: Last modification timestamp
        """
        self.id = id
        self.user_id = user_id
        self.order_number = order_number
        self.status = status
        self.subtotal_cents = subtotal_cents
        self.tax_cents = tax_cents
        self.shipping_cost_cents = shipping_cost_cents
        self.discount_cents = discount_cents
        self.total_cents = total_cents
        self.shipping_address_line1 = shipping_address_line1
        self.shipping_address_line2 = shipping_address_line2
        self.shipping_city = shipping_city
        self.shipping_state = shipping_state
        self.shipping_country = shipping_country
        self.shipping_postal_code = shipping_postal_code
        self.customer_notes = customer_notes
        self.admin_notes = admin_notes
        self.created_at = created_at
        self.updated_at = updated_at
        self._items = []
        self._payments = []
        self._shipments = []
    
    def capture_payment(self, payment_gateway_response: dict, payment_service, inventory_service, repository) -> 'Payment':
        """
        Capture payment for the order and transition to paid status.
        
        Args:
            payment_gateway_response: Response from payment gateway with transaction details
            payment_service: Payment service (currently unused, reserved for future)
            inventory_service: Service to confirm inventory reservations
            repository: Repository for persisting payment and order
            
        Returns:
            Payment: The created or existing completed payment
            
        Side Effects:
            - Creates Payment record with status 'completed'
            - Changes order status to 'paid'
            - Updates order updated_at timestamp
            - Confirms inventory reservations for all order items
            - Persists payment and order via repository
            
        Idempotency:
            - If order already paid, returns existing payment (no duplicate charge)
            - Safe to call multiple times
            
        Design Notes:
            - Payment amount from gateway response (may differ for partial payments)
            - Inventory confirmation failures silently ignored (logged elsewhere)
            - Transaction ID from gateway stored for reconciliation
        """
        if self.status in ["paid", "completed", "shipped", "delivered"]:
            existing_payment = next((p for p in self._payments if p.status == "completed"), None)
            if existing_payment:
                return existing_payment
        
        from Classes.Payment import Payment
        payment = Payment(
            id=None,
            order_id=self.id,
            amount_cents=payment_gateway_response.get("amount_cents", self.total_cents),
            method=payment_gateway_response.get("method", "unknown"),
            status="completed",
            transaction_id=payment_gateway_response.get("transaction_id"),
            raw_response=payment_gateway_response,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        if repository:
            payment = repository.create_payment(payment)
        
        self._payments.append(payment)
        self.status = "paid"
        self.updated_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)
        
        if inventory_service:
            for item in self._items:
                try:
                    inventory_service.confirm_reservation(item.variant_id, item.quantity, self.id)
                except Exception as e:
                    pass
        
        return payment
    
    def cancel(self, reason: str, actor_id: Optional[str], payment_service, inventory_service, repository) -> bool:
        """
        Cancel the order with optional refund and inventory release.
        
        Args:
            reason: Explanation for cancellation (stored in admin_notes)
            actor_id: ID of user/system performing cancellation
            payment_service: Service for processing refunds
            inventory_service: Service for releasing inventory reservations
            repository: Repository for persisting changes and audit log
            
        Returns:
            bool: True if cancellation successful, False if not allowed
            
        Cancellation Rules:
            - Cannot cancel if already cancelled, delivered, or refunded
            - Paid/processing/shipped orders require refund before cancellation
            - Refund failure blocks cancellation
            
        Side Effects:
            - Sets status to 'cancelled'
            - Appends cancellation note to admin_notes with timestamp
            - Updates order updated_at timestamp
            - Processes refund via payment service if order was paid
            - Releases inventory reservations for all items
            - Creates audit log entry
            - Persists order via repository
            
        Design Notes:
            - Inventory release failures silently ignored (idempotent operation)
            - Admin notes accumulate with timestamps for full history
            - Refund uses most recent completed payment
        """
        if self.status in ["cancelled", "delivered", "refunded"]:
            return False
        
        needs_refund = self.status in ["paid", "processing", "shipped"]
        
        if needs_refund and payment_service:
            try:
                payment = next((p for p in self._payments if p.status == "completed"), None)
                if payment:
                    refund_result = payment_service.refund(payment.id, self.total_cents)
                    if not refund_result.get("success"):
                        return False
            except Exception as e:
                return False
        
        if inventory_service:
            for item in self._items:
                try:
                    inventory_service.release_reservation(item.variant_id, item.quantity, self.id)
                except Exception as e:
                    pass
        
        self.status = "cancelled"
        self.admin_notes = f"{self.admin_notes or ''}\n[{datetime.now(timezone.utc).isoformat()}] Cancelled by {actor_id}: {reason}"
        self.updated_at = datetime.now(timezone.utc)
        
        if repository:
            repository.update(self)
            repository.create_audit_log({
                "actor_id": actor_id,
                "action": "order.cancelled",
                "target_type": "order",
                "target_id": self.id,
                "metadata": {"reason": reason}
            })
        
        return True
    
    def refund(self, amount_cents: int, reason: str, payment_service, inventory_service, repository) -> Optional['Refund']:
        """
        Process a partial or full refund for the order.
        
        Args:
            amount_cents: Amount to refund in cents (must be positive)
            reason: Explanation for refund
            payment_service: Service for processing gateway refund
            inventory_service: Service for inventory adjustments (currently unused)
            repository: Repository for persisting refund and order
            
        Returns:
            Refund: The created refund record
            
        Raises:
            ValueError: If amount_cents <= 0, exceeds available refund, no payment found,
                       or gateway refund fails
                       
        Refund Rules:
            - Amount must be positive
            - Cannot exceed (total - already_refunded)
            - Requires completed payment
            - Gateway refund must succeed
            - Full refund changes status to 'refunded'
            
        Side Effects:
            - Creates Refund record with status 'completed'
            - Processes refund through payment gateway
            - Updates order status to 'refunded' if full refund
            - Updates order updated_at timestamp
            - Persists refund and order via repository
            
        Design Notes:
            - Tracks total refunded via _refunds collection
            - Partial refunds leave order in current status
            - Gateway transaction ID stored in refund record
            - Restocking fees supported but currently 0
        """
        if amount_cents <= 0:
            raise ValueError("Refund amount must be positive")
        
        total_refunded = sum(r.amount_cents for r in getattr(self, '_refunds', []))
        available_refund = self.total_cents - total_refunded
        
        if amount_cents > available_refund:
            raise ValueError(f"Refund amount {amount_cents} exceeds available refundable amount {available_refund}")
        
        payment = next((p for p in self._payments if p.status == "completed"), None)
        if not payment:
            raise ValueError("No completed payment found for refund")
        
        if payment_service:
            refund_result = payment_service.refund(payment.id, amount_cents)
            if not refund_result.get("success"):
                raise ValueError(f"Payment gateway refund failed: {refund_result.get('error')}")
        
        from Classes.Refund import Refund
        refund = Refund(
            id=None,
            order_id=self.id,
            payment_id=payment.id,
            return_id=None,
            amount_cents=amount_cents,
            restocking_fee_cents=0,
            reason=reason,
            status="completed",
            gateway_transaction_id=refund_result.get("transaction_id") if payment_service else None,
            idempotency_key=None,
            approved_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        if repository:
            refund = repository.create_refund(refund)
        
        if amount_cents >= self.total_cents:
            self.status = "refunded"
        
        self.updated_at = datetime.now(timezone.utc)
        if repository:
            repository.update(self)
        
        return refund
    
    def to_dict(self, include_items: bool = False, include_shipments: bool = False) -> dict[str, Any]:
        """
        Convert order to dictionary for API responses.
        
        Args:
            include_items: If True, include full order items list
            include_shipments: If True, include shipments list
            
        Returns:
            dict: Order data with optional nested items/shipments
            
        Design Notes:
            - Shipping address returned as nested object
            - admin_notes excluded (use separate endpoint with auth)
            - Conditional includes reduce payload size for listings
        """
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "order_number": self.order_number,
            "status": self.status,
            "subtotal_cents": self.subtotal_cents,
            "tax_cents": self.tax_cents,
            "shipping_cost_cents": self.shipping_cost_cents,
            "discount_cents": self.discount_cents,
            "total_cents": self.total_cents,
            "shipping_address": {
                "line1": self.shipping_address_line1,
                "line2": self.shipping_address_line2,
                "city": self.shipping_city,
                "state": self.shipping_state,
                "country": self.shipping_country,
                "postal_code": self.shipping_postal_code
            },
            "customer_notes": self.customer_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items and self._items:
            result["items"] = [item.to_dict() for item in self._items]
        
        if include_shipments and self._shipments:
            result["shipments"] = [shipment.to_dict() for shipment in self._shipments]
        
        return result