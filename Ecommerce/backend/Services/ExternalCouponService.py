class ExternalCouponService:
    """
    Service for integrating and installing external coupons (e.g., Honey, browser extensions).
    Handles import, validation, and mapping to native coupon system.
    """
    def __init__(self, coupon_repository):
        self.coupon_repository = coupon_repository

    async def install_external_coupon(self, external_code: str, external_metadata: dict) -> int:
        """
        Install an external coupon as a native coupon in the system.
        Args:
            external_code: The coupon code from the external provider
            external_metadata: Any extra info (provider, source, restrictions, etc.)
        Returns:
            The new coupon's ID
        """
        from Ecommerce.backend.Classes.Coupon import Coupon
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        # Set sensible defaults for required fields
        coupon = Coupon(
            id=None,
            code=external_code,
            description=external_metadata.get('description', f'External coupon from provider'),
            discount_type=external_metadata.get('discount_type', 'fixed'),
            discount_value_cents=external_metadata.get('discount_value_cents', 0),
            min_purchase_amount_cents=external_metadata.get('min_purchase_amount_cents'),
            max_discount_amount_cents=external_metadata.get('max_discount_amount_cents'),
            applicable_product_ids=external_metadata.get('applicable_product_ids'),
            applicable_category_ids=external_metadata.get('applicable_category_ids'),
            usage_limit=external_metadata.get('usage_limit'),
            usage_count=0,
            per_user_limit=external_metadata.get('per_user_limit'),
            is_active=True,
            starts_at=now,
            expires_at=now + timedelta(days=external_metadata.get('valid_days', 30)),
            created_at=now,
            updated_at=now,
            external_metadata=external_metadata
        )
        created = await self.coupon_repository.create(coupon)
        return created.id

    async def validate_external_coupon(self, code: str) -> bool:
        """
        Validate if an external coupon code exists and is active in the system.
        """
        coupon = await self.coupon_repository.get_by_code(code)
        return coupon is not None and coupon.is_active
