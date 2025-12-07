from typing import Dict, Optional
from decimal import Decimal
from Models.Refund import Refund

class PaymentService:
    """Payment service for payment intents, captures, and stored methods."""
    
    def __init__(self, payment_repository, payment_method_repository=None, payment_gateway=None):
        self.payment_repository = payment_repository
        self.payment_method_repository = payment_method_repository
        self.payment_gateway = payment_gateway
    
    async def create_payment_intent(self, order_id: int, amount_cents: int, currency: str, payment_method_id: Optional[int] = None, method: dict = None) -> dict:
        """
        Create payment intent (authorization before payment).
        This reserves funds but doesn't charge the customer yet.
        """
        from Models.Payment import Payment, PaymentStatus, PaymentMethod
        
        gateway_token = None
        payment_method_type = PaymentMethod.CREDIT_CARD
        
        # If using stored payment method, retrieve gateway token
        if payment_method_id and self.payment_method_repository:
            stored_method = await self.payment_method_repository.get_by_id(payment_method_id)
            if stored_method:
                gateway_token = stored_method.gateway_token
                payment_method_type = PaymentMethod.CREDIT_CARD  # Or map from stored_method.card_brand
        
        # Call gateway if available
        gateway_response = {}
        if self.payment_gateway:
            gateway_response = self.payment_gateway.create_intent(
                amount=amount_cents,
                currency=currency,
                payment_method=gateway_token,
                metadata={"order_id": order_id}
            )
        
        payment = Payment(
            order_id=order_id,
            amount_cents=amount_cents,
            method=payment_method_type,
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
        """
        Capture authorized payment (complete the charge).
        This actually charges the customer after payment intent was created.
        """
        from Models.Payment import PaymentStatus
        payment = await self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError(f"Cannot capture payment with status {payment.status}")
        
        capture_amount = amount_cents or payment.amount_cents
        
        # Call gateway if available
        if self.payment_gateway:
            gateway_response = self.payment_gateway.capture(
                gateway_id=payment.transaction_id,
                amount=capture_amount
            )
        
        payment.status = PaymentStatus.COMPLETED  # Changed to COMPLETED after successful capture
        await self.payment_repository.update(payment)
        
        return {
            'payment_id': payment.id,
            'status': 'captured',
            'captured_amount_cents': capture_amount
        }
    
    async def charge_stored_payment_method(self, user_id: int, amount_cents: int, currency: str, order_id: int, payment_method_id: Optional[int] = None) -> dict:
        """
        Charge a stored payment method directly (for subscriptions, recurring charges).
        Combines create_intent + capture into one step.
        """
        # Get payment method (use default if not specified)
        if payment_method_id:
            stored_method = await self.payment_method_repository.get_by_id(payment_method_id)
        else:
            stored_method = await self.payment_method_repository.get_default_for_user(user_id)
        
        if not stored_method:
            raise ValueError("No payment method found")
        
        if not stored_method.is_active:
            raise ValueError("Payment method is inactive")
        
        # Create payment intent with stored method
        intent = await self.create_payment_intent(
            order_id=order_id,
            amount_cents=amount_cents,
            currency=currency,
            payment_method_id=stored_method.id
        )
        
        # Immediately capture the payment
        capture_result = await self.capture_payment(intent['payment_id'], amount_cents)
        
        return {
            'payment_id': intent['payment_id'],
            'status': 'completed',
            'amount_cents': amount_cents,
            'currency': currency,
            'payment_method': {
                'brand': stored_method.card_brand,
                'last_four': stored_method.card_last_four
            }
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
