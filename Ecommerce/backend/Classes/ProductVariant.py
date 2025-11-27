from typing import Any, Optional
from datetime import datetime, timezone

class ProductVariant:
    """
    Domain model representing a specific product variant with inventory management.
    
    This class manages product variations (size, color, etc.) with independent pricing,
    inventory tracking, and stock adjustment capabilities. It supports complex inventory
    policies and reservation systems.
    
    Key Responsibilities:
        - Store variant-specific attributes (options, pricing, inventory)
        - Adjust stock levels with transaction logging
        - Calculate available quantity (stock minus reservations)
        - Support multiple inventory policies (deny, continue)
        - Track up to 3 option dimensions (e.g., Color/Size/Material)
    
    Inventory Management:
        - Track stock: Enable/disable inventory tracking
        - Inventory policy: 'deny' (prevent overselling) or 'continue' (allow)
        - Reservations: Hold stock for pending orders
        - Available = stock - active reservations
    
    Option System:
        - Up to 3 option dimensions (option1, option2, option3)
        - Each option has name (e.g., 'Color') and value (e.g., 'Blue')
        - Options combine to form unique variants
    
    Design Notes:
        - Prices stored in cents (avoids floating-point errors)
        - compare_at_price_cents enables strike-through pricing
        - cost_cents tracks COGS for margin analysis
        - This is a domain object; persistence handled by ProductVariantRepository
    """
    def __init__(self, id, product_id, sku, name, price_cents, compare_at_price_cents, cost_cents, stock_quantity, inventory_management, inventory_policy, track_stock, option1_name, option1_value, option2_name, option2_value, option3_name, option3_value):
        """
        Initialize a ProductVariant domain object.
        
        Args:
            id: Unique identifier (None for new variants before persistence)
            product_id: Foreign key to parent product
            sku: Stock Keeping Unit identifier
            name: Variant display name (e.g., "Blue / Large")
            price_cents: Selling price in cents
            compare_at_price_cents: Original price for discounts (None if no discount)
            cost_cents: Product cost/COGS in cents
            stock_quantity: Current inventory count
            inventory_management: Inventory system identifier (e.g., 'internal', 'shopify')
            inventory_policy: Policy for out-of-stock ('deny' or 'continue')
            track_stock: Whether to track inventory for this variant
            option1_name: First option dimension name (e.g., 'Color')
            option1_value: First option value (e.g., 'Blue')
            option2_name: Second option dimension name (e.g., 'Size')
            option2_value: Second option value (e.g., 'Large')
            option3_name: Third option dimension name (e.g., 'Material')
            option3_value: Third option value (e.g., 'Cotton')
        """
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
        """
        Adjust inventory quantity and create transaction record.
        
        Args:
            delta: Change amount (positive for increase, negative for decrease)
            reason: Transaction type (e.g., 'sale', 'restock', 'adjustment')
            actor_id: User/system performing the adjustment
            reference_id: Related document ID (order ID, etc.)
            repository: Repository for persisting changes
            
        Returns:
            InventoryTransaction: Created transaction record
            
        Raises:
            ValueError: If delta is 0 or would result in negative stock with 'deny' policy
            
        Side Effects:
            - Updates self.stock_quantity
            - Creates InventoryTransaction record
            - Persists variant and transaction via repository
            
        Inventory Policy:
            - 'deny': Raises error if adjustment would go negative
            - 'continue': Clamps to 0 if would go negative
            
        Design Notes:
            - All stock changes logged for audit trail
            - Quantity clamped to 0 minimum (never negative)
            - Transaction records quantity_after for reconciliation
        """
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
        """
        Calculate quantity available for purchase (stock minus reservations).
        
        Args:
            repository: Repository for querying active reservations (optional)
            
        Returns:
            int: Available quantity (never negative)
            
        Calculation:
            - If not tracking stock: returns 999999 (effectively unlimited)
            - Otherwise: stock_quantity - sum of active reservations
            - Uses _reservations_cache if available (performance)
            - Clamped to 0 minimum
            
        Design Notes:
            - Reservations are negative deltas in inventory transactions
            - Cache enables performance optimization
            - Repository failures silently ignored (returns stock quantity)
        """
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
        """
        Check if variant is currently available for purchase.
        
        Args:
            repository: Repository for reservation lookup (optional)
            
        Returns:
            bool: True if available quantity > 0 or stock not tracked
        """
        if not self.track_stock:
            return True
        return self.available_quantity(repository) > 0
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert product variant to dictionary for API responses.
        
        Returns:
            dict: Variant data with computed fields (discount info, stock status,
                  formatted options array)
                  
        Design Notes:
            - Options formatted as list of {name, value} objects
            - Empty options excluded from list
            - Discount percentage calculated if compare_at_price set
            - stock_quantity hidden if not tracking inventory
        """
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