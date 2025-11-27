from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.ProductImage import ProductImage
from typing import List


class ProductImageRepository:
    """
    Data access layer for ProductImage entities.
    
    This repository manages product image metadata and associations,
    supporting image ordering and primary image designation.
    
    Responsibilities:
        - ProductImage CRUD operations
        - Query images by product (sorted)
        - Support image gallery management
    
    Design Patterns:
        - Repository Pattern: Isolates image data access
        - Async/Await: Non-blocking database I/O
    
    Usage:
        repository = ProductImageRepository(db_session)
        images = await repository.get_by_product(product_id)
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = ProductImage
    
    async def get_by_id(self, image_id: int) -> ProductImage:
        """
        Retrieve a product image by ID.
        
        Args:
            image_id: The unique ID of the image
            
        Returns:
            ProductImage: The image object if found, None otherwise
        """
        result = await self.db.execute(select(ProductImage).where(ProductImage.id == image_id))
        return result.scalar_one_or_none()
    
    async def get_by_product(self, product_id: int) -> List[ProductImage]:
        """
        Get all images for a product, ordered by sort_order.
        
        Args:
            product_id: The product ID to query
            
        Returns:
            List[ProductImage]: Images in display order
            
        Ordering:
            Results sorted by sort_order (ascending)
        """
        result = await self.db.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
        )
        return result.scalars().all()
    
    async def create(self, image: ProductImage) -> ProductImage:
        """
        Add a new image to a product.
        
        Args:
            image: ProductImage object to persist
            
        Returns:
            ProductImage: Created image with database-generated ID
        """
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image
    
    async def update(self, image: ProductImage):
        """
        Update image metadata (alt_text, sort_order, is_primary).
        
        Args:
            image: ProductImage object with modifications
        """
        await self.db.merge(image)
        await self.db.commit()
        await self.db.refresh(image)
    
    async def delete(self, image_id: int):
        """
        Remove an image from a product.
        
        Args:
            image_id: ID of the image to delete
            
        Note:
            Does not delete the underlying blob (file)
        """
        image = await self.get_by_id(image_id)
        if image:
            await self.db.delete(image)
            await self.db.commit()
