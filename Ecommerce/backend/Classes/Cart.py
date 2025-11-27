from typing import Any, Optional
from datetime import datetime, timezone

class Cart:
    """
    Domain model representing a shopping cart with item management and pricing capabilities.
    
    This class manages a user's shopping session, tracking items, quantities, applied coupons,
    and providing total calculations. It integrates with repositories for persistence and
    external services for pricing, tax, and coupon validation.
    
    Key Responsibilities:
        - Manage cart items (add, update, remove, clear)
        - Apply and track promotional coupons
        - Calculate totals (subtotal, tax, shipping, discounts)
        - Generate order payload for checkout
        - Maintain updated_at timestamp for cart modifications
    
    Design Patterns:
        - Aggregate Root: Cart owns CartItems lifecycle
        - Service Integration: Delegates pricing/tax to PricingService
        - Repository Pattern: Accepts repository for persistence operations
    
    Performance Considerations:
        - Items stored in memory list for fast access during session
        - Repository operations optional (supports testing without persistence)
        - Totals calculated on-demand (not cached)
    
    Usage:
        cart = Cart(id=1, user_id=123, created_at=now, updated_at=now)
        cart.add_item(variant_id='v1', quantity=2, unit_price_cents=1500, 
                     product_id='p1', item_metadata=None, repository=cart_repo)
        totals = cart.get_totals(pricing_service=pricing_svc, shipping_address=addr)
    """
    def __init__(self, id, user_id, created_at, updated_at):
        """
        Initialize a Cart domain object.
        
        Args:
            id: Unique identifier (None for new carts before persistence)
            user_id: Foreign key to the owning user
            created_at: Cart creation timestamp
            updated_at: Last modification timestamp
        """
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self._items = []
        self._coupons = []
    
    def add_item(self, variant_id: str, quantity: int, unit_price_cents: int, product_id: str, item_metadata: Optional[dict], repository) -> 'CartItem':
        """
        Add an item to the cart or update quantity if variant already exists.
        
        If an item with the same variant_id and metadata already exists, its quantity
        is incremented. Otherwise, a new CartItem is created and added to the cart.
        
        Args:
            variant_id: Product variant identifier
            quantity: Number of units to add (must be positive)
            unit_price_cents: Price per unit in cents
            product_id: Parent product identifier
            item_metadata: Optional custom data (e.g., engraving, gift message)
            repository: Repository for persisting changes (optional for testing)
            
        Returns:
            CartItem: The newly created or updated cart item
            
        Raises:
            ValueError: If quantity is not positive
            
        Side Effects:
            - Updates self.updated_at to current UTC time
            - Persists cart item and cart via repository if provided
            - Appends item to self._items if new
            
        Design Notes:
            - Items with same variant but different metadata are treated as separate
            - Price is always updated to current unit_price_cents (supports price changes)
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        existing_item = None
        for item in self._items:
            if item.variant_id == variant_id and item.item_metadata == item_metadata:
                existing_item = item
                break
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.unit_price_cents = unit_price_cents
            if repository:
                repository.update_item(existing_item)
            cart_item = existing_item
        else:
            from Classes.CartItem import CartItem
            cart_item = CartItem(
                id=None,
                cart_id=self.id,
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity,
                unit_price_cents=unit_price_cents,
                item_metadata=item_metadata or {},
                added_at=datetime.now(timezone.utc)
            )
            if repository:
                cart_item = repository.create_item(cart_item)
            self._items.append(cart_item)
        
        self.updated_at = datetime.now(timezone.utc)
        if repository:
            repository.update(self)
        
        return cart_item
    
    def update_item(self, cart_item_id: str, quantity: int, repository) -> Optional['CartItem']:
        """
        Update the quantity of an existing cart item.
        
        Args:
            cart_item_id: ID of the cart item to update
            quantity: New quantity (0 removes the item, negative raises error)
            repository: Repository for persisting changes (optional)
            
        Returns:
            CartItem: Updated item, or None if item not found or quantity was 0
            
        Raises:
            ValueError: If quantity is negative
            
        Side Effects:
            - Updates self.updated_at to current UTC time
            - Persists item and cart via repository if provided
            - Removes item if quantity is 0
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if quantity == 0:
            return self.remove_item(cart_item_id, repository)
        
        for item in self._items:
            if item.id == cart_item_id:
                item.quantity = quantity
                if repository:
                    repository.update_item(item)
                self.updated_at = datetime.now(timezone.utc)
                if repository:
                    repository.update(self)
                return item
        
        return None
    
    def remove_item(self, cart_item_id: str, repository) -> None:
        """
        Remove an item from the cart by ID.
        
        Args:
            cart_item_id: ID of the cart item to remove
            repository: Repository for persisting deletion (optional)
            
        Side Effects:
            - Removes item from self._items list
            - Deletes item from database via repository if provided
            - Updates self.updated_at to current UTC time
            - Persists cart via repository if provided
        """
        self._items = [item for item in self._items if item.id != cart_item_id]
        if repository:
            repository.delete_item(cart_item_id)
        self.updated_at = datetime.now(timezone.utc)
        if repository:
            repository.update(self)
    
    def clear(self, repository=None) -> None:
        """
        Remove all items and coupons from the cart.
        
        Args:
            repository: Repository for persisting deletions (optional)
            
        Side Effects:
            - Clears self._items and self._coupons lists
            - Deletes all items from database via repository if provided
            - Updates self.updated_at to current UTC time
            - Persists cart via repository if provided
        """
        item_ids = [item.id for item in self._items]
        self._items = []
        self._coupons = []
        if repository:
            for item_id in item_ids:
                repository.delete_item(item_id)
        self.updated_at = datetime.now(timezone.utc)
        if repository:
            repository.update(self)
    
    def apply_coupon(self, code: str, coupon_validator) -> dict[str, Any]:
        """
        Validate and apply a coupon code to the cart.
        
        Args:
            code: Coupon code to apply
            coupon_validator: Service to validate coupon eligibility
            
        Returns:
            dict: Validation result with 'valid' (bool), 'reason' (str), 
                  'discount_cents' (int)
                  
        Side Effects:
            - Adds code to self._coupons list if valid
            
        Design Notes:
            - Validation delegated to external service
            - Duplicate coupons are prevented
            - Invalid coupons are not stored but result is returned
        """
        if not coupon_validator:
            return {"valid": False, "reason": "Coupon validation service unavailable", "discount_cents": 0}
        
        result = coupon_validator.validate_for_cart(self, self.user_id)
        
        if result.get("valid"):
            if code not in self._coupons:
                self._coupons.append(code)
        
        return result
    
    def get_totals(self, pricing_service=None, shipping_address=None, billing_address=None) -> dict[str, Any]:
        """
        Calculate comprehensive cart totals including taxes, shipping, and discounts.
        
        Args:
            pricing_service: Service for calculating tax, shipping, discounts (optional)
            shipping_address: Shipping address for tax/shipping calculation (optional)
            billing_address: Billing address (optional, currently unused)
            
        Returns:
            dict: Cart totals with keys:
                - subtotal_cents: Sum of all item line totals
                - discount_cents: Applied discounts from coupons
                - tax_cents: Calculated tax
                - shipping_cents: Shipping cost
                - total_cents: Final amount (never negative)
                - item_count: Number of items in cart
                - items: List of item dictionaries
                
        Design Notes:
            - Subtotal calculated internally, other amounts from pricing_service
            - Without pricing_service, discount/tax/shipping default to 0
            - Total is clamped to non-negative (prevents negative checkout)
        """
        subtotal_cents = sum(item.line_total_cents() for item in self._items)
        
        discount_cents = 0
        tax_cents = 0
        shipping_cents = 0
        
        if pricing_service:
            pricing_result = pricing_service.calculate_cart_totals(self, shipping_address)
            discount_cents = pricing_result.get("discount_cents", 0)
            tax_cents = pricing_result.get("tax_cents", 0)
            shipping_cents = pricing_result.get("shipping_cents", 0)
        
        total_cents = subtotal_cents - discount_cents + tax_cents + shipping_cents
        
        return {
            "subtotal_cents": subtotal_cents,
            "discount_cents": discount_cents,
            "tax_cents": tax_cents,
            "shipping_cents": shipping_cents,
            "total_cents": max(0, total_cents),
            "item_count": len(self._items),
            "items": [item.to_dict() for item in self._items]
        }
    
    def to_order_payload(self, billing_address, shipping_address, pricing_service=None) -> dict[str, Any]:
        """
        Convert cart to order creation payload for checkout.
        
        Args:
            billing_address: Billing address dictionary
            shipping_address: Shipping address dictionary
            pricing_service: Service for final total calculations (optional)
            
        Returns:
            dict: Order payload containing cart_id, user_id, items, addresses,
                  coupons, and all calculated totals
                  
        Design Notes:
            - This is a data transfer object (DTO) for order creation
            - Includes all necessary information to create an Order
            - Items include full details (variant, price, quantity, metadata)
        """
        totals = self.get_totals(pricing_service, shipping_address, billing_address)
        
        return {
            "cart_id": self.id,
            "user_id": self.user_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "variant_id": item.variant_id,
                    "quantity": item.quantity,
                    "unit_price_cents": item.unit_price_cents,
                    "line_total_cents": item.line_total_cents(),
                    "metadata": item.item_metadata
                }
                for item in self._items
            ],
            "coupons": self._coupons,
            "billing_address": billing_address,
            "shipping_address": shipping_address,
            "subtotal_cents": totals["subtotal_cents"],
            "discount_cents": totals["discount_cents"],
            "tax_cents": totals["tax_cents"],
            "shipping_cents": totals["shipping_cents"],
            "total_cents": totals["total_cents"],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }