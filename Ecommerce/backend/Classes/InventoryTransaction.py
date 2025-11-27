from typing import Any

class InventoryTransaction:
    """
    Domain model representing an immutable inventory movement record for audit and reconciliation.
    
    This class captures every change to product inventory quantities, providing a complete
    audit trail for stock movements. It records what changed, by how much, the resulting
    quantity, who made the change, and why.
    
    Key Responsibilities:
        - Record inventory quantity changes (increases and decreases)
        - Track transaction type (sale, restock, adjustment, return, damage)
        - Capture quantity_before and quantity_after for reconciliation
        - Link to source documents (orders, returns, etc.)
        - Attribute changes to actors (users, systems)
        - Store explanatory notes
    
    Transaction Types:
        - sale: Inventory sold to customer
        - restock: New inventory received
        - adjustment: Manual correction
        - return: Customer return
        - damage: Damaged/lost inventory write-off
        - reservation: Inventory held for pending order
        - release: Reservation cancelled
    
    Audit Trail Features:
        - Immutable once created (no updates or deletes)
        - Complete change history (sum of changes = current stock)
        - Actor attribution (who made each change)
        - Reference links to source documents
    
    Design Notes:
        - This is a write-only model (created but never updated)
        - quantity_change can be positive (increase) or negative (decrease)
        - quantity_after enables sanity checking and reconciliation
        - This is a domain object; persistence handled by InventoryTransactionRepository
    """
    def __init__(self, id, product_id, transaction_type, quantity_change, quantity_after, reference_id, actor_id, notes, created_at):
        """
        Initialize an InventoryTransaction domain object.
        
        Args:
            id: Unique identifier (None for new transactions before persistence)
            product_id: Foreign key to the product or variant
            transaction_type: Type of transaction (e.g., 'sale', 'restock', 'adjustment')
            quantity_change: Change amount (positive for increase, negative for decrease)
            quantity_after: Resulting quantity after this transaction
            reference_id: ID of related document (order ID, return ID, etc.)
            actor_id: ID of user/system who performed the transaction
            notes: Human-readable explanation
            created_at: Transaction timestamp
        """
        self.id = id
        self.product_id = product_id
        self.transaction_type = transaction_type
        self.quantity_change = quantity_change
        self.quantity_after = quantity_after
        self.reference_id = reference_id
        self.actor_id = actor_id
        self.notes = notes
        self.created_at = created_at
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert inventory transaction to dictionary for API responses.
        
        Returns:
            dict: Transaction data with all fields for audit reporting
        """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "transaction_type": self.transaction_type,
            "quantity_change": self.quantity_change,
            "quantity_after": self.quantity_after,
            "reference_id": self.reference_id,
            "actor_id": self.actor_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }