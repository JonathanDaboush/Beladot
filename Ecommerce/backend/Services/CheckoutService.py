import logging
from typing import Any, Optional
from uuid import UUID
from datetime import datetime

from Ecommerce.backend.Classes import Order as order, OrderItem as orderitem, Cart as cart, Address as address
from Ecommerce.backend.Repositories import OrderRepository as orderrepository, OrderItemRepository as orderitemrepository, AddressRepository as addressrepository

# Configure logging
logger = logging.getLogger(__name__)

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
        logger.info(f"Starting checkout for cart_id={cart_id}, idempotency_key={idempotency_key}")
        
        try:
            # Check for existing order with idempotency key
            if idempotency_key:
                existing_order = self.order_repository.get_by_idempotency_key(idempotency_key)
                if existing_order:
                    logger.info(f"Order already exists for idempotency_key={idempotency_key}, order_id={existing_order.id}")
                    return existing_order
            
            # Retrieve and validate cart
            cart = self.cart_service.get_cart(cart_id)
            if not cart or not cart.items:
                logger.error(f"Cart {cart_id} is empty or not found")
                raise ValueError("Cart is empty or not found")
            
            logger.info(f"Cart {cart_id} has {len(cart.items)} items")
            
            # Validate pricing and availability
            pricing_result = self.pricing_service.calculate_cart_total(cart)
            if not pricing_result or pricing_result['total_cents'] <= 0:
                logger.error(f"Invalid pricing for cart {cart_id}")
                raise ValueError("Invalid cart pricing")
            
            logger.info(f"Cart total calculated: {pricing_result['total_cents']} cents")
            
            # Check inventory availability for all items
            for item in cart.items:
                available = self.inventory_service.check_availability(
                    item.variant_id or item.product_id, 
                    item.quantity
                )
                if not available:
                    logger.warning(f"Product {item.product_id} variant {item.variant_id} not available for quantity {item.quantity}")
                    raise ValueError(f"Product {item.product_name} is not available in requested quantity")
            
            # Reserve inventory atomically
            reservation_id = self.inventory_service.reserve_stock(cart.items, idempotency_key)
            logger.info(f"Inventory reserved with reservation_id={reservation_id}")
            
            # Create order from cart snapshot
            order_data = {
                'user_id': cart.user_id,
                'status': 'pending',
                'subtotal_cents': pricing_result['subtotal_cents'],
                'tax_cents': pricing_result['tax_cents'],
                'shipping_cents': pricing_result['shipping_cents'],
                'discount_cents': pricing_result.get('discount_cents', 0),
                'total_cents': pricing_result['total_cents'],
                'billing_address_id': billing_address.id if hasattr(billing_address, 'id') else None,
                'shipping_address_id': shipping_address.id if hasattr(shipping_address, 'id') else None,
                'idempotency_key': idempotency_key,
                'reservation_id': reservation_id,
                'metadata': metadata or {}
            }
            
            new_order = self.order_repository.create(order_data)
            logger.info(f"Order created: order_id={new_order.id}, total={pricing_result['total_cents']} cents")
            
            # Create order items from cart items
            for cart_item in cart.items:
                order_item_data = {
                    'order_id': new_order.id,
                    'product_id': cart_item.product_id,
                    'variant_id': cart_item.variant_id,
                    'product_name': cart_item.product.name if hasattr(cart_item, 'product') else 'Product',
                    'product_sku': cart_item.product.sku if hasattr(cart_item, 'product') else 'SKU',
                    'variant_name': cart_item.variant.name if hasattr(cart_item, 'variant') else None,
                    'quantity': cart_item.quantity,
                    'unit_price_cents': cart_item.unit_price_cents,
                    'total_price_cents': cart_item.unit_price_cents * cart_item.quantity,
                    'discount_cents': 0,
                    'tax_cents': 0
                }
                self.order_repository.create_order_item(order_item_data)
            
            logger.info(f"Order items created for order_id={new_order.id}")
            
            # Create payment intent
            payment_intent = self.payment_service.create_payment_intent(
                order_id=new_order.id,
                amount_cents=pricing_result['total_cents'],
                payment_method=payment_method,
                idempotency_key=idempotency_key
            )
            
            logger.info(f"Payment intent created: payment_id={payment_intent.get('id')}, requires_action={payment_intent.get('requires_action')}")
            
            # Attach payment info to order
            new_order.payment_intent_id = payment_intent.get('id')
            new_order.payment_status = payment_intent.get('status', 'pending')
            self.order_repository.update(new_order)
            
            return {
                'order': new_order,
                'payment_intent': payment_intent,
                'requires_action': payment_intent.get('requires_action', False)
            }
            
        except Exception as e:
            logger.error(f"Failed to create order from cart {cart_id}: {str(e)}", exc_info=True)
            # Rollback inventory reservation if exists
            if 'reservation_id' in locals():
                try:
                    self.inventory_service.release_reservation(reservation_id)
                    logger.info(f"Rolled back inventory reservation {reservation_id}")
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback reservation {reservation_id}: {str(rollback_error)}")
            raise
    
    def capture_payment(self, order_id: UUID, payment_details: dict):
        """
        Capture a payment (post-authorization) and on success finalize inventory
        (InventoryService.confirm_reservation), change Order.status to paid,
        and enqueue fulfillment jobs. Must be idempotent and support partial captures.
        """
        logger.info(f"Starting payment capture for order_id={order_id}")
        
        try:
            # Retrieve order
            order = self.order_repository.get_by_id(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                raise ValueError("Order not found")
            
            # Check if already captured (idempotency)
            if order.status == 'paid':
                logger.info(f"Order {order_id} already paid, skipping capture")
                return {'status': 'already_captured', 'order': order}
            
            if order.status not in ('pending', 'authorized'):
                logger.warning(f"Order {order_id} has invalid status for capture: {order.status}")
                raise ValueError(f"Cannot capture payment for order with status: {order.status}")
            
            # Capture payment via payment service
            logger.info(f"Attempting to capture payment for order {order_id}, amount: {order.total_cents} cents")
            
            capture_result = self.payment_service.capture_payment(
                payment_intent_id=order.payment_intent_id,
                amount_cents=payment_details.get('amount_cents', order.total_cents),
                idempotency_key=f"capture_{order_id}_{datetime.utcnow().isoformat()}"
            )
            
            if not capture_result or capture_result.get('status') != 'succeeded':
                logger.error(f"Payment capture failed for order {order_id}: {capture_result}")
                order.status = 'payment_failed'
                order.payment_status = 'failed'
                self.order_repository.update(order)
                raise ValueError(f"Payment capture failed: {capture_result.get('error', 'Unknown error')}")
            
            logger.info(f"Payment captured successfully for order {order_id}, transaction_id={capture_result.get('transaction_id')}")
            
            # Confirm inventory reservation (finalize stock deduction)
            if hasattr(order, 'reservation_id') and order.reservation_id:
                self.inventory_service.confirm_reservation(order.reservation_id)
                logger.info(f"Inventory reservation confirmed for order {order_id}, reservation_id={order.reservation_id}")
            
            # Update order status
            order.status = 'paid'
            order.payment_status = 'completed'
            order.paid_at = datetime.utcnow()
            order.transaction_id = capture_result.get('transaction_id')
            self.order_repository.update(order)
            
            logger.info(f"Order {order_id} marked as paid")
            
            # Trigger fulfillment and notifications
            try:
                self.complete_checkout(order_id)
                logger.info(f"Checkout completion initiated for order {order_id}")
            except Exception as completion_error:
                logger.error(f"Failed to complete checkout for order {order_id}: {str(completion_error)}", exc_info=True)
                # Don't fail the capture if notification/fulfillment fails
            
            return {
                'status': 'captured',
                'order': order,
                'transaction_id': capture_result.get('transaction_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to capture payment for order {order_id}: {str(e)}", exc_info=True)
            raise
    
    def complete_checkout(self, order_id: UUID):
        """
        Complete order lifecycle steps after capture: send confirmation emails,
        initiate fulfillment, and mark analytics conversion events.
        This step should be safe to call repeatedly but perform idempotent behavior
        (not re-send duplicate emails).
        """
        logger.info(f"Completing checkout for order_id={order_id}")
        
        try:
            # Fetch order and user
            order = self.order_repository.get_by_id(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                raise ValueError("Order not found")

            # Only send confirmation if order is paid and not already sent
            if getattr(order, 'confirmation_email_sent', False):
                logger.info(f"Order {order_id} confirmation already sent, skipping")
                return  # Idempotency: do not resend
                
            if order.status not in ("paid", "completed", "processing", "shipped", "delivered"):
                logger.warning(f"Order {order_id} status is {order.status}, not sending confirmation")
                return  # Only send for paid or further states

            # Fetch user (assume user repository or user object available)
            user = getattr(order, 'user', None)
            if not user:
                if hasattr(self.order_repository, 'get_user_for_order'):
                    user = self.order_repository.get_user_for_order(order.id)
                else:
                    logger.error(f"User not found for order {order_id}")
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
            logger.info(f"Sending order confirmation email for order {order_id} to {getattr(user, 'email', 'unknown')}")
            
            from Ecommerce.backend.Utilities.email import EmailService
            email_service = EmailService()
            to_email = getattr(user, 'email', None)
            
            if to_email:
                email_sent = email_service.send_email(
                    to_email=to_email,
                    subject="Your Order Confirmation",
                    html_content=email_service._render_template(
                        email_service._load_template("order_confirmation"),
                        variables
                    )
                )
                
                if email_sent:
                    logger.info(f"Order confirmation email sent successfully for order {order_id}")
                else:
                    logger.warning(f"Failed to send confirmation email for order {order_id}")
            else:
                logger.warning(f"No email address found for user of order {order_id}")

            # Mark as sent (persist if possible)
            setattr(order, 'confirmation_email_sent', True)
            if hasattr(self.order_repository, 'update'):
                self.order_repository.update(order)
                logger.info(f"Order {order_id} marked as confirmation sent")

            # Notify fulfillment service
            try:
                if hasattr(self, 'fulfillment_service'):
                    self.fulfillment_service.initiate_fulfillment(order_id)
                    logger.info(f"Fulfillment initiated for order {order_id}")
            except Exception as fulfillment_error:
                logger.error(f"Failed to initiate fulfillment for order {order_id}: {str(fulfillment_error)}")
            
            # Track analytics conversion
            try:
                if hasattr(self, 'analytics_service'):
                    self.analytics_service.track_conversion(order_id, order.total_cents)
                    logger.info(f"Analytics conversion tracked for order {order_id}")
            except Exception as analytics_error:
                logger.error(f"Failed to track analytics for order {order_id}: {str(analytics_error)}")
                
            logger.info(f"Checkout completed successfully for order {order_id}")
            
        except Exception as e:
            logger.error(f"Failed to complete checkout for order {order_id}: {str(e)}", exc_info=True)
            raise
    
    def cancel_order(self, order_id: UUID, reason: str) -> bool:
        """
        Cancel order and perform compensating actions: if paid, call PaymentService.refund;
        if reserved, call InventoryService.release_reservation; update order status and audit.
        Ensure the cancellation is idempotent and that refund attempts are safely re-triable.
        """
        logger.info(f"Starting order cancellation for order_id={order_id}, reason={reason}")
        
        try:
            # Retrieve order
            order = self.order_repository.get_by_id(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                raise ValueError("Order not found")
            
            # Check if already cancelled (idempotency)
            if order.status == 'cancelled':
                logger.info(f"Order {order_id} already cancelled")
                return True
            
            # Check if order can be cancelled
            if order.status in ('shipped', 'delivered', 'completed'):
                logger.warning(f"Order {order_id} cannot be cancelled, status: {order.status}")
                raise ValueError(f"Cannot cancel order with status: {order.status}")
            
            logger.info(f"Order {order_id} current status: {order.status}, payment_status: {getattr(order, 'payment_status', 'unknown')}")
            
            # Handle refund if payment was captured
            if order.status == 'paid' or getattr(order, 'payment_status', None) == 'completed':
                logger.info(f"Initiating refund for order {order_id}")
                
                try:
                    refund_result = self.payment_service.refund_payment(
                        payment_intent_id=order.payment_intent_id,
                        amount_cents=order.total_cents,
                        reason=reason,
                        idempotency_key=f"refund_{order_id}_{datetime.utcnow().isoformat()}"
                    )
                    
                    if refund_result and refund_result.get('status') == 'succeeded':
                        logger.info(f"Refund successful for order {order_id}, refund_id={refund_result.get('refund_id')}")
                        order.refund_id = refund_result.get('refund_id')
                        order.payment_status = 'refunded'
                    else:
                        logger.error(f"Refund failed for order {order_id}: {refund_result}")
                        # Continue with cancellation but log failure
                        
                except Exception as refund_error:
                    logger.error(f"Refund error for order {order_id}: {str(refund_error)}", exc_info=True)
                    # Continue with cancellation but log error
            
            # Release inventory reservation
            if hasattr(order, 'reservation_id') and order.reservation_id:
                try:
                    self.inventory_service.release_reservation(order.reservation_id)
                    logger.info(f"Inventory reservation released for order {order_id}, reservation_id={order.reservation_id}")
                except Exception as inventory_error:
                    logger.error(f"Failed to release inventory for order {order_id}: {str(inventory_error)}", exc_info=True)
            
            # Update order status
            order.status = 'cancelled'
            order.cancelled_at = datetime.utcnow()
            order.cancellation_reason = reason
            self.order_repository.update(order)
            
            logger.info(f"Order {order_id} cancelled successfully")
            
            # Send cancellation notification
            try:
                if hasattr(self, 'notification_service'):
                    self.notification_service.send_cancellation_notification(order_id, reason)
                    logger.info(f"Cancellation notification sent for order {order_id}")
            except Exception as notification_error:
                logger.error(f"Failed to send cancellation notification for order {order_id}: {str(notification_error)}")
            
            # Create audit log entry
            try:
                if hasattr(self, 'audit_service'):
                    self.audit_service.log_order_cancellation(order_id, reason)
                    logger.info(f"Audit log created for order cancellation {order_id}")
            except Exception as audit_error:
                logger.error(f"Failed to create audit log for order {order_id}: {str(audit_error)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {str(e)}", exc_info=True)
            raise
