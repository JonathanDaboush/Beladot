from typing import Any, Optional
from datetime import datetime, timezone

class Cart:
    def __init__(self, id, user_id, created_at, updated_at):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self._items = []
        self._coupons = []
    
    def add_item(self, variant_id: str, quantity: int, unit_price_cents: int, product_id: str, item_metadata: Optional[dict], repository) -> 'CartItem':
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
        self._items = [item for item in self._items if item.id != cart_item_id]
        if repository:
            repository.delete_item(cart_item_id)
        self.updated_at = datetime.now(timezone.utc)
        if repository:
            repository.update(self)
    
    def clear(self, repository=None) -> None:
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
        if not coupon_validator:
            return {"valid": False, "reason": "Coupon validation service unavailable", "discount_cents": 0}
        
        result = coupon_validator.validate_for_cart(self, self.user_id)
        
        if result.get("valid"):
            if code not in self._coupons:
                self._coupons.append(code)
        
        return result
    
    def get_totals(self, pricing_service=None, shipping_address=None, billing_address=None) -> dict[str, Any]:
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