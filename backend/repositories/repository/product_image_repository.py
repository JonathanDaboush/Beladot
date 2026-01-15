
# ------------------------------------------------------------------------------
# product_image_repository.py
# ------------------------------------------------------------------------------
# Repository for accessing ProductImage records from the database.
# Provides async CRUD methods for product images and product-specific queries.
# ------------------------------------------------------------------------------

from backend.model.product_image import ProductImage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class ProductImageRepository:
    """
    Repository for ProductImage model.
    Provides async CRUD operations for product images and product-specific queries.
    """
    def __init__(self, db: AsyncSession):
        """Initialize repository with async DB session."""
        self.db = db

    async def get_by_id(self, image_id):
        """Retrieve a product image by its ID."""
        result = await self.db.execute(
            select(ProductImage).filter(ProductImage.image_id == image_id)
        )
        return result.scalars().first()

    async def get_by_product_id(self, product_id):
        """Retrieve all images for a specific product."""
        result = await self.db.execute(
            select(ProductImage).filter(ProductImage.product_id == product_id)
        )
        return result.scalars().all()

    async def save(self, image):
        """Save a new product image to the database."""
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def update(self, image_id, **kwargs):
        """Update an existing product image by ID with provided fields."""
        image = await self.get_by_id(image_id)
        if not image:
            return None
        for k, v in kwargs.items():
            if hasattr(image, k):
                setattr(image, k, v)
        await self.db.commit()
        return image

    async def delete(self, image_id):
        """Delete a product image by its ID."""
        image = await self.get_by_id(image_id)
        if image:
            await self.db.delete(image)
            await self.db.commit()
            return True
        return False
