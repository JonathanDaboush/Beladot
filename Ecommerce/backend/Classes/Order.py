from typing import Any, Optional
from datetime import datetime, timezone

class Order:
    def __init__(self, id, user_id, order_number, status, subtotal_cents, tax_cents, shipping_cost_cents, discount_cents, total_cents, shipping_address_line1, shipping_address_line2, shipping_city, shipping_state, shipping_country, shipping_postal_code, customer_notes, admin_notes, created_at, updated_at):
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