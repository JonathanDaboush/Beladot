# Represents a refund request and processing for returning money to customers.
# Refunds can be full or partial, and may be tied to returns or issued independently (e.g., for damaged items).
class Refund:
    def __init__(self, id, order_id, payment_id, amount_cents, reason, status, admin_notes, requested_at, processed_at):
        self.id = id  # Unique refund identifier
        self.order_id = order_id  # Links to Order being refunded
        self.payment_id = payment_id  # Links to original Payment to refund (used by payment gateway for transaction reversal)
        self.amount_cents = amount_cents  # How much money to return to customer (in cents, can be less than order total for partial refunds)
        self.reason = reason  # Why refund was issued (e.g., "Defective product", "Customer changed mind", "Item not as described")
        self.status = status  # Refund state: "pending", "approved", "processing", "completed", "failed", "cancelled"
        self.admin_notes = admin_notes  # Internal notes for staff (not visible to customer)
        self.requested_at = requested_at  # When refund was requested by customer or initiated by admin
        self.processed_at = processed_at  # When refund was actually sent to customer's payment method (null if not yet processed)
