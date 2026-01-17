"""
sellerServices.py

Service layer for seller operations, including product creation, variant management, payouts, and analysis.
All repository and model operations use a db session that is request-scoped and managed by the caller (not global).
"""
from backend.repositories.repository.product_repository import ProductRepository
from backend.persistance.product import Product
from backend.repositories.repository.product_comment_repository import ProductCommentRepository
from backend.repositories.repository.order_repository import OrderRepository
from backend.repositories.repository.product_variant_repository import ProductVariantRepository
from backend.persistance.product_variant import ProductVariant
from backend.repositories.repository.product_image_repository import ProductImageRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.persistance.product_image import ProductImage
from backend.repositories.repository.product_variant_repository import ProductVariantRepository
from backend.repositories.repository.seller_payout_repository import SellerPayoutRepository
from backend.persistance.product import Product
from backend.persistance.product_variant import ProductVariant
from backend.repositories.repository.product_image_repository import ProductImageRepository
        
import os
import asyncio

async def create_product(self, product_data):
    """
    Create a new product and its variants for a seller.
    Args:
        product_data: Dictionary containing product and variant details.
    Returns:
        The created Product object.
    """
    db = product_data.get('db')
    repo = ProductRepository(db)
    variant_repo = ProductVariantRepository(db)
    product = Product(
        product_id=None,
        name=product_data['name'],
        description=product_data['description'],
        price=product_data['price'],
        stock=product_data['stock'],
        category_id=product_data['category_id'],
        subcategory_id=product_data['subcategory_id']
    )
    product = await repo.save(product)
    from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
    from backend.persistance.product_variant_image import ProductVariantImage
    # Save variants if provided
    variants = product_data.get('variants', [])
    for v in variants:
        variant = ProductVariant(
            variant_id=None,
            product_id=product.product_id,
            name=v['name'],
            price=v['price'],
            stock=v['stock']
        )
        saved_variant = await variant_repo.save(variant)
        # Create variant image folder
        variant_folder = os.path.join('backend', 'images', 'variant_images', f'variant_{saved_variant.variant_id}')
        os.makedirs(variant_folder, exist_ok=True)
        # Save variant images if provided
        variant_images = v.get('images', [])
        variant_image_repo = ProductVariantImageRepository(db)
        for img_url in variant_images:
            image = ProductVariantImage(
                image_id=None,
                variant_id=saved_variant.variant_id,
                image_url=img_url
            )
            await variant_image_repo.save(image)
    # Create product image folder
    product_folder = os.path.join('backend', 'images', 'product_images', f'product_{product.product_id}')
    os.makedirs(product_folder, exist_ok=True)
    # Save product images if provided
    image_repo = ProductImageRepository(db)
    images = product_data.get('images', [])
    for img_url in images:
        image = ProductImage(
            image_id=None,
            product_id=product.product_id,
            image_url=img_url
        )
        image_repo.save(image)
    return product

async def edit_product(self, product):
    db = product.get('db')
    repo = ProductRepository(db)
    variant_repo = ProductVariantRepository(db)
    product_id = product['product_id']
    update_fields = {k: v for k, v in product.items() if k != 'product_id' and k != 'db' and k != 'variants' and k != 'images'}
    updated_product = await repo.update(product_id, **update_fields)
    import os
    from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
    from backend.persistance.product_variant_image import ProductVariantImage
    # Update or add variants and their images
    variants = product.get('variants', [])
    variant_image_repo = ProductVariantImageRepository(db)
    for v in variants:
        if 'variant_id' in v:
            await variant_repo.update(v['variant_id'], name=v['name'], price=v['price'], stock=v['stock'])
            # Sync variant images
            variant_folder = os.path.join('backend', 'images', 'variant_images', f'variant_{v["variant_id"]}')
            os.makedirs(variant_folder, exist_ok=True)
            existing_images = await variant_image_repo.get_by_variant_id(v['variant_id'])
            existing_urls = set(img.image_url for img in existing_images)
            new_urls = set(v.get('images', []))
            # Remove images not in new list
            for img in existing_images:
                if img.image_url not in new_urls:
                    await variant_image_repo.delete(img.image_id)
                    img_path = os.path.join(variant_folder, os.path.basename(img.image_url))
                    if os.path.exists(img_path):
                        os.remove(img_path)
            # Add new images
            for img_url in new_urls - existing_urls:
                image = ProductVariantImage(
                    image_id=None,
                    variant_id=v['variant_id'],
                    image_url=img_url
                )
                await variant_image_repo.save(image)
        else:
            variant = ProductVariant(
                variant_id=None,
                product_id=product_id,
                name=v['name'],
                price=v['price'],
                stock=v['stock']
            )
            saved_variant = await variant_repo.save(variant)
            variant_folder = os.path.join('backend', 'images', 'variant_images', f'variant_{saved_variant.variant_id}')
            os.makedirs(variant_folder, exist_ok=True)
            for img_url in v.get('images', []):
                image = ProductVariantImage(
                    image_id=None,
                    variant_id=saved_variant.variant_id,
                    image_url=img_url
                )
                await variant_image_repo.save(image)
    # Sync product images and folder
    image_repo = ProductImageRepository(db)
    product_folder = os.path.join('backend', 'images', 'product_images', f'product_{product_id}')
    os.makedirs(product_folder, exist_ok=True)
    if 'images' in product:
        existing_images = await image_repo.get_by_product_id(product_id)
        existing_urls = set(img.image_url for img in existing_images)
        new_urls = set(product['images'])
        # Remove images not in new list
        for img in existing_images:
            if img.image_url not in new_urls:
                await image_repo.delete(img.image_id)
                img_path = os.path.join(product_folder, os.path.basename(img.image_url))
                if os.path.exists(img_path):
                    os.remove(img_path)
        # Add new images
        for img_url in new_urls - existing_urls:
            image = ProductImage(
                image_id=None,
                product_id=product_id,
                image_url=img_url
            )
            await image_repo.save(image)
    # Return product, all variants, and images
    from sqlalchemy import select
    all_variants_res = await db.execute(select(ProductVariant).filter(ProductVariant.product_id == product_id))
    all_variants = all_variants_res.scalars().all()
    all_images = await image_repo.get_by_product_id(product_id)
    return {'product': updated_product, 'variants': all_variants, 'images': all_images}

async def delete_product(self, product_id):
    import os
    from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
    from backend.routes_uploads import delete_uploaded_image
    db = product_id.get('db') if isinstance(product_id, dict) else None
    pid = product_id['product_id'] if isinstance(product_id, dict) else product_id
    repo = ProductRepository(db)
    variant_repo = ProductVariantRepository(db)
    variant_image_repo = ProductVariantImageRepository(db)
    # Delete all variants and their images/folders for this product
    variants_res = await db.execute(select(ProductVariant).filter(ProductVariant.product_id == pid))
    variants = variants_res.scalars().all()
    for v in variants:
        # Delete variant images from DB and folder
        variant_images = await variant_image_repo.get_by_variant_id(v.variant_id)
        variant_folder = os.path.join('backend', 'images', 'variant_images', f'variant_{v.variant_id}')
        for img in variant_images:
            await variant_image_repo.delete(img.image_id)
            img_path = os.path.join(variant_folder, os.path.basename(img.image_url))
            if os.path.exists(img_path):
                os.remove(img_path)
        if os.path.exists(variant_folder):
            try:
                os.rmdir(variant_folder)
            except OSError:
                pass
        await variant_repo.delete(v.variant_id)
    # Delete all product images from DB and folder
    from backend.repositories.repository.product_image_repository import ProductImageRepository
    image_repo = ProductImageRepository(db)
    images = await image_repo.get_by_product_id(pid)
    product_folder = os.path.join('backend', 'images', 'product_images', f'product_{pid}')
    for img in images:
        await image_repo.delete(img.image_id)
        img_path = os.path.join(product_folder, os.path.basename(img.image_url))
        if os.path.exists(img_path):
            os.remove(img_path)
    if os.path.exists(product_folder):
        try:
            os.rmdir(product_folder)
        except OSError:
            pass

    # Cleanup uploaded images (new upload endpoints)
    # Remove all images in /backend/images/uploads/product_{pid}
    delete_uploaded_image(image_id=None, product_id=pid)

    return await repo.delete(pid)

async def get_product(self, product_id):
    from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
    db = product_id.get('db') if isinstance(product_id, dict) else None
    pid = product_id['product_id'] if isinstance(product_id, dict) else product_id
    repo = ProductRepository(db)
    product = await repo.get_by_id(pid)
    from backend.repositories.repository.product_variant_repository import ProductVariantRepository
    variant_repo = ProductVariantRepository(db)
    from sqlalchemy import select
    variants_res = await db.execute(select(ProductVariant).filter(ProductVariant.product_id == pid))
    variants = variants_res.scalars().all()
    # Get product images
    from backend.repositories.repository.product_image_repository import ProductImageRepository
    image_repo = ProductImageRepository(db)
    images = await image_repo.get_by_product_id(pid)
    # Get variant images
    variant_image_repo = ProductVariantImageRepository(db)
    variants_with_images = []
    for v in variants:
        v_images = await variant_image_repo.get_by_variant_id(v.variant_id)
        variants_with_images.append({'variant': v, 'images': v_images})
    return {'product': product, 'variants': variants_with_images, 'images': images}

async def get_all_products(self):
    from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
    db = getattr(self, 'db', None)
    repo = ProductRepository(db)
    from backend.repositories.repository.product_variant_repository import ProductVariantRepository
    variant_repo = ProductVariantRepository(db)
    products_res = await repo.db.execute(select(Product))
    products = products_res.scalars().all()
    result = []
    for p in products:
        variants_res = await repo.db.execute(select(ProductVariant).filter(ProductVariant.product_id == p.product_id))
        variants = variants_res.scalars().all()
        variant_image_repo = ProductVariantImageRepository(db)
        variants_with_images = []
        for v in variants:
            v_images = await variant_image_repo.get_by_variant_id(v.variant_id)
            variants_with_images.append({'variant': v, 'images': v_images})
        result.append({'product': p, 'variants': variants_with_images})
    return result

async def respond_to_comment(self,data):
    db = data.get('db')
    comment_id = data['comment_id']
    response_text = data['response_text']
    repo = ProductCommentRepository(db)
    comment = await repo.get_by_id(comment_id)
    if not comment:
        return None
    comment.response = response_text
    await db.commit()
    return comment

async def analyze_orders_for_product(db: AsyncSession, seller_id, product_id=None, age_range=None, sex=None, start_date=None, end_date=None, analysis_func=None, **analysis_kwargs):
    order_repo = OrderRepository(db)
    # Only use non-deleted, seller-owned products
    product_repo = ProductRepository(db)
    result = await db.execute(select(Product).filter(Product.seller_id == seller_id, Product.is_deleted == False))
    valid_products = result.scalars().all()
    valid_product_ids = [p.product_id for p in valid_products]
    # Only use non-deleted, non-refunded orders
    orders = await order_repo.filter_orders(
        product_id=product_id if product_id in valid_product_ids else None,
        age_range=age_range,
        sex=sex,
        start_date=start_date,
        end_date=end_date
    )



async def get_seller_payout(self, seller_id, year, month, db: AsyncSession):
    repo = SellerPayoutRepository(db)
    payout_result = await repo.db.execute(
        select(repo.model).filter(
            repo.model.seller_id == seller_id,
            repo.model.payout_date.year == year,
            repo.model.payout_date.month == month,
            repo.model.is_deleted == False
        )
    )
    payout = payout_result.scalars().first()
    # Calculate sum of non-deleted, non-refunded orders for this seller and month
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    result_products = await db.execute(select(Product).filter(Product.seller_id == seller_id, Product.is_deleted == False))
    valid_products = result_products.scalars().all()
    valid_product_ids = [p.product_id for p in valid_products]
    orders = await order_repo.filter_orders()
    filtered_orders = [o for o in orders if o.product_id in valid_product_ids and not getattr(o, 'is_deleted', False) and getattr(o, 'status', '').lower() != 'refunded' and getattr(o, 'created_at', None) and o.created_at.year == year and o.created_at.month == month]
    order_sum = sum(getattr(o, 'total_amount', 0) for o in filtered_orders)
    if payout and hasattr(payout, 'total') and abs(order_sum - payout.total) > 0.01:
        raise ValueError(f"Payout total ({payout.total}) does not match sum of orders ({order_sum}) for seller {seller_id} in {year}-{month}.")
    return payout

async def search_products_for_seller(self, seller_id, db: AsyncSession, keywords=None, category_id=None, subcategory_id=None, min_price=None, max_price=None):
    base = select(Product).filter(Product.seller_id == seller_id)
    if category_id:
        base = base.filter(Product.category_id == category_id)
    if subcategory_id:
        base = base.filter(Product.subcategory_id == subcategory_id)
    if min_price is not None:
        base = base.filter(Product.price >= min_price)
    if max_price is not None:
        base = base.filter(Product.price <= max_price)
    products_result = await db.execute(base)
    products = products_result.scalars().all()
    result = []
    keyword_set = set()
    if keywords:
        keyword_set = set(word.lower() for word in keywords.split())
    image_repo = ProductImageRepository(db)
    for product in products:
        matches = False
        text_fields = [getattr(product, 'name', '') or '', getattr(product, 'description', '') or '']
        if keyword_set:
            for field in text_fields:
                if any(kw in field.lower() for kw in keyword_set):
                    matches = True
                    break
        else:
            matches = True
        if matches:
            images = await image_repo.get_by_product_id(product.product_id)
            main_image_url = images[0].image_url if images else None
            result.append({
                'product_id': product.product_id,
                'name': product.name,
                'image_url': main_image_url,
                'price': product.price,
                'category_id': getattr(product, 'category_id', None),
                'category_name': getattr(product, 'category_name', None),
                'subcategory_id': getattr(product, 'subcategory_id', None),
                'subcategory_name': getattr(product, 'subcategory_name', None),
                'is_available': getattr(product, 'is_available', True),
                # Add any other fields shown in user product list here
            })
    # Optionally add pagination info if needed by frontend contract
    return result

async def search_products_for_customer(self, db: AsyncSession, keywords=None, category_id=None, subcategory_id=None, min_price=None, max_price=None):
    base = select(Product)
    if category_id:
        base = base.filter(Product.category_id == category_id)
    if subcategory_id:
        base = base.filter(Product.subcategory_id == subcategory_id)
    if min_price is not None:
        base = base.filter(Product.price >= min_price)
    if max_price is not None:
        base = base.filter(Product.price <= max_price)
    products_result = await db.execute(base)
    products = products_result.scalars().all()
    result = []
    keyword_set = set()
    if keywords:
        keyword_set = set(word.lower() for word in keywords.split())
    image_repo = ProductImageRepository(db)
    for product in products:
        matches = False
        text_fields = [getattr(product, 'name', '') or '', getattr(product, 'description', '') or '']
        if keyword_set:
            for field in text_fields:
                if any(kw in field.lower() for kw in keyword_set):
                    matches = True
                    break
        else:
            matches = True
        images = await image_repo.get_by_product_id(product.product_id)
        if matches:
            result.append({'product': product, 'images': images})
    return result

