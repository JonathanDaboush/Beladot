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
        # Fetch order and user
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        # Only send confirmation if order is paid and not already sent
        if getattr(order, 'confirmation_email_sent', False):
            return  # Idempotency: do not resend
        if order.status not in ("paid", "completed", "processing", "shipped", "delivered"):
            return  # Only send for paid or further states

        # Fetch user (assume user repository or user object available)
        user = getattr(order, 'user', None)
        if not user:
            if hasattr(self.order_repository, 'get_user_for_order'):
                user = self.order_repository.get_user_for_order(order.id)
            else:
                raise ValueError("User not found for order")

        # Prepare order rows for email
        order_rows = ""
        for item in getattr(order, 'items', []):
            order_rows += f"<tr><td>{item.product_name} {item.variant_name or ''}</td><td>{item.quantity}</td><td>${item.unit_price_cents/100:.2f}</td><td>${item.total_price_cents/100:.2f}</td></tr>"

        # Prepare variables for template
        variables = {
            "first_name": getattr(user, 'first_name', 'Customer'),
            "order_rows": order_rows,
            "total": f"${order.total_cents/100:.2f}"
        }

        # Send email
        from Ecommerce.backend.Utilities.email import EmailService
        email_service = EmailService()
        to_email = getattr(user, 'email', None)
        if to_email:
            email_service.send_email(
                to_email=to_email,
                subject="Your Order Confirmation",
                html_content=email_service._render_template(
                    email_service._load_template("order_confirmation"),
                    variables
                )
            )

        # Mark as sent (persist if possible)
        setattr(order, 'confirmation_email_sent', True)
        if hasattr(self.order_repository, 'update'):
            self.order_repository.update(order)

        # Continue with fulfillment and analytics as needed
    
    def cancel_order(self, order_id: UUID, reason: str) -> bool:
        """
        Cancel order and perform compensating actions: if paid, call PaymentService.refund;
        if reserved, call InventoryService.release_reservation; update order status and audit.
        Ensure the cancellation is idempotent and that refund attempts are safely re-triable.
        """
        pass
