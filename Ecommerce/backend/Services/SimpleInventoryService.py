"""
Simple Inventory Service for Product-level stock management.
This is a simplified version for testing that works with Product entities directly.
"""
from typing import List, Optional
from Repositories.ProductRepository import ProductRepository


class SimpleInventoryService:
    """
    Simplified inventory service that works with Product stock_quantity directly.
    For use in tests that don't need the full ProductVariant/InventoryTransaction complexity.
    """
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    async def check_availability(self, product_id: int, requested_qty: int) -> bool:
        """Check if product has sufficient stock."""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return False
        return product.stock_quantity >= requested_qty
    
    async def reserve_stock(self, product_id: int, qty: int, reason: str = "reservation") -> bool:
        """Reserve stock by decrementing product quantity."""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return False
        
        if product.stock_quantity < qty:
            return False
        
        product.stock_quantity -= qty
        await self.product_repository.update(product)
        return True
    
    async def release_stock(self, product_id: int, qty: int) -> bool:
        """Release reserved stock by incrementing product quantity."""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        product.stock_quantity += qty
        await self.product_repository.update(product)
        return True
    
    async def update_stock_level(self, product_id: int, new_quantity: int) -> bool:
        """Set product stock to a specific level."""
        if new_quantity < 0:
            raise ValueError("Stock level cannot be negative")
        
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return False
        
        product.stock_quantity = new_quantity
        await self.product_repository.update(product)
        return True
    
    async def get_stock_level(self, product_id: int) -> Optional[int]:
        """Get current stock level for a product."""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return None
        return product.stock_quantity
    
    async def restock_product(self, product_id: int, qty: int) -> bool:
        """Add stock to a product."""
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            return False
        
        product.stock_quantity += qty
        await self.product_repository.update(product)
        return True

