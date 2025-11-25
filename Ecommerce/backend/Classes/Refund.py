from typing import Any

class Refund:
    def __init__(self, id, order_id, payment_id, return_id, amount_cents, restocking_fee_cents, reason, status, gateway_transaction_id, idempotency_key, admin_notes, requested_at, approved_at, processed_at):
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