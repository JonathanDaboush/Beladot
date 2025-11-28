from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import Product as product, ProductVariant as productvariant, Coupon as coupon
from Ecommerce.backend.Repositories import ProductRepository as productrepository, ProductVariantRepository as productvariantrepository, CouponRepository as couponrepository

class PricingService:


    def apply_promotions(self, cart) -> list:
        """
        Automatically apply all active promotion-type coupons to the cart.
        Promotions are coupons with promotion=True and are applied regardless of user activation.
        Returns a list of applied promotion codes.
        """
        coupon_repo = getattr(self.promotion_service, 'coupon_repository', None)
        if not coupon_repo:
            return []
        # Assume coupon_repo has a method to list all coupons (sync or async)
        if hasattr(coupon_repo, 'list_all_sync'):
            all_coupons = coupon_repo.list_all_sync()
        elif hasattr(coupon_repo, 'list_all'):
            import asyncio
            all_coupons = asyncio.run(coupon_repo.list_all())
        else:
            return []
        applied_promos = []
        from Ecommerce.backend.Classes.Coupon import Coupon as CouponClass
        for coupon_obj in all_coupons:
            if getattr(coupon_obj, 'promotion', False) and getattr(coupon_obj, 'is_active', True):
                coupon_domain = CouponClass(
                    id=coupon_obj.id,
                    code=coupon_obj.code,
                    description=coupon_obj.description,
                    discount_type=coupon_obj.discount_type,
                    discount_value_cents=coupon_obj.discount_value_cents,
                    min_purchase_amount_cents=coupon_obj.min_purchase_amount_cents,
                    max_discount_amount_cents=coupon_obj.max_discount_amount_cents,
                    applicable_product_ids=coupon_obj.applicable_product_ids,
                    applicable_category_ids=coupon_obj.applicable_category_ids,
                    usage_limit=coupon_obj.usage_limit,
                    usage_count=coupon_obj.usage_count,
                    per_user_limit=coupon_obj.per_user_limit,
                    is_active=coupon_obj.is_active,
                    starts_at=coupon_obj.starts_at,
                    expires_at=coupon_obj.expires_at,
                    created_at=coupon_obj.created_at,
                    updated_at=coupon_obj.updated_at,
                    external_metadata=getattr(coupon_obj, 'external_metadata', None),
                    promotion=getattr(coupon_obj, 'promotion', False),
                    promotion_metadata=getattr(coupon_obj, 'promotion_metadata', None)
                )
                result = coupon_domain.validate_for_cart(cart, cart.user_id)
                if result.get('valid'):
                    if not hasattr(cart, '_coupons') or coupon_obj.code not in cart._coupons:
                        if hasattr(cart, '_coupons'):
                            cart._coupons.append(coupon_obj.code)
                    applied_promos.append(coupon_obj.code)
        return applied_promos
    """
    Pricing and Tax Calculation Service
    Centralized engine for pricing, taxes, discounts, promotions, and rounding rules.
    Pure service (no DB side-effects) to make totals predictable and testable.
    Computes per-line pricing considering promotions and tax using regional rules.
    """
    
    def __init__(self, product_repository, promotion_service, tax_provider=None):
        self.product_repository = product_repository
        self.promotion_service = promotion_service
        self.tax_provider = tax_provider
    
    def calculate_line_price(self, variant_id: UUID, quantity: int, coupons: list[str], user_id: UUID | None) -> dict:
        """
        Determine unit price, applied discounts, taxes, and total for a single line.
        Applies all valid coupons to this line (if applicable).
        """
        # Fetch product variant and base price
        variant = self.product_repository.get_variant_by_id(variant_id)
        unit_price_cents = variant.price_cents
        line_total_cents = unit_price_cents * quantity
        discounts_cents = 0
        applied_coupons = []
        # Only apply coupons that are explicitly activated/passed in
        coupon_repo = getattr(self.promotion_service, 'coupon_repository', None)
        if coupons and coupon_repo:
            for code in coupons:
                coupon_obj = coupon_repo.get_by_code_sync(code) if hasattr(coupon_repo, 'get_by_code_sync') else None
                if coupon_obj:
                    # Validate coupon for a single line (simulate a cart with just this item)
                    from Ecommerce.backend.Classes.Coupon import Coupon as CouponClass
                    from Ecommerce.backend.Classes.Cart import Cart as CartClass
                    from Ecommerce.backend.Classes.CartItem import CartItem as CartItemClass
                    import datetime
                    fake_cart = CartClass(id=None, user_id=user_id, created_at=datetime.datetime.now(datetime.timezone.utc), updated_at=datetime.datetime.now(datetime.timezone.utc))
                    fake_item = CartItemClass(id=None, cart_id=None, product_id=variant.product_id, variant_id=variant_id, quantity=quantity, unit_price_cents=unit_price_cents, item_metadata=None, added_at=datetime.datetime.now(datetime.timezone.utc))
                    fake_cart._items.append(fake_item)
                    coupon_domain = CouponClass(
                        id=coupon_obj.id,
                        code=coupon_obj.code,
                        description=coupon_obj.description,
                        discount_type=coupon_obj.discount_type,
                        discount_value_cents=coupon_obj.discount_value_cents,
                        min_purchase_amount_cents=coupon_obj.min_purchase_amount_cents,
                        max_discount_amount_cents=coupon_obj.max_discount_amount_cents,
                        applicable_product_ids=coupon_obj.applicable_product_ids,
                        applicable_category_ids=coupon_obj.applicable_category_ids,
                        usage_limit=coupon_obj.usage_limit,
                        usage_count=coupon_obj.usage_count,
                        per_user_limit=coupon_obj.per_user_limit,
                        is_active=coupon_obj.is_active,
                        starts_at=coupon_obj.starts_at,
                        expires_at=coupon_obj.expires_at,
                        created_at=coupon_obj.created_at,
                        updated_at=coupon_obj.updated_at,
                        external_metadata=getattr(coupon_obj, 'external_metadata', None)
                    )
                    result = coupon_domain.validate_for_cart(fake_cart, user_id)
                    if result.get('valid'):
                        discounts_cents += result.get('discount_cents', 0)
                        applied_coupons.append(code)
        # Taxes (if any)
        tax_cents = 0
        if self.tax_provider:
            tax_cents = self.tax_provider.calculate_tax(unit_price_cents * quantity - discounts_cents)
        total_cents = max(0, line_total_cents - discounts_cents + tax_cents)
        return {
            'unit_price_cents': unit_price_cents,
            'quantity': quantity,
            'discounts_cents': discounts_cents,
            'tax_cents': tax_cents,
            'total_cents': total_cents,
            'applied_coupons': applied_coupons
        }
    
    def calculate_cart_totals(self, cart, shipping_address=None) -> dict:
        """
        Aggregate line calculations, apply order-level promotions and coupons,
        compute shipping using FulfillmentService estimates if required,
        and return the final totals with a full per-line breakdown.
        This must be deterministic and usable at order creation time.
        """
        subtotal_cents = sum(item.line_total_cents() for item in cart._items)
        discounts_cents = 0
        applied_coupons = []
        # Only apply coupons that are already activated (in cart._coupons)
        coupon_repo = getattr(self.promotion_service, 'coupon_repository', None)
        if hasattr(cart, '_coupons') and cart._coupons and coupon_repo:
            for code in cart._coupons:
                coupon_obj = coupon_repo.get_by_code_sync(code) if hasattr(coupon_repo, 'get_by_code_sync') else None
                if coupon_obj:
                    from Ecommerce.backend.Classes.Coupon import Coupon as CouponClass
                    coupon_domain = CouponClass(
                        id=coupon_obj.id,
                        code=coupon_obj.code,
                        description=coupon_obj.description,
                        discount_type=coupon_obj.discount_type,
                        discount_value_cents=coupon_obj.discount_value_cents,
                        min_purchase_amount_cents=coupon_obj.min_purchase_amount_cents,
                        max_discount_amount_cents=coupon_obj.max_discount_amount_cents,
                        applicable_product_ids=coupon_obj.applicable_product_ids,
                        applicable_category_ids=coupon_obj.applicable_category_ids,
                        usage_limit=coupon_obj.usage_limit,
                        usage_count=coupon_obj.usage_count,
                        per_user_limit=coupon_obj.per_user_limit,
                        is_active=coupon_obj.is_active,
                        starts_at=coupon_obj.starts_at,
                        expires_at=coupon_obj.expires_at,
                        created_at=coupon_obj.created_at,
                        updated_at=coupon_obj.updated_at,
                        external_metadata=getattr(coupon_obj, 'external_metadata', None)
                    )
                    result = coupon_domain.validate_for_cart(cart, cart.user_id)
                    if result.get('valid'):
                        discounts_cents += result.get('discount_cents', 0)
                        applied_coupons.append(code)
        # Taxes (if any)
        tax_cents = 0
        if self.tax_provider:
            tax_cents = self.tax_provider.calculate_tax(subtotal_cents - discounts_cents)
        # Shipping (if any)
        shipping_cents = 0
        if hasattr(self, 'fulfillment_service') and self.fulfillment_service:
            shipping_cents = self.fulfillment_service.estimate_shipping(cart, shipping_address)
        total_cents = max(0, subtotal_cents - discounts_cents + tax_cents + shipping_cents)
        return {
            'subtotal_cents': subtotal_cents,
            'discount_cents': discounts_cents,
            'tax_cents': tax_cents,
            'shipping_cents': shipping_cents,
            'total_cents': total_cents,
            'applied_coupons': applied_coupons
        }
