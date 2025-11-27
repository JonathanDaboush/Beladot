from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Order as order, OrderItem as orderitem, Cart as cart, Address as address
from Ecommerce.backend.Repositories import OrderRepository as orderrepository, OrderItemRepository as orderitemrepository, AddressRepository as addressrepository

class CheckoutService:
    """
    Checkout Orchestration Service
    Coordinator that turns an authenticated or guest cart into a paid Order.
    Orchestrates pricing confirmation, inventory reservation and finalization,
    payment intent creation and capture flows, and triggers fulfillment and notifications.
    Manages transactional integrity and supports idempotency to prevent duplicate orders.
    """
    
    def __init__(self, order_repository, cart_service, inventory_service, payment_service, 
                 pricing_service, notification_service):
        self.order_repository = order_repository
        self.cart_service = cart_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.pricing_service = pricing_service
        self.notification_service = notification_service
    
    def create_order_from_cart(self, cart_id: UUID, billing_address, shipping_address, 
                               payment_method: dict, metadata: dict | None = None, 
                               idempotency_key: str | None = None):
        """
        Validate cart (prices, availability), reserve stock atomically using InventoryService.reserve_stock,
        snapshot cart to an immutable Order with status='pending',
        create Payment intent via PaymentService.create_payment_intent
        (or return client instructions for 3DS), and return the Order.
        Must handle idempotency and protect against double reservations/charges
        by linking operations to idempotency_key.
        """
        pass
    
    def capture_payment(self, order_id: UUID, payment_details: dict):
        """
        Capture a payment (post-authorization) and on success finalize inventory
        (InventoryService.confirm_reservation), change Order.status to paid,
        and enqueue fulfillment jobs. Must be idempotent and support partial captures.
        """
        pass
    
    def complete_checkout(self, order_id: UUID):
        """
        Complete order lifecycle steps after capture: send confirmation emails,
        initiate fulfillment, and mark analytics conversion events.
        This step should be safe to call repeatedly but perform idempotent behavior
        (not re-send duplicate emails).
        """
        pass
    
    def cancel_order(self, order_id: UUID, reason: str) -> bool:
        """
        Cancel order and perform compensating actions: if paid, call PaymentService.refund;
        if reserved, call InventoryService.release_reservation; update order status and audit.
        Ensure the cancellation is idempotent and that refund attempts are safely re-triable.
        """
        pass
