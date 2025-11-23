# Represents a product return request and tracking workflow.
# Customer wants to send items back - separate from Refund (you can return items without refund, or get refund without return).
class Return:
    def __init__(self, id, order_id, reason, status, admin_notes, requested_at, approved_at, received_at):
        self.id = id  # Unique return identifier
        self.order_id = order_id  # Links to Order being returned
        self.reason = reason  # Why customer wants to return (e.g., "Wrong size", "Not as expected", "Defective")
        self.status = status  # Return workflow state: "requested", "approved", "rejected", "shipped_back", "received", "completed"
        self.admin_notes = admin_notes  # Internal staff notes (e.g., "Item arrived damaged", "Approved exception to policy")
        self.requested_at = requested_at  # When customer initiated the return request
        self.approved_at = approved_at  # When return was approved and customer given return instructions (null if not yet approved)
        self.received_at = received_at  # When returned items arrived back at warehouse (null if not yet received)
