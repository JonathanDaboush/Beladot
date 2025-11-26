from typing import Any, Optional
from datetime import datetime, timezone

class ProductVariant:
    def __init__(self, id, product_id, sku, name, price_cents, compare_at_price_cents, cost_cents, stock_quantity, inventory_management, inventory_policy, track_stock, option1_name, option1_value, option2_name, option2_value, option3_name, option3_value):
        self.id = id
        self.product_id = product_id
        self.sku = sku
        self.name = name
        self.price_cents = price_cents
        self.compare_at_price_cents = compare_at_price_cents
        self.cost_cents = cost_cents
        self.stock_quantity = stock_quantity
        self.inventory_management = inventory_management
        self.inventory_policy = inventory_policy
        self.track_stock = track_stock
        self.option1_name = option1_name
        self.option1_value = option1_value
        self.option2_name = option2_name
        self.option2_value = option2_value
        self.option3_name = option3_name
        self.option3_value = option3_value
        self._reservations_cache = None
    
    def adjust_stock(self, delta: int, reason: str, actor_id: Optional[str], reference_id: Optional[str], repository):
        if delta == 0:
            raise ValueError("Delta must be non-zero")
        
        new_quantity = self.stock_quantity + delta
        
        if self.track_stock and new_quantity < 0:
            if self.inventory_policy == "deny":
                raise ValueError(f"Insufficient stock: requested change {delta}, current stock {self.stock_quantity}, would result in {new_quantity}")
        
        if new_quantity < 0:
            new_quantity = 0
        
        from Classes.InventoryTransaction import InventoryTransaction
        transaction = InventoryTransaction(
            id=None,
            variant_id=self.id,
            delta=delta,
            stock_after=new_quantity,
            transaction_type=reason,
            reference_id=reference_id,
            actor_id=actor_id,
            notes=f"Stock adjustment: {reason}",
            created_at=datetime.now(timezone.utc)
        )
        
        self.stock_quantity = new_quantity
        
        if repository:
            repository.update(self)
            transaction = repository.create_transaction(transaction)
        
        return transaction
    
    def available_quantity(self, repository=None) -> int:
        if not self.track_stock:
            return 999999
        
        available = self.stock_quantity
        
        if self._reservations_cache is not None:
            #reservation cache to keep tabs if multi users doing same action.
            available -= self._reservations_cache
        elif repository:
            try:
                reservations = repository.get_active_reservations(self.id)
                reserved_total = sum(r.delta for r in reservations if r.delta < 0)
                available += reserved_total
            except:
                pass
        
        return max(0, available)
    
    def is_in_stock(self, repository=None) -> bool:
        if not self.track_stock:
            return True
        return self.available_quantity(repository) > 0
    
    def to_dict(self) -> dict[str, Any]:
        options = []
        if self.option1_name and self.option1_value:
            options.append({"name": self.option1_name, "value": self.option1_value})
        if self.option2_name and self.option2_value:
            options.append({"name": self.option2_name, "value": self.option2_value})
        if self.option3_name and self.option3_value:
            options.append({"name": self.option3_name, "value": self.option3_value})
        
        has_discount = self.compare_at_price_cents and self.compare_at_price_cents > self.price_cents
        discount_percentage = None
        if has_discount:
            discount_percentage = int(((self.compare_at_price_cents - self.price_cents) / self.compare_at_price_cents) * 100)
        
        return {
            "id": self.id,
            "product_id": self.product_id,
            "sku": self.sku,
            "name": self.name,
            "price_cents": self.price_cents,
            "compare_at_price_cents": self.compare_at_price_cents,
            "has_discount": has_discount,
            "discount_percentage": discount_percentage,
            "stock_quantity": self.stock_quantity if self.track_stock else None,
            "in_stock": self.is_in_stock(),
            "options": options,
            "inventory_policy": self.inventory_policy,
            "track_stock": self.track_stock
        }