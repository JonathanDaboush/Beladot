from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Payment as payment, Order as order, Refund as refund
from Ecommerce.backend.Repositories import PaymentRepository as paymentrepository, RefundRepository as refundrepository

class PaymentService:
    """
    Payment Gateway Abstraction Service
    Translates domain payment intents into provider-specific actions.
    Creates payment intents, captures and refunds, handles webhooks to reconcile
    asynchronous events. Implements plugin interface for multiple gateways.
    Ensures sensitive operations are idempotent and auditable.
    """
    
    def __init__(self, payment_repository, gateway_provider):
        self.payment_repository = payment_repository
        self.gateway_provider = gateway_provider
    
    def create_payment_intent(self, order_id: UUID, amount_cents: int, currency: str, method: dict) -> dict:
        """
        Create gateway-specific intent or token, return {client_secret, gateway_id, next_action}
        to drive client-side flows for authentication.
        Persist initial Payment record with status='pending'.
        """
        pass
    
    def capture(self, payment_id: UUID, amount_cents: int | None = None) -> dict:
        """
        Perform capture on an authorized intent. Return normalized response and update
        Payment persistence. Handle partial captures and idempotency.
        """
        pass
    
    def refund(self, payment_id: UUID, amount_cents: int) -> dict:
        """
        Request refund from gateway, persist Refund or Payment state changes,
        and return normalized response. Ensure safe retries and idempotency.
        """
        pass
    
    def handle_webhook(self, gateway: str, payload: dict) -> None:
        """
        Normalize gateway events and update Payment and Order state accordingly
        (e.g., mark order paid on charge.succeeded).
        Ensure deduplication by event id and verify signatures.
        """
        pass
