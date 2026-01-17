
# ------------------------------------------------------------------------------
# product_variant_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing ProductVariant records from the database.
# Provides async CRUD methods and stock management for product variants.
# ------------------------------------------------------------------------------

from backend.persistance.product_variant import ProductVariant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ProductVariantRepository:
    """
    Repository for ProductVariant model.
    Provides async CRUD operations and stock management for product variants.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def decrement_stock(self, variant_id, qty):
        """Decrement the stock of a product variant by a given quantity if sufficient stock exists."""
        result = await self.db.execute(
            select(ProductVariant).filter(ProductVariant.variant_id == variant_id, ProductVariant.stock >= qty, ProductVariant.is_deleted == False)
        )
        variant = result.scalars().first()
        if variant:
            variant.stock -= qty
            await self.db.commit()
            return True
        return False

    async def get_by_id(self, variant_id):
        """Retrieve a product variant by its ID, excluding deleted variants."""
        result = await self.db.execute(
            select(ProductVariant).filter(ProductVariant.variant_id == variant_id, ProductVariant.is_deleted == False)
        )
        return result.scalars().first()

    async def save(self, variant):
        """Save a new product variant to the database."""
        self.db.add(variant)
        await self.db.commit()
        await self.db.refresh(variant)
        return variant

    async def update(self, variant_id, **kwargs):
        """Update an existing product variant by ID with provided fields."""
        variant = await self.get_by_id(variant_id)
        if not variant:
            return None
        for k, v in kwargs.items():
            if hasattr(variant, k):
                setattr(variant, k, v)
        await self.db.commit()
        return variant

    async def delete(self, variant_id):
        """Soft delete a product variant by its ID (marks as unavailable)."""
        variant = await self.get_by_id(variant_id)
        if variant:
            variant.is_available = False
            await self.db.commit()
            return True
        return False
