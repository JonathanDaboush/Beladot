from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Product import Product
from typing import List


class ProductRepository:
    """
    Data access layer for Product entities.
    
    This repository provides async database operations for Product records. It handles
    CRUD operations and common product queries like slug lookups and pagination.
    
    Responsibilities:
        - CRUD operations for Product entities
        - Query by ID or slug (SEO-friendly URLs)
        - Paginated product listings
        - Database session management
    
    Design Patterns:
        - Repository Pattern: Isolates data access from business logic
        - Async/Await: Non-blocking database I/O
        - Session Injection: Database session provided via constructor
    
    Usage:
        repository = ProductRepository(db_session)
        product = await repository.get_by_slug("awesome-t-shirt")
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: Async SQLAlchemy session for database operations
        """
        self.db = db
        self.model = Product
    
    async def get_by_id(self, product_id: int) -> Product:
        """
        Retrieve a product by its unique identifier.
        
        Args:
            product_id: The unique ID of the product
            
        Returns:
            Product: The product object if found, None otherwise
            
        Database:
            Uses primary key index for O(1) lookup
        """
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Product:
        """
        Retrieve a product by its URL slug.
        
        Args:
            slug: The SEO-friendly URL identifier (e.g., 'awesome-t-shirt')
            
        Returns:
            Product: The product object if found, None otherwise
            
        Database:
            Uses unique index on slug column for fast lookup
        """
        result = await self.db.execute(select(Product).where(Product.slug == slug))
        return result.scalar_one_or_none()
    
    async def create(self, product: Product) -> Product:
        """
        Persist a new product to the database.
        
        Args:
            product: Product object to create (id should be None)
            
        Returns:
            Product: The created product with database-generated ID
            
        Side Effects:
            - Sets product.id to database-generated value
            - Sets created_at and updated_at via database defaults
            - Commits transaction immediately
            
        Errors:
            Raises SQLAlchemy exception if:
            - Slug already exists (unique constraint violation)
            - SKU already exists (unique constraint violation)
            - Validation constraints fail
        """
        # Ensure seller_id is present
        if not hasattr(product, 'seller_id') or product.seller_id is None:
            raise ValueError('seller_id is required for product creation')
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def update(self, product: Product):
        """
        Update an existing product in the database.
        
        Args:
            product: Product object with modifications
            
        Side Effects:
            - Updates product.updated_at via database trigger
            - Commits transaction immediately
            
        Design:
            Uses merge() to handle detached objects safely
        """
        # Ensure seller_id is present
        if not hasattr(product, 'seller_id') or product.seller_id is None:
            raise ValueError('seller_id is required for product update')
        await self.db.merge(product)
        await self.db.commit()
        await self.db.refresh(product)
    
    async def get_all(self, limit: int = 100, offset: int = 0, seller_id: int = None) -> List[Product]:
        """
        Retrieve paginated list of all products.
        
        Args:
            limit: Maximum number of products to return (default 100)
            offset: Number of products to skip (default 0)
            seller_id: Optional seller_id to filter products by seller
            
        Returns:
            List[Product]: List of product objects
            
        Pagination:
            - limit controls page size
            - offset enables pagination (page * limit)
            - No specific ordering (use application-level sorting)
        """
        query = select(Product)
        if seller_id is not None:
            query = query.where(Product.seller_id == seller_id)
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_variants_and_total_quantity(self, product_id: int):
        """
        Retrieve all variants for a given product_id and return both the list of variants and the total quantity.
        Returns (variants_list, total_quantity)
        """
        from Models.ProductVariant import ProductVariant
        result = await self.db.execute(select(ProductVariant).where(ProductVariant.product_id == product_id))
        variants = result.scalars().all()
        total_quantity = sum(v.stock_quantity for v in variants)
        return variants, total_quantity
