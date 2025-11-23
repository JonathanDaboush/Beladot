# Represents a customer's order with pricing breakdown, shipping details, and order lifecycle tracking.
# An order contains multiple OrderItems and goes through various statuses (pending → paid → shipped → delivered).
class Order:
    def __init__(self, id, user_id, order_number, status, subtotal_cents, tax_cents, shipping_cost_cents, discount_cents, total_cents, shipping_address_line1, shipping_address_line2, shipping_city, shipping_state, shipping_country, shipping_postal_code, customer_notes, admin_notes, created_at, updated_at):
        self.id = id  # Unique order identifier in database
        self.user_id = user_id  # Links to User who placed the order
        self.order_number = order_number  # Human-readable order reference (e.g., "ORD-2024-001234") shown to customers
        self.status = status  # Order lifecycle state: pending, paid, processing, shipped, delivered, cancelled, refunded
        self.subtotal_cents = subtotal_cents  # Sum of all OrderItem totals before tax/shipping/discounts (in cents)
        self.tax_cents = tax_cents  # Calculated sales tax based on shipping address (in cents)
        self.shipping_cost_cents = shipping_cost_cents  # Delivery fee charged to customer (in cents)
        self.discount_cents = discount_cents  # Total discount from coupons/promotions applied to order (in cents)
        self.total_cents = total_cents  # Final amount charged: subtotal + tax + shipping - discount (in cents)
        self.shipping_address_line1 = shipping_address_line1  # Street address for delivery (e.g., "123 Main St")
        self.shipping_address_line2 = shipping_address_line2  # Additional address info (apartment, suite, etc.)
        self.shipping_city = shipping_city  # City for delivery
        self.shipping_state = shipping_state  # State/province for delivery
        self.shipping_country = shipping_country  # Country for delivery (2-letter code like "US")
        self.shipping_postal_code = shipping_postal_code  # ZIP/postal code for delivery
        self.customer_notes = customer_notes  # Special delivery instructions from customer (e.g., "Leave at door")
        self.admin_notes = admin_notes  # Internal notes for staff/fulfillment team (not visible to customer)
        self.created_at = created_at  # When order was placed
        self.updated_at = updated_at  # When order status/details were last modified