from typing import Any, IO
from uuid import UUID

from Ecommerce.backend.Classes import Product as product, ProductVariant as productvariant, ProductImage as productimage, Category as category
from Ecommerce.backend.Repositories import (
    ProductRepository as productrepository,
    ProductVariantRepository as productvariantrepository,
    ProductImageRepository as productimagerepository,
    CategoryRepository as categoryrepository,
    AuditLogRepository as auditlogrepository
)

class CatalogService:
    """
    Product Catalog Service
    Primary CRUD and presentation layer for product catalog used by both storefront and admin.
    Handles product/variant creation, updates, and efficient listing with filters.
    Does NOT perform inventory mutations - delegates to InventoryService.
    """
    
    def __init__(self, db_session):
        self.product_repo = productrepository(db_session)
        self.variant_repo = productvariantrepository(db_session)
        self.image_repo = productimagerepository(db_session)
        self.category_repo = categoryrepository(db_session)
        self.audit_repo = auditlogrepository(db_session)
    
    async def create_product(self, payload: dict, actor_id=None):
        # Validate category exists
        category_id = payload.get('category_id')
        category_obj = await self.category_repo.get_by_id(category_id)
        if not category_obj:
            raise ValueError('Category does not exist')
        # Create product
        prod = product(**{k: v for k, v in payload.items() if k != 'variants' and k != 'images'})
        db_prod = await self.product_repo.create(prod)
        # Create default variant if none provided
        variants = payload.get('variants')
        created_variants = []
        if not variants:
            default_variant = productvariant(product_id=db_prod.id, sku=db_prod.sku, name=db_prod.name, price_cents=db_prod.price_cents, compare_at_price_cents=db_prod.compare_at_price_cents, cost_cents=db_prod.cost_cents, stock_quantity=0, inventory_management=None, inventory_policy='deny', track_stock=True, option1_name=None, option1_value=None, option2_name=None, option2_value=None, option3_name=None, option3_value=None)
            created_variants.append(await self.variant_repo.create(default_variant))
        else:
            for v in variants:
                v['product_id'] = db_prod.id
                created_variants.append(await self.variant_repo.create(productvariant(**v)))
        # Create images if provided
        images = payload.get('images', [])
        created_images = []
        for img in images:
            img['product_id'] = db_prod.id
            created_images.append(await self.image_repo.create(productimage(**img)))
        # Audit log
        await self.audit_repo.create({
            'actor_id': actor_id,
            'action': 'create_product',
            'target_type': 'product',
            'target_id': db_prod.id,
            'metadata': {'product': db_prod.name}
        })
        return db_prod
    
    async def update_product(self, product_id: UUID, patch: dict, actor_id=None):
        db_prod = await self.product_repo.get_by_id(product_id)
        if not db_prod:
            raise ValueError('Product not found')
        for k, v in patch.items():
            setattr(db_prod, k, v)
        await self.product_repo.update(db_prod)
        await self.audit_repo.create({
            'actor_id': actor_id,
            'action': 'update_product',
            'target_type': 'product',
            'target_id': db_prod.id,
            'metadata': {'fields_updated': list(patch.keys())}
        })
        return db_prod
    
    async def list_products(self, filters: dict, page: int, per_page: int) -> dict:
        # Simple filter by category for now
        products = await self.product_repo.get_all(limit=per_page, offset=(page-1)*per_page)
        # TODO: Apply more filters as needed
        await self.audit_repo.create({
            'actor_id': None,
            'action': 'list_products',
            'target_type': 'product',
            'target_id': None,
            'metadata': {'filters': filters, 'page': page, 'per_page': per_page}
        })
        return {'products': products}
    
    async def get_product_by_slug(self, slug: str, actor_id=None):
        db_prod = await self.product_repo.get_by_slug(slug)
        if not db_prod:
            return None
        variants, total_qty = await self.product_repo.get_variants_and_total_quantity(db_prod.id)
        images = await self.image_repo.get_by_product(db_prod.id)
        await self.audit_repo.create({
            'actor_id': actor_id,
            'action': 'get_product_by_slug',
            'target_type': 'product',
            'target_id': db_prod.id,
            'metadata': {'slug': slug}
        })
        return {'product': db_prod, 'variants': variants, 'images': images, 'total_quantity': total_qty}
    
    async def create_variant(self, product_id: UUID, variant_payload: dict, actor_id=None):
        variant_payload['product_id'] = product_id
        new_variant = productvariant(**variant_payload)
        created_variant = await self.variant_repo.create(new_variant)
        await self.audit_repo.create({
            'actor_id': actor_id,
            'action': 'create_variant',
            'target_type': 'product_variant',
            'target_id': created_variant.id,
            'metadata': {'product_id': product_id}
        })
        return created_variant
    
    async def update_variant(self, variant_id: UUID, patch: dict, actor_id=None):
        db_variant = await self.variant_repo.get_by_id(variant_id)
        if not db_variant:
            raise ValueError('Variant not found')
        for k, v in patch.items():
            setattr(db_variant, k, v)
        await self.variant_repo.update(db_variant)
        await self.audit_repo.create({
            'actor_id': actor_id,
            'action': 'update_variant',
            'target_type': 'product_variant',
            'target_id': db_variant.id,
            'metadata': {'fields_updated': list(patch.keys())}
        })
        return db_variant
    
    async def upload_image(self, product_id: UUID, variant_id: UUID | None, file_stream: IO, filename: str, actor_id=None):
        # For now, just create ProductImage entry (assume blob already handled)
        img = productimage(id=None, product_id=product_id, blob_id=filename, alt_text=filename, is_primary=False, sort_order=0)
        created_img = await self.image_repo.create(img)
        await self.audit_repo.create({
            'actor_id': actor_id,
            'action': 'upload_image',
            'target_type': 'product_image',
            'target_id': created_img.id,
            'metadata': {'product_id': product_id, 'variant_id': variant_id, 'filename': filename}
        })
        return created_img
