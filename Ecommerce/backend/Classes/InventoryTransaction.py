# Represents a record of inventory changes for audit trail and stock tracking.
# Every time inventory moves (sale, restock, damage, return), a transaction is logged for accountability.
class InventoryTransaction:
    def __init__(self, id, product_id, transaction_type, quantity_change, quantity_after, reference_id, notes, created_at):
        self.id = id  # Unique transaction identifier
        self.product_id = product_id  # Links to Product whose inventory changed
        self.transaction_type = transaction_type  # Type of change: "sale", "restock", "adjustment", "return", "damage", "loss"
        self.quantity_change = quantity_change  # How much inventory changed (negative for decreases, positive for increases)
        self.quantity_after = quantity_after  # Resulting stock quantity after this transaction (snapshot for verification)
        self.reference_id = reference_id  # Links to related record (Order ID for sales, PO number for restocks, etc.)
        self.notes = notes  # Additional context (e.g., "Damaged in shipping", "Annual inventory count adjustment")
        self.created_at = created_at  # When the inventory change occurred