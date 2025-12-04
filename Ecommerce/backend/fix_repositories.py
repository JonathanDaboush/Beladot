"""
Script to add missing repository methods needed by tests.
"""

CART_REPO_ADDITIONS = '''
    async def create(self, cart: Cart) -> Cart:
        """Create a new cart."""
        self.db.add(cart)
        await self.db.commit()
        await self.db.refresh(cart)
        return cart
    
    async def get_by_id(self, cart_id: int) -> Cart:
        """Get cart by ID."""
        result = await self.db.execute(select(Cart).where(Cart.id == cart_id))
        return result.scalar_one_or_none()
    
    async def get_active_cart_by_user_id(self, user_id: int) -> Cart:
        """Get active cart for user."""
        result = await self.db.execute(
            select(Cart).where(Cart.user_id == user_id, Cart.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_by_session_id(self, session_id: str) -> Cart:
        """Get cart by session ID."""
        result = await self.db.execute(select(Cart).where(Cart.session_id == session_id))
        return result.scalar_one_or_none()
    
    async def add_item_to_cart(self, cart_id: int, product_id: int, quantity: int) -> CartItem:
        """Add item to cart."""
        # Check if item already exists
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        )
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            existing_item.quantity += quantity
            await self.update_item(existing_item)
            return existing_item
        else:
            # Get product price
            from Models.Product import Product
            result = await self.db.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one_or_none()
            
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                price_cents=product.price_cents if product else 0
            )
            return await self.create_item(cart_item)
    
    async def remove_item_from_cart(self, cart_id: int, product_id: int) -> bool:
        """Remove item from cart."""
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        )
        item = result.scalar_one_or_none()
        if item:
            await self.delete_item(item.id)
            return True
        return False
    
    async def update_cart_item_quantity(self, cart_id: int, product_id: int, quantity: int) -> CartItem:
        """Update cart item quantity."""
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        )
        item = result.scalar_one_or_none()
        if item:
            item.quantity = quantity
            await self.update_item(item)
            return item
        return None
    
    async def clear_cart(self, cart_id: int) -> bool:
        """Clear all items from cart."""
        await self.db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
        await self.db.commit()
        return True
    
    async def merge_carts(self, source_cart_id: int, dest_cart_id: int) -> Cart:
        """Merge source cart items into destination cart."""
        # Get source items
        result = await self.db.execute(select(CartItem).where(CartItem.cart_id == source_cart_id))
        source_items = result.scalars().all()
        
        # Add each item to destination
        for item in source_items:
            await self.add_item_to_cart(dest_cart_id, item.product_id, item.quantity)
        
        # Clear source cart
        await self.clear_cart(source_cart_id)
        
        # Return destination cart
        return await self.get_by_id(dest_cart_id)
    
    async def apply_coupon_to_cart(self, cart_id: int, coupon_code: str) -> bool:
        """Apply coupon to cart."""
        cart = await self.get_by_id(cart_id)
        if cart:
            cart.coupon_code = coupon_code
            await self.update(cart)
            return True
        return False
'''

ORDER_REPO_ADDITIONS = '''
    async def create(self, order: Order) -> Order:
        """Create a new order."""
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def get_by_id(self, order_id: int) -> Order:
        """Get order by ID."""
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()
    
    async def get_by_order_number(self, order_number: str) -> Order:
        """Get order by order number."""
        result = await self.db.execute(select(Order).where(Order.order_number == order_number))
        return result.scalar_one_or_none()
'''

PAYMENT_REPO_ADDITIONS = '''
    async def create(self, payment: Payment) -> Payment:
        """Create a new payment."""
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def get_by_id(self, payment_id: int) -> Payment:
        """Get payment by ID."""
        result = await self.db.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()
    
    async def update(self, payment: Payment):
        """Update payment."""
        await self.db.merge(payment)
        await self.db.commit()
        await self.db.refresh(payment)
    
    async def create_refund(self, refund: Refund) -> Refund:
        """Create a refund."""
        self.db.add(refund)
        await self.db.commit()
        await self.db.refresh(refund)
        return refund
'''

import os

def add_methods_to_file(filepath, additions, marker="# Add test helper methods here"):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add at the end of the class if marker not found
    if marker not in content:
        # Find the last method and add after it
        content = content.rstrip() + "\n" + additions
    else:
        content = content.replace(marker, additions)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Add methods to repositories
repos_dir = os.path.dirname(os.path.abspath(__file__)) + "/Repositories"

print("Adding missing methods to repositories...")

cart_repo_path = f"{repos_dir}/CartRepository.py"
if os.path.exists(cart_repo_path):
    add_methods_to_file(cart_repo_path, CART_REPO_ADDITIONS)
    print("✓ Updated CartRepository.py")

order_repo_path = f"{repos_dir}/OrderRepository.py"
if os.path.exists(order_repo_path):
    add_methods_to_file(order_repo_path, ORDER_REPO_ADDITIONS)
    print("✓ Updated OrderRepository.py")

payment_repo_path = f"{repos_dir}/PaymentRepository.py"
if os.path.exists(payment_repo_path):
    add_methods_to_file(payment_repo_path, PAYMENT_REPO_ADDITIONS)
    print("✓ Updated PaymentRepository.py")

print("\n✓ All repositories updated successfully!")
