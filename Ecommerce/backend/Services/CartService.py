from typing import Any
from uuid import UUID

from Ecommerce.backend.Classes import AuditLog as auditLog
from Ecommerce.backend.Repositories import ProductRepository as productRepository,CartRepository as cartrepository, CartItemRepository as cartitemrepository,UserRepository as userRepository

class CartService:
    """
    Cart Lifecycle Service
    High-level orchestrator for cart lifecycle: create, merge, update, and estimate totals.
    Handles guest-to-user cart merging rules, applies coupons safely, and calls PricingService
    for accurate totals. Conservative about enforcing inventory until checkout.
    """
    
    def __init__(self, cart_repository, pricing_service, promotion_service):
        self.cart_repository = cart_repository
        self.pricing_service = pricing_service
        self.promotion_service = promotion_service
    
    def get_cart(self, user_id: UUID | None, session_id: str | None):
        """
        Return existing cart by user or session or atomically create a new one.
        For logged-in users with an existing guest cart, perform a deterministic merge
        per config and persist result.
        """
        user,session=None,None
        try:
            user=user.UserRepository.get_by_id(user_id) if user_id else None
            session=session.SessionRepository.get_by_id(session_id) if session_id else None
        except Exception as e:
            return None
        if user and session and user.id == session.user_id:
            cart=self.cart_repository.get_active_cart_by_user_id(user.id)
            # Audit log
            from datetime import datetime, timezone
            from Ecommerce.backend.Repositories import AuditLogRepository
            from Ecommerce.backend.Classes import AuditLog as auditLog
            auditLog_entry = auditLog(
                id=None,
                actor_id=user.id if user else None,
                actor_type='user',
                actor_email=getattr(user, 'email', None) if user else None,
                action='get_cart',
                target_type='cart',
                target_id=str(cart.id) if cart else None,
                item_metadata={
                    'user_id': str(user.id) if user else None,
                    'session_id': session_id
                },
                ip_address=None,
                created_at=datetime.now(timezone.utc)
            )
            AuditLogRepository.create(auditLog_entry)
            return cart
    
    def add_to_cart(self, cart_id: UUID, product_id: UUID, quantity: int, metadata: dict | None = None, ipAddress: str = "", user=None):
        """
        Add an item to the cart: persist cart, create CartItem (no variant_id yet), and create audit log.
        """
        from datetime import datetime, timezone
        cart = None
        try:
            cart = self.cart_repository.get_by_id(cart_id)
        except Exception as e:
            return None
        product = productRepository.get_by_id(product_id)
        if product is None:
            return None
        unit_price_cents = product.price_cents
        # Create CartItem (variant_id is None or generated later)
        from Ecommerce.backend.Classes.CartItem import CartItem
        cart_item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            variant_id=None,  # Not yet made
            quantity=quantity,
            unit_price_cents=unit_price_cents,
            item_metadata=metadata or {},
            added_at=datetime.now(timezone.utc)
        )
        # Persist CartItem
        cartitemrepository.create(cart_item)
        # Add to cart's in-memory list
        cart._items.append(cart_item)
        # Persist cart update
        self.cart_repository.update(cart)
        # Audit log
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        auditLog_entry = auditLog(
            id=None,
            actor_id=cart.user_id,
            actor_type='user',
            actor_email=getattr(user, 'email', None) if user else None,
            action='add_to_cart',
            target_type='cart_item',
            target_id=str(cart_item.id),
            item_metadata={
                'cart_id': str(cart.id),
                'product_id': str(product_id),
                'quantity': quantity,
                'unit_price_cents': unit_price_cents
            },
            ip_address=ipAddress,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        return cart_item
    
    def update_cart_item(self, cart_id: UUID, item_id: UUID, quantity: int, user_id: UUID = None, ip_address: str = ""):
        """
        Adjust quantity with validation and return updated line.
        """
        try:
            cart_item = cartitemrepository.get_by_id(item_id)
            
        except Exception as e:
            return {"message": str(e)}
        if not cart_item or not any(i.id == item_id for i in cart_item):
            return None
        cart_item.quantity = quantity
        cartitemrepository.update(cart_item)
        cart = self.cart_repository.get_by_id(cart_id)
        user_email = None
        if user_id:
            try:
                user = userRepository.get_by_id(user_id)
                user_email = getattr(user, 'email', None)
            except Exception:
                user_email = None
        from datetime import datetime, timezone
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        auditLog_entry = auditLog(
            id=None,
            actor_id=cart.user_id,
            actor_type='user',
            actor_email=user_email,
            action='update_cart_item',
            target_type='cart_item',
            target_id=str(cart_item.id),
            item_metadata={
                'cart_id': str(cart.id),
                'item_id': str(item_id),
                'quantity': quantity
            },
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        return cart_item
    
    def apply_coupon(self, cart_id: UUID, code: str) -> dict:
        """
        Validate coupon through PromotionService and attach it to cart if valid
        (still not consuming uses_count). Return result {valid, discount_cents, message}.
        """
        # Audit log
        from datetime import datetime, timezone
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        cart = self.cart_repository.get_by_id(cart_id)
        auditLog_entry = auditLog(
            id=None,
            actor_id=getattr(cart, 'user_id', None),
            actor_type='user',
            actor_email=None,
            action='apply_coupon',
            target_type='cart',
            target_id=str(cart_id),
            item_metadata={
                'cart_id': str(cart_id),
                'code': code
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        pass
    
    def estimate_totals(self, cart_id: UUID, shipping_address=None) -> dict:
        """
        Call PricingService.calculate_cart_totals and return breakdown.
        Must be pure and cacheable.
        """
        cart_items = self.cartitemrepository.get_by_cart_id(cart_id)
        totals=[]
        for item in cart_items:
            totals.append({
                item.unit_price_cents * item.quantity
            })
        total=sum(i for i in totals)
        # Audit log
        from datetime import datetime, timezone
        from Ecommerce.backend.Repositories import AuditLogRepository
        from Ecommerce.backend.Classes import AuditLog as auditLog
        auditLog_entry = auditLog(
            id=None,
            actor_id=None,
            actor_type=None,
            actor_email=None,
            action='estimate_totals',
            target_type='cart',
            target_id=str(cart_id),
            item_metadata={
                'cart_id': str(cart_id),
                'total': total
            },
            ip_address=None,
            created_at=datetime.now(timezone.utc)
        )
        AuditLogRepository.create(auditLog_entry)
        return total
