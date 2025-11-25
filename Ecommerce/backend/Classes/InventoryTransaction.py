from typing import Any

class InventoryTransaction:
    def __init__(self, id, product_id, transaction_type, quantity_change, quantity_after, reference_id, actor_id, notes, created_at):
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