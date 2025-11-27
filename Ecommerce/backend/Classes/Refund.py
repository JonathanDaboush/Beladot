from typing import Any

class Refund:
    """
    Domain model representing a refund transaction with lifecycle tracking.
    
    This class manages refunds issued to customers, tracking the refund lifecycle
    from request through approval and processing. It supports both return-based
    and non-return refunds (e.g., order cancellations).
    
    Key Responsibilities:
        - Store refund details (amount, reason, associated entities)
        - Track refund lifecycle (requested, approved, processed)
        - Link to order, payment, and optionally return
        - Support restocking fees
        - Maintain gateway transaction references
        - Enable idempotency via idempotency_key
    
    Refund Types:
        - Return-based: Customer returns items (has return_id)
        - Cancellation: Order cancelled before shipment (no return_id)
        - Adjustment: Price correction or goodwill gesture
    
    Lifecycle States:
        - requested: Customer requested refund
        - pending: Approved, awaiting processing
        - approved: Admin approved refund
        - processed: Gateway processed refund
        - failed: Gateway rejected refund
    
    Design Notes:
        - Prices stored in cents (avoids floating-point errors)
        - restocking_fee_cents deducted from refund amount
        - idempotency_key prevents duplicate refunds
        - gateway_transaction_id links to payment processor
        - This is a domain object; persistence handled by RefundRepository
    """
    def __init__(self, id, order_id, payment_id, return_id, amount_cents, restocking_fee_cents, reason, status, gateway_transaction_id, idempotency_key, admin_notes, requested_at, approved_at, processed_at):
        """
        Initialize a Refund domain object.
        
        Args:
            id: Unique identifier (None for new refunds before persistence)
            order_id: Foreign key to the order
            payment_id: Foreign key to the payment being refunded
            return_id: Foreign key to return (None for non-return refunds)
            amount_cents: Gross refund amount in cents (before fees)
            restocking_fee_cents: Fee deducted from refund (default 0)
            reason: Explanation for refund
            status: Refund status (requested, pending, approved, processed, failed)
            gateway_transaction_id: Payment gateway refund transaction ID
            idempotency_key: Unique key to prevent duplicate refunds
            admin_notes: Internal notes (not visible to customer)
            requested_at: When refund was requested
            approved_at: When admin approved refund
            processed_at: When gateway processed refund
        """
        self.id = id
        self.order_id = order_id
        self.payment_id = payment_id
        self.return_id = return_id
        self.amount_cents = amount_cents
        self.restocking_fee_cents = restocking_fee_cents
        self.reason = reason
        self.status = status
        self.gateway_transaction_id = gateway_transaction_id
        self.idempotency_key = idempotency_key
        self.admin_notes = admin_notes
        self.requested_at = requested_at
        self.approved_at = approved_at
        self.processed_at = processed_at
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert refund to dictionary for API responses.
        
        Returns:
            dict: Refund data with calculated net_refund_cents (amount - restocking fee)
            
        Design Notes:
            - Net refund is what customer actually receives
            - admin_notes excluded (use separate endpoint with auth)
        """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "return_id": self.return_id,
            "amount_cents": self.amount_cents,
            "restocking_fee_cents": restocking_fee_cents,
            "net_refund_cents": self.amount_cents - self.restocking_fee_cents,
            "reason": self.reason,
            "status": self.status,
            "gateway_transaction_id": self.gateway_transaction_id,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }