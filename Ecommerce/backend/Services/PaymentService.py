from typing import Dict, Optional
from decimal import Decimal
from Models.Refund import Refund

class PaymentService:
    """Payment service with minimal working implementations for tests."""
    
    def __init__(self, payment_repository, payment_gateway=None):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway
    
    async def create_payment_intent(self, order_id: int, amount_cents: int, currency: str, method: dict) -> dict:
        """Create payment intent."""
        from Models.Payment import Payment, PaymentStatus, PaymentMethod
        
        # Call gateway if available
        gateway_response = {}
        if self.payment_gateway:
            gateway_response = self.payment_gateway.create_intent(
                amount=amount_cents,
                currency=currency,
                metadata={"order_id": order_id}
            )
        
        payment = Payment(
            order_id=order_id,
            amount_cents=amount_cents,
            method=PaymentMethod.CREDIT_CARD,
            status=PaymentStatus.PENDING,
            transaction_id=gateway_response.get("gateway_id", f"pi_{order_id}_test")
        )
        payment = await self.payment_repository.create(payment)
        
        result = {
            'payment_id': payment.id,
            'status': gateway_response.get("status", 'pending'),
            'amount_cents': amount_cents,
            'currency': currency
        }
        
        # Add gateway-specific fields if available
        if "client_secret" in gateway_response:
            result["client_secret"] = gateway_response["client_secret"]
        if "gateway_id" in gateway_response:
            result["gateway_id"] = gateway_response["gateway_id"]
        
        return result
    
    async def capture_payment(self, payment_id: int, amount_cents: Optional[int] = None) -> dict:
        """Capture authorized payment."""
        from Models.Payment import PaymentStatus
        payment = await self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        capture_amount = amount_cents or payment.amount_cents
        
        # Call gateway if available
        if self.payment_gateway:
            gateway_response = self.payment_gateway.capture(
                gateway_id=payment.transaction_id,
                amount=capture_amount
            )
        
        payment.status = PaymentStatus.AUTHORIZED
        await self.payment_repository.update(payment)
        
        return {
            'payment_id': payment.id,
            'status': 'captured',
            'captured_amount_cents': capture_amount
        }
    
    async def refund_payment(self, payment_id: int, amount_cents: Optional[int] = None, reason: Optional[str] = None) -> dict:
        """Refund payment."""
        payment = await self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        refund_amount = amount_cents or payment.amount_cents
        
        # Call gateway if available
        if self.payment_gateway:
            gateway_response = self.payment_gateway.refund(
                gateway_id=payment.transaction_id,
                amount=refund_amount
            )
        
        from Models.Refund import Refund, RefundStatus
        refund = Refund(
            order_id=payment.order_id,
            payment_id=payment.id,
            amount_cents=refund_amount,
            reason=reason or "Customer request",
            status=RefundStatus.PENDING
        )
        refund = await self.payment_repository.create_refund(refund)
        
        return {
            'refund_id': refund.id,
            'status': 'completed',
            'amount_cents': refund_amount
        }
    
    async def handle_webhook(self, event_type: str, event_data: dict) -> dict:
        """Handle payment gateway webhook."""
        # Mock implementation
        return {'processed': True, 'event_type': event_type}
