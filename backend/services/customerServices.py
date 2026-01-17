"""
customerServices.py

Service layer for customer operations, including account deactivation, cart and wishlist management, and email notifications.
All operations are asynchronous and require a database session.
"""

# Remove invalid ...existing code... and ensure all necessary imports are present
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def deactivate_user_account(db: AsyncSession) -> tuple[bool, Optional[str]]:
    """
    Deactivate a user account (set account_status to False) and clear their cart and wishlist.
    Args:
        db: Database session
    Returns:
        Tuple (success: bool, error_message: str or None)
    """
    # user_id should be passed explicitly as a parameter
    # user_id = g.user['user_id']
    ur = UserRepository(db)
    user = await ur.get_by_id(user_id)
    if not user:
        return False, 'User not found.'
    user.account_status = False
    await ur.set_user_for_update(user)

    # Clear cart
    cart_repo = CartRepository(db)
    cart_item_repo = CartItemRepository(db)
    cart_result = await db.execute(select(Cart).filter(Cart.user_id == user_id))
    cart = cart_result.scalars().first()
    if cart:
        cart_items_result = await db.execute(select(CartItem).filter(CartItem.cart_id == cart.cart_id))
        cart_items = cart_items_result.scalars().all()
        for item in cart_items:
            await db.delete(item)
        await db.commit()

    # Clear wishlist
    wishlist_repo = WishlistRepository(db)
    wishlist_item_repo = WishlistItemRepository(db)
    wishlist_result = await db.execute(select(Wishlist).filter(Wishlist.user_id == user_id))
    wishlist = wishlist_result.scalars().first()
    if wishlist:
        wishlist_items_result = await db.execute(select(WishlistItem).filter(WishlistItem.wishlist_id == wishlist.wishlist_id))
        wishlist_items = wishlist_items_result.scalars().all()
        for item in wishlist_items:
            await db.delete(item)
        await db.commit()

    # Send goodbye email
    if user and user.email:
        try:
            # await generate_email(user.email, 'We\x19re sorry to see you go', 'goodbye_account.html')
            pass
        except Exception:
            pass  # Email failure should not block deactivation
    return True, None
from backend.repositories.repository.refund_request_repository import RefundRequestRepository
from backend.persistance.refund_request import RefundRequest
from backend.persistance.enums import RefundRequestStatusEnum

import re
import datetime
import os
import shutil
from sqlalchemy.exc import SQLAlchemyError
from backend.persistance.user import User
from backend.persistance.enums import SellerStatusEnum
from backend.repositories.repository.user_repository import UserRepository
from backend.repositories.repository.cart_repository import CartRepository
from backend.repositories.repository.cart_item_repository import CartItemRepository
from backend.repositories.repository.product_repository import ProductRepository
from backend.repositories.repository.wishlist_repository import WishlistRepository
from backend.repositories.repository.wishlist_item_repository import WishlistItemRepository
from backend.persistance.cart import Cart
from backend.persistance.cart_item import CartItem
from backend.persistance.wishlist import Wishlist
from backend.persistance.wishlist_item import WishlistItem
from sqlalchemy import select
from backend.repositories.repository.user_finance_repository import UserFinanceRepository
from backend.persistance.user_finance import UserFinance
from backend.repositories.repository.customer_shipment_repository import CustomerShipmentRepository
from backend.persistance.customer_shipment import CustomerShipment
from backend.repositories.repository.product_variant_repository import ProductVariantRepository
from backend.repositories.repository.product_image_repository import ProductImageRepository
from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
from backend.persistance.order import Order
from backend.repositories.repository.order_repository import OrderRepository
from backend.persistance.order_item import OrderItem
from backend.repositories.repository.order_item_repository import OrderItemRepository
from backend.persistance.shipment import Shipment
from backend.repositories.repository.shipment_repository import ShipmentRepository
from backend.persistance.shipment_item import ShipmentItem
from backend.repositories.repository.shipment_item_repository import ShipmentItemRepository
from backend.persistance.shipment_event import ShipmentEvent
from backend.repositories.repository.shipment_event_repository import ShipmentEventRepository
from backend.persistance.product_rating import ProductRating
from backend.repositories.repository.product_rating_repository import ProductRatingRepository
    
import asyncio

async def handle_payment_info(purchase_data: dict, db: AsyncSession):
    payment_info = purchase_data.get('payment_info')
    save_payment_method = purchase_data.get('save_payment_method', False)
    if not payment_info:
        return None, False, 'Payment info required.'
    required_fields = ['user_id', 'payment_method_token', 'expiry_date', 'cardholder_name', 'billing_address']
    for field in required_fields:
        if not payment_info.get(field):
            return None, False, f'Missing required payment field: {field}'
    # PCI-DSS: Do not store CVV or PAN
    if 'cvv' in payment_info:
        del payment_info['cvv']
    if 'card_number' in payment_info:
        del payment_info['card_number']
    user_finance = None
    if save_payment_method:
        uf_repo = UserFinanceRepository(db)
        try:
            user_finance = UserFinance(**payment_info)
            db.add(user_finance)
            await db.commit()
            await db.refresh(user_finance)
        except Exception as e:
            await db.rollback()
            return None, False, f'Failed to save payment method: {str(e)}'
    return user_finance, True, None

async def handle_shipment_info(purchase_data: dict, db: AsyncSession):
    shipment_info = purchase_data.get('shipment_info')
    save_shipment = purchase_data.get('save_shipment', False)
    if not shipment_info:
        return None, False, 'Shipment info required.'
    required_fields = ['customer_id', 'postal_code', 'street_line_1', 'city', 'state_province', 'country']
    for field in required_fields:
        if not shipment_info.get(field):
            return None, False, f'Missing required shipment field: {field}'
    customer_shipment = None
    if save_shipment:
        cs_repo = CustomerShipmentRepository(db)
        try:
            customer_shipment = CustomerShipment(**shipment_info)
            db.add(customer_shipment)
            await db.commit()
            await db.refresh(customer_shipment)
        except Exception as e:
            await db.rollback()
            return None, False, f'Failed to save shipment info: {str(e)}'
    return customer_shipment, True, None

async def create_order_and_items(purchase_data: dict, db: AsyncSession, cart_items, total_amount):
    user_id = g.user['user_id']
    order_repo = OrderRepository(db)
    order_number = f"ORD{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
    # Extract address fields from purchase_data
    address = purchase_data.get('address')
    postal_code = purchase_data.get('postal_code')
    country = purchase_data.get('country')
    city = purchase_data.get('city')
    order = Order(
        order_id=None,
        user_id=user_id,
        cart_id=purchase_data.get('cart_id'),
        order_status='pending',
        total_amount=total_amount,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        order_number=order_number,
        address=address,
        postal_code=postal_code,
        country=country,
        city=city
    )
    try:
        order = await order_repo.save(order)
    except Exception as e:
        await db.rollback()
        return None, False, f'Order creation failed: {str(e)}'
    order_item_repo = OrderItemRepository(db)
    order_items = [
        OrderItem(
            order_item_id=None,
            order_id=order.order_id,
            product_id=item['product_id'],
            variant_id=item['variant_id'],
            quantity=item['quantity'],
            subtotal=item['subtotal']
        ) for item in cart_items
    ]
    try:
        await db.add_all(order_items)
        await db.commit()
    except Exception as e:
        await db.rollback()
        return None, False, f'Order item creation failed: {str(e)}'
    return order, order_items, True, None

async def deduct_inventory(order_items, db: AsyncSession):
    product_repo = ProductRepository(db)
    product_variant_repo = ProductVariantRepository(db)
    try:
        for oi in order_items:
            if oi.variant_id:
                affected = await product_variant_repo.decrement_stock(oi.variant_id, oi.quantity)
                if not affected:
                    return False, f'Not enough stock for variant {oi.variant_id}'
            else:
                affected = await product_repo.decrement_stock(oi.product_id, oi.quantity)
                if not affected:
                    return False, f'Not enough stock for product {oi.product_id}'
    except Exception as e:
        return False, f'Inventory deduction failed: {str(e)}'
    return True, None

async def empty_cart(cart_items, db: AsyncSession):
    try:
        for item in cart_items:
            await db.delete(item['db_obj'])
        await db.commit()
    except Exception as e:
        await db.rollback()
        return False, f'Failed to empty cart: {str(e)}'
    return True, None

async def sighnUp(user_data):
    full_name = user_data.get('full_name', None)
    dob = user_data.get('dob', None)
    password = user_data.get('password', None)
    phone_number = user_data.get('phone_number', None)
    email = user_data.get('email', None)
    created_at = datetime.date.today().replace(year=datetime.date.today().year)
    # Handle user image
    image = user_data.get('image', None)  # Expecting image file path or file-like object
    img_location = None
    if email and image:
        user_dir = os.path.join('images', 'user_images', email)
        os.makedirs(user_dir, exist_ok=True)
        ext = os.path.splitext(image)[1] if isinstance(image, str) else '.jpg'
        img_path = os.path.join(user_dir, f'profile{ext}')
        if isinstance(image, str):
            shutil.copy(image, img_path)
        else:
            with open(img_path, 'wb') as f:
                f.write(image.read())
        img_location = img_path
    else:
        img_location = None
    user_data['img_location'] = img_location
    account_status = user_data.get('account_status', True)
    user = User(
        user_id=None,  # Will be set by DB
        full_name=full_name,
        dob=dob,
        password=password,
        phone_number=phone_number,
        email=email,
        created_at=created_at,
        img_location=img_location,
        account_status=account_status
    )
    
    ur=UserRepository(None)
    await ur.add_user(user)
    # Send account creation email
    if email:
        # await generate_email(email, 'Your Divina Popina Account Has Been Created', 'account_created.html')
        pass
async def forgotPassword(user_Data):
    email = user_Data.get('email', None)
    exists=False
    password=""
    try:
        user=await UserRepository.get_by_email(email)
        if user is not None:
            user.password = user_Data.get('new_password', None)
            if hasattr(user, 'account_status') and user.account_status is False:
                user.account_status = True
                await UserRepository.set_user_for_update(user)
            exists = True
            # Send password reset email
                # await generate_email(email, 'Your Divina Popina Password Has Been Reset', 'password_reset.html')
        # Remove user function to send account removal email
        def removeUser(user_data):
            email = user_data.get('email', None)
            # Remove user image directory if exists
            if email:
                user_dir = os.path.join('images', 'user_images', email)
                if os.path.exists(user_dir):
                    shutil.rmtree(user_dir)
                # Send account removal email
                    # generate_email(email, 'Your Divina Popina Account Has Been Removed', 'account_removed.html')
        
    except Exception as e:
        exists=False
        
def updateUser(user_data):
    full_name = user_data.get('full_name', None)
    dob = user_data.get('dob', None)
    password = user_data.get('password', None)
    phone_number = user_data.get('phone_number', None)
    email = user_data.get('email', None)
    id = user_data.get('user_id', None)
    account_status = user_data.get('account_status', True)
    # Handle user image update
    image = user_data.get('image', None)
    img_location = None
    if email:
        user_dir = os.path.join('images', 'user_images', email)
        if image:
            os.makedirs(user_dir, exist_ok=True)
            ext = os.path.splitext(image)[1] if isinstance(image, str) else '.jpg'
            img_path = os.path.join(user_dir, f'profile{ext}')
            if isinstance(image, str):
                shutil.copy(image, img_path)
            else:
                with open(img_path, 'wb') as f:
                    f.write(image.read())
            img_location = img_path
        else:
            # Remove image if exists and no image provided
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
            img_location = None
        user_data['img_location'] = img_location
        email = user_data.get('email', None)
        if email:
            user_dir = os.path.join('images', 'user_images', email)
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
        ur = UserRepository(None)
        user = ur.get_by_id(id)
        if user:
            user.full_name = full_name
            user.dob = dob
            user.password = password
            user.phone_number = phone_number
            user.email = email
            user.img_location = img_location
            user.account_status = account_status
            ur.set_user_for_update(user)
    

from backend.repositories.repository.employee_repository import EmployeeRepository
from backend.repositories.repository.seller_snapshot_repository import SellerSnapshotRepository
from backend.persistance.employee import Employee
from backend.persistance.seller_snapshot import SellerSnapshot
from sqlalchemy.ext.asyncio import AsyncSession

async def sighnIn(user_data, db: AsyncSession = None):
    email = user_data.get('email', None)
    password = user_data.get('password', None)
    ur = UserRepository(db)
    user = await ur.get_by_email(email)
    if user and user.password == password:
        if hasattr(user, 'account_status') and user.account_status is False:
            user.account_status = True
            await ur.set_user_for_update(user)

        # Enrich user/session object
        session_obj = {
            'user_id': user.user_id,
            'full_name': user.full_name,
            'dob': user.dob,
            'phone_number': user.phone_number,
            'email': user.email,
            'img_location': user.img_location,
            'account_status': user.account_status,
        }

        # Check employee status
        emp_repo = EmployeeRepository(db)
        emp_res = await db.execute(select(Employee).filter(Employee.user_id == user.user_id))
        employee = emp_res.scalars().first()
        if employee:
            session_obj['isEmployee'] = True
            session_obj['department'] = getattr(employee, 'department_id', None)
            session_obj['job'] = getattr(employee, 'job', None) if hasattr(employee, 'job') else None
        else:
            session_obj['isEmployee'] = False
            session_obj['department'] = None
            session_obj['job'] = None

        # Check seller status
        seller_repo = SellerSnapshotRepository(db)
        seller_res = await db.execute(select(SellerSnapshot).filter(SellerSnapshot.contact_email == user.email))
        seller = seller_res.scalars().first()
        if seller:
            session_obj['isSeller'] = True
            session_obj['seller_store_name'] = getattr(seller, 'store_name', None)
            session_obj['seller_type'] = getattr(seller, 'seller_type', None)
        else:
            session_obj['isSeller'] = False
            session_obj['seller_store_name'] = None
            session_obj['seller_type'] = None

        return session_obj

def getUserById():
    user_id = g.user['user_id']
    ur=UserRepository(None)
    user=ur.get_by_id(user_id)
    return user
def removeUser(user_data):
    email = user_data.get('email', None)
    ur=UserRepository(None)
    user=ur.get_by_email(email)
    if user:
        ur.remove_user(user)
        # Remove user image directory if exists
        if email:
            user_dir = os.path.join('images', 'user_images', email)
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
            # Send account removal email
                # generate_email(email, 'Your Divina Popina Account Has Been Removed', 'account_removed.html')
def filterUserInfo(user_data):
        dob = user_data.get('dob', None)
        password = user_data.get('password', None)
        img_location =  user_data.get('img_location', None)
        # Check if img_location is a URL and exists
        if img_location and (img_location.startswith('http://') or img_location.startswith('https://')):
            import requests
            try:
                response = requests.head(img_location, allow_redirects=True, timeout=5)
                if response.status_code >= 400:
                    errors.append('Image URL does not exist or is not accessible.')
            except Exception:
                errors.append('Image URL does not exist or is not accessible.')
        errors=[]
        twelve_years_ago = datetime.date.today().replace(year=datetime.date.today().year - 12)
        if dob is not None:
            if isinstance(dob, str):
                try:
                    dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    errors.append("Invalid date format for dob. Use YYYY-MM-DD.")
            if isinstance(dob, datetime.date) and dob >= twelve_years_ago:
                errors.append("User must be at least 12 years old.")
        regex = r'^(?=[A-Za-z])(?=.[0-9])(?=.[!_#])(?=.[A-Z])(?=.[a-z]).+$'
        if password is not None:
            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")
            if not re.match(regex, password):
                errors.append("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character (!, _, #).")
        twelve_years_ago = datetime.date.today().replace(year=datetime.date.today().year - 12)
        if dob is not None:
            if isinstance(dob, str):
                try:
                    dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    errors.append("Invalid date format for dob. Use YYYY-MM-DD.")
            if isinstance(dob, datetime.date) and dob >= twelve_years_ago:
                errors.append("User must be at least 12 years old.")
        return errors

# Add item to cart
def add_item_to_cart(user_id: int, product_id: int, quantity: int, db, cart_id=None, variant_id=None):
    cart_repo = CartRepository(db)
    cart_item_repo = CartItemRepository(db)
    product_repo = ProductRepository(db)
    product = product_repo.get_by_id(product_id)
    if not product:
        raise ValueError('Product not found')
    if quantity > product.stock:
        quantity = product.stock
    cart = cart_repo.get_by_id(cart_id) if cart_id else None
    if not cart:
        cart = Cart(cart_id=None, user_id=user_id, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
        db.add(cart)
        db.commit()
        db.refresh(cart)
    cart_item = CartItem(cart_item_id=None, cart_id=cart.cart_id, product_id=product_id, variant_id=variant_id, quantity=quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

# Add item to wishlist
def add_item_to_wishlist(user_id: int, product_id: int, quantity: int, db, wishlist_id=None, variant_id=None):
    wishlist_repo = WishlistRepository(db)
    wishlist_item_repo = WishlistItemRepository(db)
    product_repo = ProductRepository(db)
    product = product_repo.get_by_id(product_id)
    if not product:
        raise ValueError('Product not found')
    if quantity > product.stock:
        quantity = product.stock
    wishlist = wishlist_repo.get_by_id(wishlist_id) if wishlist_id else None
    if not wishlist:
        wishlist = Wishlist(wishlist_id=None, user_id=user_id, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)
    wishlist_item = WishlistItem(wishlist_item_id=None, wishlist_id=wishlist.wishlist_id, product_id=product_id, variant_id=variant_id, quantity=quantity)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

# Get cart items with alerts
async def get_cart_items(db: AsyncSession, cart_id: Optional[int] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
    # Accept user_id as argument for FastAPI context
    if user_id is None:
        return {'items': [], 'notes': ['No user_id provided.'], 'time': str(datetime.datetime.now())}
    cart_repo = CartRepository(db)
    cart_item_repo = CartItemRepository(db)
    product_repo = ProductRepository(db)
    product_variant_repo = ProductVariantRepository(db)
    product_image_repo = ProductImageRepository(db)
    cart = await cart_repo.get_by_id(cart_id) if cart_id else None
    if not cart:
        return {'items': [], 'notes': ['No cart found for user.'], 'time': str(datetime.datetime.now())}
    items_res = await db.execute(select(CartItem).filter(CartItem.cart_id == cart.cart_id))
    items = items_res.scalars().all()
    notes = []
    result_items = []
    for item in items:
        product = await product_repo.get_by_id(item.product_id)
        if not product:
            notes.append(f"Product {item.product_id} removed from cart at {datetime.datetime.now()}.")
            await db.delete(item)
            await db.commit()
            continue
        # Get product images
        images = await product_image_repo.get_by_product_id(product.product_id)
        image_url = images[0].image_url if images else None
        # Get category/subcategory names if available
        category_name = getattr(product, 'category_id', None)
        subcategory_name = getattr(product, 'subcategory_id', None)
        # Variant info
        variant = None
        variant_name = None
        variant_image_url = None
        price = product.price
        if item.variant_id:
            variant = await product_variant_repo.get_by_id(item.variant_id)
            if variant:
                variant_name = getattr(variant, 'name', None)
                price = getattr(variant, 'price', price)
                # Try to get variant image
                from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
                variant_image_repo = ProductVariantImageRepository(db)
                variant_images = await variant_image_repo.get_by_variant_id(variant.variant_id)
                variant_image_url = variant_images[0].image_url if variant_images else None
        # Stock check
        if item.quantity > product.stock:
            notes.append(f"Product {item.product_id} quantity reduced to {product.stock} at {datetime.datetime.now()}.")
            item.quantity = product.stock
            await db.commit()
        result_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'product_image': image_url,
            'category': category_name,
            'subcategory': subcategory_name,
            'variant_id': item.variant_id,
            'variant_name': variant_name,
            'variant_image': variant_image_url,
            'price': price,
            'quantity': item.quantity
        })
    return {'items': result_items, 'notes': notes}

# Get wishlist items with alerts
async def get_wishlist_items(db: AsyncSession, wishlist_id: Optional[int] = None) -> Dict[str, Any]:
    user_id = g.user['user_id']
    wishlist_repo = WishlistRepository(db)
    wishlist_item_repo = WishlistItemRepository(db)
    product_repo = ProductRepository(db)
    product_variant_repo = ProductVariantRepository(db)
    product_image_repo = ProductImageRepository(db)
    wishlist = await wishlist_repo.get_by_id(wishlist_id) if wishlist_id else None
    if not wishlist:
        return {'items': [], 'notes': ['No wishlist found for user.'], 'time': str(datetime.datetime.now())}
    items_res = await db.execute(select(WishlistItem).filter(WishlistItem.wishlist_id == wishlist.wishlist_id))
    items = items_res.scalars().all()
    notes = []
    result_items = []
    for item in items:
        product = await product_repo.get_by_id(item.product_id)
        if not product:
            notes.append(f"Product {item.product_id} removed from wishlist at {datetime.datetime.now()}.")
            await db.delete(item)
            await db.commit()
            continue
        # Get product images
        images = await product_image_repo.get_by_product_id(product.product_id)
        image_url = images[0].image_url if images else None
        # Get category/subcategory names if available
        category_name = getattr(product, 'category_id', None)
        subcategory_name = getattr(product, 'subcategory_id', None)
        # Variant info
        variant = None
        variant_name = None
        variant_image_url = None
        price = product.price
        if item.variant_id:
            variant = await product_variant_repo.get_by_id(item.variant_id)
            if variant:
                variant_name = getattr(variant, 'name', None)
                price = getattr(variant, 'price', price)
                # Try to get variant image
                from backend.repositories.repository.product_variant_image_repository import ProductVariantImageRepository
                variant_image_repo = ProductVariantImageRepository(db)
                variant_images = await variant_image_repo.get_by_variant_id(variant.variant_id)
                variant_image_url = variant_images[0].image_url if variant_images else None
        # Stock check
        if item.quantity > product.stock:
            notes.append(f"Product {item.product_id} quantity reduced to {product.stock} at {datetime.datetime.now()}.")
            item.quantity = product.stock
            await db.commit()
        result_items.append({
            'product_id': item.product_id,
            'product_name': product.name,
            'product_image': image_url,
            'category': category_name,
            'subcategory': subcategory_name,
            'variant_id': item.variant_id,
            'variant_name': variant_name,
            'variant_image': variant_image_url,
            'price': price,
            'quantity': item.quantity
        })
    return {'items': result_items, 'notes': notes}

# Edit cart item quantity
async def edit_cart_item_quantity(cart_item_id: int, new_quantity: int, db: AsyncSession):
    cart_item_repo = CartItemRepository(db)
    product_repo = ProductRepository(db)
    item = cart_item_repo.get_by_id(cart_item_id)
    notes = []
    if not item:
        return {'notes': [f'Cart item {cart_item_id} not found at {datetime.datetime.now()}']}
    product = product_repo.get_by_id(item.product_id)
    if not product:
        db.delete(item)
        db.commit()
        notes.append(f'Product {item.product_id} removed from cart at {datetime.datetime.now()}')
        return {'notes': notes}
    if new_quantity > product.stock:
        item.quantity = product.stock
        db.commit()
        notes.append(f'Quantity for product {item.product_id} set to {product.stock} at {datetime.datetime.now()}')
    elif new_quantity <= 0:
        db.delete(item)
        db.commit()
        notes.append(f'Cart item {cart_item_id} removed at {datetime.datetime.now()}')
    else:
        item.quantity = new_quantity
        db.commit()
    return {'notes': notes}

# Edit wishlist item quantity
async def edit_wishlist_item_quantity(wishlist_item_id: int, new_quantity: int, db: AsyncSession):
    wishlist_item_repo = WishlistItemRepository(db)
    product_repo = ProductRepository(db)
    item = await wishlist_item_repo.get_by_id(wishlist_item_id)
    notes = []
    if not item:
        return {'notes': [f'Wishlist item {wishlist_item_id} not found at {datetime.datetime.now()}']}
    product = await product_repo.get_by_id(item.product_id)
    if not product:
        await db.delete(item)
        await db.commit()
        notes.append(f'Product {item.product_id} removed from wishlist at {datetime.datetime.now()}')
        return {'notes': notes}
    if new_quantity > product.stock:
        item.quantity = product.stock
        await db.commit()
        notes.append(f'Quantity for product {item.product_id} set to {product.stock} at {datetime.datetime.now()}')
    elif new_quantity <= 0:
        await db.delete(item)
        await db.commit()
        notes.append(f'Wishlist item {wishlist_item_id} removed at {datetime.datetime.now()}')
    else:
        item.quantity = new_quantity
        await db.commit()
    return {'notes': notes}

# Remove cart item
async def remove_cart_item(cart_item_id: int, db: AsyncSession):
    cart_item_repo = CartItemRepository(db)
    item = await cart_item_repo.get_by_id(cart_item_id)
    if item:
        await db.delete(item)
        await db.commit()

# Remove wishlist item
async def remove_wishlist_item(wishlist_item_id: int, db: AsyncSession):
    wishlist_item_repo = WishlistItemRepository(db)
    item = await wishlist_item_repo.get_by_id(wishlist_item_id)
    if item:
        await db.delete(item)
        await db.commit()

async def purchase(purchase_data):
    db = purchase_data.get('db')
    user_id = purchase_data.get('user_id')
    try:
        # 1. Handle payment info (PCI-DSS compliant)
        user_finance, ok, msg = await handle_payment_info(purchase_data, db)
        if not ok:
            return False, msg

        # 2. Handle shipment info
        customer_shipment, ok, msg = await handle_shipment_info(purchase_data, db)
        if not ok:
            return False, msg

        # 3. Validate cart and prepare order items
        cart_id = purchase_data.get('cart_id')
        cart_repo = CartRepository(db)
        cart_item_repo = CartItemRepository(db)
        product_repo = ProductRepository(db)
        product_variant_repo = ProductVariantRepository(db)
        cart = await cart_repo.get_by_id(cart_id)
        if not cart:
            return False, 'Cart not found.'
        cart_items_db = []
        # NOTE: This assumes async session and async query, update as needed for your ORM
        # cart_items_db = await db.execute(select(CartItem).filter_by(cart_id=cart_id))
        # cart_items_db = cart_items_db.scalars().all()
        # For now, fallback to sync if needed
        cart_items_db = await db.execute(select(CartItem).filter(CartItem.cart_id == cart_id))
        cart_items_db = cart_items_db.scalars().all()
        cart_items = []
        total_amount = 0
        for item in cart_items_db:
            product = await product_repo.get_by_id(item.product_id)
            if not product:
                await db.delete(item)
                continue
            if item.variant_id:
                variant = await product_variant_repo.get_by_id(item.variant_id)
                if not variant or variant.stock < item.quantity:
                    item.quantity = variant.stock if variant and variant.stock > 0 else 0
                if not variant or item.quantity == 0:
                    await db.delete(item)
                    continue
                price = variant.price
            else:
                if product.stock < item.quantity:
                    item.quantity = product.stock if product.stock > 0 else 0
                if item.quantity == 0:
                    await db.delete(item)
                    continue
                price = product.price
            subtotal = price * item.quantity
            total_amount += subtotal
            cart_items.append({
                'product_id': item.product_id,
                'variant_id': item.variant_id,
                'quantity': item.quantity,
                'subtotal': subtotal,
                'db_obj': item
            })
        if not cart_items:
            return False, 'No valid items in cart to purchase.'

        # 4. Create order and order items
        # Pass address fields from purchase_data (should be set by frontend)
        order, order_items, ok, msg = await create_order_and_items(purchase_data, db, cart_items, total_amount)
        if not ok:
            return False, msg

        # 5. Deduct inventory
        ok, msg = await deduct_inventory(order_items, db)
        if not ok:
            return False, msg

        # 6. Empty cart
        ok, msg = await empty_cart(cart_items, db)
        if not ok:
            return False, msg

        await db.commit()
        return True, 'Purchase succeeded.'
    except Exception as e:
        return False, f'Unexpected error: {str(e)}'
async def get_user_orders(db: AsyncSession) -> List[Order]:
    user_id = g.user['user_id']
    order_repo = OrderRepository(db)
    orders_res = await db.execute(select(Order).filter(Order.user_id == user_id))
    orders = orders_res.scalars().all()
    return orders

async def get_order_details(order_id: int, db: AsyncSession) -> Dict[str, Any]:
    order_item_repo = OrderItemRepository(db)
    shipment_repo = ShipmentRepository(db)
    shipment_item_repo = ShipmentItemRepository(db)
    order_items_res = await db.execute(select(OrderItem).filter(OrderItem.order_id == order_id))
    order_items = order_items_res.scalars().all()
    shipment_res = await db.execute(select(Shipment).filter(Shipment.order_id == order_id))
    shipment = shipment_res.scalars().first()
    shipment_items = []
    if shipment:
        shipment_items_res = await db.execute(select(ShipmentItem).filter(ShipmentItem.shipment_id == shipment.shipment_id))
        shipment_items = shipment_items_res.scalars().all()
    return {
        'order_items': order_items,
        'shipment': shipment,
        'shipment_items': shipment_items
    }
    
async def create_refund_request(order_id: int, order_item_ids: list[int], reason: str, db: AsyncSession):
    from datetime import datetime
    refund_repo = RefundRequestRepository(db)
    refund_request = RefundRequest(
        refund_request_id=None,
        order_id=order_id,
        order_item_ids=order_item_ids,
        reason=reason,
        status=RefundRequestStatusEnum.PENDING,
        date_of_request=datetime.now()
    )
    return await refund_repo.save(refund_request)

async def get_refund_status(refund_request_id: int, db: AsyncSession):
    refund_repo = RefundRequestRepository(db)
    return await refund_repo.get_by_id(refund_request_id)

async def rate_and_comment_product(product_id: int, rating: int, comment: str, db: AsyncSession):
    user_id = g.user['user_id']
    if not (1 <= rating <= 5):
        raise ValueError('Rating must be between 1 and 5')
    repo = ProductRatingRepository(db)
    product_rating = ProductRating(
        rating_id=None,
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
        created_at=datetime.datetime.now()
    )
    return await repo.save(product_rating)

def search_products(db, keywords=None, category_id=None, subcategory_id=None, min_price=None, max_price=None):
    from backend.models.model.product import Product
    from backend.repositories.repository.product_image_repository import ProductImageRepository
    base = select(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if subcategory_id:
        query = query.filter(Product.subcategory_id == subcategory_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    products = query.all()
    result = []
    keyword_set = set()
    if keywords:
        keyword_set = set(word.lower() for word in keywords.split())
    image_repo = ProductImageRepository(db)
    for product in products:
        matches = False
        text_fields = [product.name or '', product.description or '']
        if keyword_set:
            for field in text_fields:
                if any(kw in field.lower() for kw in keyword_set):
                    matches = True
                    break
        else:
            matches = True
        images = image_repo.get_by_product_id(product.product_id)
        if matches:
            result.append({'product': product, 'images': images})
    return result

