"""
Order Service
Manages order lifecycle, status transitions, and permissions
"""
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from Models.Order import Order, OrderStatus
from Models.Return import Return, ReturnStatus
from Models.OrderItem import OrderItem
from Repositories.OrderRepository import OrderRepository
from Repositories.ReturnRepository import ReturnRepository
from Repositories.OrderItemRepository import OrderItemRepository
from Services.SimpleInventoryService import SimpleInventoryService


class OrderService:
    """
    Order service handling order lifecycle and permissions.
    
    Responsibilities:
    - Order creation with inventory validation
    - Order status management with role-based permissions
    - Order cancellation (user before delivery)
    - Refund requests (user after delivery)
    - Inventory synchronization on status changes
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.return_repo = ReturnRepository(db)
        self.order_item_repo = OrderItemRepository(db)
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """
        Get all orders for a user with items.
        
        Args:
            user_id: User ID
            
        Returns:
            List of orders with order items
        """
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        orders = result.scalars().all()
        
        # Load items for each order
        for order in orders:
            item_result = await self.db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            order.items = item_result.scalars().all()
        
        return orders
    
    async def get_all_orders(self) -> List[Order]:
        """
        Get all orders (admin/customer_service only).
        
        Returns:
            List of all orders
        """
        result = await self.db.execute(
            select(Order).order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items."""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if order:
            item_result = await self.db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            order.items = item_result.scalars().all()
        
        return order
    
    async def cancel_order(self, order_id: int, user_id: int, reason: str = None):
        """
        Cancel order before delivery and release inventory.
        
        Args:
            order_id: Order ID
            user_id: User ID (for permission check)
            reason: Cancellation reason
            
        Raises:
            ValueError: If order not found, not owned by user, or already shipped
        """
        order = await self.get_order_by_id(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        if order.user_id != user_id:
            raise ValueError("Order does not belong to user")
        
        # Cannot cancel shipped or delivered orders
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("Cannot cancel shipped or delivered orders. Request refund instead.")
        
        # Cannot cancel already cancelled orders
        if order.status == OrderStatus.CANCELLED:
            raise ValueError("Order already cancelled")
        
        # Update status
        old_status = order.status
        order.status = OrderStatus.CANCELLED
        if reason:
            order.admin_notes = f"Cancelled by user: {reason}"
        order.updated_at = datetime.utcnow()
        
        # Release inventory
        from Repositories.ProductRepository import ProductRepository
        product_repo = ProductRepository(self.db)
        inventory_service = SimpleInventoryService(product_repo)
        
        for item in order.items:
            await inventory_service.release_stock(item.product_id, item.quantity)
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def request_refund(
        self, 
        order_id: int, 
        user_id: int, 
        items: List[Dict], 
        reason: str
    ) -> Return:
        """
        Request refund for delivered order.
        
        Args:
            order_id: Order ID
            user_id: User ID (for permission check)
            items: List of items to return [{"order_item_id": int, "quantity": int, "reason": str}]
            reason: Overall return reason
            
        Returns:
            Created return request
            
        Raises:
            ValueError: If order not found, not delivered, or not owned by user
        """
        order = await self.get_order_by_id(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        if order.user_id != user_id:
            raise ValueError("Order does not belong to user")
        
        # Can only request refund for delivered orders
        if order.status != OrderStatus.DELIVERED:
            raise ValueError("Can only request refund for delivered orders")
        
        # Check if return already exists
        existing_return = await self.db.execute(
            select(Return)
            .where(Return.order_id == order_id)
            .where(Return.status.in_([ReturnStatus.REQUESTED, ReturnStatus.APPROVED]))
        )
        if existing_return.scalar_one_or_none():
            raise ValueError("Return request already exists for this order")
        
        # Create return request
        return_request = Return(
            order_id=order_id,
            status=ReturnStatus.REQUESTED,
            reason=reason,
            return_items=items,
            requested_at=datetime.utcnow()
        )
        
        self.db.add(return_request)
        await self.db.commit()
        await self.db.refresh(return_request)
        
        return return_request
    
    async def update_order_status(
        self, 
        order_id: int, 
        new_status: str, 
        actor_role: str,
        notes: str = None
    ) -> Order:
        """
        Update order status (customer_service or transfer only).
        
        Args:
            order_id: Order ID
            new_status: New status value
            actor_role: Role of actor (must be customer_service or transfer)
            notes: Optional admin notes
            
        Returns:
            Updated order
            
        Raises:
            PermissionError: If actor role not authorized
            ValueError: If order not found or invalid status
        """
        # Permission check
        if actor_role not in ['customer_service', 'transfer', 'admin']:
            raise PermissionError("Only customer service, transfer, or admin can change order status")
        
        order = await self.get_order_by_id(order_id)
        
        if not order:
            raise ValueError("Order not found")
        
        # Validate status
        try:
            status_enum = OrderStatus(new_status)
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")
        
        old_status = order.status
        order.status = status_enum
        order.updated_at = datetime.utcnow()
        
        if notes:
            existing_notes = order.admin_notes or ""
            order.admin_notes = f"{existing_notes}\n[{datetime.utcnow()}] {notes}" if existing_notes else notes
        
        # Handle inventory changes based on status
        from Repositories.ProductRepository import ProductRepository
        product_repo = ProductRepository(self.db)
        inventory_service = SimpleInventoryService(product_repo)
        
        # When shipped: confirm the sale (inventory already reserved during order creation)
        if new_status == OrderStatus.SHIPPED.value and old_status != OrderStatus.SHIPPED:
            # Inventory already reduced during order creation, no action needed
            pass
        
        # When cancelled: release inventory
        if new_status == OrderStatus.CANCELLED.value and old_status != OrderStatus.CANCELLED:
            for item in order.items:
                await inventory_service.release_stock(item.product_id, item.quantity)
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
