# Represents a payment transaction for an order - tracks payment processing through external gateways (Stripe, PayPal, etc.).
# One order can have multiple payments (e.g., failed attempt followed by successful payment, or partial payments/refunds).
class Payment:
    def __init__(self, id, order_id, amount_cents, method, status, transaction_id, raw_response, created_at, updated_at):
        self.id = id  # Unique payment record identifier
        self.order_id = order_id  # Links to Order being paid
        self.amount_cents = amount_cents  # Amount charged/processed in this payment transaction (in cents)
        self.method = method  # Payment type: credit_card, debit_card, paypal, bank_transfer, cash_on_delivery
        self.status = status  # Payment state: pending, completed, failed, refunded, cancelled
        self.transaction_id = transaction_id  # Unique ID from payment gateway (e.g., Stripe charge ID like "ch_3ABC123") for reconciliation
        self.raw_response = raw_response  # Full JSON response from payment gateway for debugging and dispute resolution
        self.created_at = created_at  # When payment was initiated
        self.updated_at = updated_at  # When payment status last changed (e.g., from pending to completed)