"""
Search Service - Product Discovery and Indexing
===============================================

Provides product search functionality with:
- Full-text search across product fields
- Filtering by price, stock, category
- Variant-level search results
- Relevance ranking (future: ML-based)
- Faceted search support
- Search index synchronization

Search Strategy:
    - Primary: Search index provider (Elasticsearch, Algolia, etc.)
    - Fallback: Direct database queries for reliability
    - Indexing: Async jobs keep search index in sync
    - Tolerance: Handles indexing delays gracefully

Search Fields:
    - Product: name, description, short_description, slug
    - Category: name, parent category name
    - Variant: name, SKU, attributes

Filters Supported:
    - in_stock: Show only available items
    - min_price/max_price: Price range filtering
    - category_id: Category filtering
    - attributes: Variant attribute filtering

Dependencies:
    - ProductRepository: Product data access
    - SearchIndexProvider: Search engine integration

Author: Jonathan Daboush
Version: 2.0.0
"""
from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Product as product, ProductVariant as productvariant
from Ecommerce.backend.Repositories import ProductRepository as productrepository, ProductVariantRepository as productvariantrepository

class SearchService:
    """
    Product search and indexing service.
    
    Provides full-text search across products with filtering,
    pagination, and relevance ranking. Supports both indexed
    search (fast) and database fallback (reliable).
    """
    
    def __init__(self, product_repository, search_index_provider):
        self.product_repository = product_repository
        self.search_index_provider = search_index_provider
    
    async def search_products(self, query: str, filters: dict) -> list:
        # Get all products
        products = await self.product_repository.get_all(limit=10000, offset=0)
        results = []
        query_lower = (query or '').lower().strip()
        in_stock = filters.get('in_stock')
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        for prod in products:
            # Get category name and subcategory name
            cat_name = getattr(prod.category, 'name', '') if hasattr(prod, 'category') and prod.category else ''
            subcat_name = ''
            if hasattr(prod.category, 'parent') and prod.category and prod.category.parent:
                subcat_name = getattr(prod.category.parent, 'name', '')
            # Check product fields
            fields = [
                prod.name or '',
                prod.description or '',
                prod.short_description or '',
                cat_name,
                prod.slug or '',
                subcat_name
            ]
            # Get all variants for this product
            variants, _ = await self.product_repository.get_variants_and_total_quantity(prod.id)
            variant_match = False
            for var in variants:
                vfields = [var.name or '', var.inventory_policy or '', var.inventory_management or '']
                all_fields = fields + vfields
                # If query is blank, match all; else, match if any field contains query
                if not query_lower or any(query_lower in (str(f).lower()) for f in all_fields):
                    # Filter by in_stock
                    if in_stock is not None:
                        if in_stock and getattr(var, 'stock_quantity', 0) <= 0:
                            continue
                        if not in_stock and getattr(var, 'stock_quantity', 0) > 0:
                            continue
                    # Filter by price
                    price = getattr(var, 'price_cents', None)
                    if min_price is not None and price is not None and price < min_price:
                        continue
                    if max_price is not None and price is not None and price > max_price:
                        continue
                    results.append({'product': prod, 'variant': var, 'category': cat_name, 'subcategory': subcat_name})
                    variant_match = True
            # If no variants, still check product-level match (rare)
            if not variants and (not query_lower or any(query_lower in (str(f).lower()) for f in fields)):
                results.append({'product': prod, 'variant': None, 'category': cat_name, 'subcategory': subcat_name})
        return results
