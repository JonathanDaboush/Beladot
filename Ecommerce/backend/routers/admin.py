"""
Admin Routes
Admin can do ANYTHING and EVERYTHING in the system:
- User management (CRUD all users)
- Seller management (CRUD all sellers)
- Employee management (CRUD all employees)
- Order management (view, modify, cancel any order)
- Product management (CRUD all products)
- Inventory management (adjust stock, transfers)
- Payment management (refunds, adjustments)
- Schedule management (modify any schedule)
- Analytics (view all reports)
- System configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional

from database import get_db
from schemas import MessageResponse
from Services.UserService import UserService
from Services.SellerService import SellerService
from Services.ProductService import ProductService
from Services.OrderService import OrderService
from Services.InventoryService import InventoryService
from Services.PaymentService import PaymentService
from Services.SchedulingService import SchedulingService
from Services.PayrollService import PayrollService
from Services.AnalyticsService import AnalyticsService
from Utilities.auth import get_current_admin_user
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============================================================================
# USER MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.get("/users", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_users(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (Admin only)"""
    user_service = UserService(db)
    users = await user_service.get_all_users()
    return {"users": users}


@router.post("/users", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def create_user(
    data: dict,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new user (Admin only)"""
    user_service = UserService(db)
    user = await user_service.create_user(**data)
    return {"message": f"User {user.id} created successfully"}


@router.put("/users/{user_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_user(
    user_id: int,
    data: dict,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update any user (Admin only)"""
    user_service = UserService(db)
    await user_service.update_user(user_id, data)
    return {"message": f"User {user_id} updated successfully"}


@router.delete("/users/{user_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def delete_user(
    user_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete any user (Admin only)"""
    user_service = UserService(db)
    await user_service.delete_user(user_id)
    return {"message": f"User {user_id} deleted successfully"}


# ============================================================================
# SELLER MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.get("/sellers", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_sellers(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all sellers (Admin only)"""
    seller_service = SellerService(db)
    sellers = await seller_service.get_all_sellers()
    return {"sellers": sellers}


@router.delete("/sellers/{seller_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def delete_seller(
    seller_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete any seller (Admin only)"""
    seller_service = SellerService(db)
    await seller_service.delete_seller(seller_id)
    return {"message": f"Seller {seller_id} deleted successfully"}


# ============================================================================
# ORDER MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.get("/orders", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_orders(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders (Admin only)"""
    order_service = OrderService(db)
    orders = await order_service.get_all_orders()
    return {"orders": orders}


@router.put("/orders/{order_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_order(
    order_id: int,
    data: dict,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update any order (Admin only)"""
    order_service = OrderService(db)
    await order_service.update_order(order_id, data)
    return {"message": f"Order {order_id} updated successfully"}


@router.delete("/orders/{order_id}/cancel", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def cancel_order(
    order_id: int,
    reason: str,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel any order (Admin only)"""
    order_service = OrderService(db)
    await order_service.cancel_order(order_id, reason)
    return {"message": f"Order {order_id} cancelled"}


# ============================================================================
# PRODUCT MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.get("/products", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_products(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all products (Admin only)"""
    product_service = ProductService(db)
    products = await product_service.get_all_products()
    return {"products": products}


@router.put("/products/{product_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_product(
    product_id: int,
    data: dict,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update any product (Admin only)"""
    product_service = ProductService(db)
    await product_service.update_product(product_id, data)
    return {"message": f"Product {product_id} updated successfully"}


@router.delete("/products/{product_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def delete_product(
    product_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete any product (Admin only)"""
    product_service = ProductService(db)
    await product_service.delete_product(product_id)
    return {"message": f"Product {product_id} deleted successfully"}


# ============================================================================
# INVENTORY MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.put("/inventory/adjust", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def adjust_inventory(
    product_id: int,
    new_stock: int,
    reason: str,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Adjust inventory for any product (Admin only)"""
    inventory_service = InventoryService(db)
    await inventory_service.adjust_stock(product_id, new_stock, reason, current_admin.id)
    return {"message": f"Inventory adjusted for product {product_id}"}


# ============================================================================
# PAYMENT MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.post("/payments/refund/{payment_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def process_refund(
    payment_id: int,
    amount: float,
    reason: str,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Process refund for any payment (Admin only)"""
    payment_service = PaymentService(db)
    await payment_service.process_refund(payment_id, amount, reason, current_admin.id)
    return {"message": f"Refund processed for payment {payment_id}"}


# ============================================================================
# SCHEDULE MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.get("/schedules", dependencies=[Depends(rate_limiter_moderate)])
async def get_all_schedules(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all employee schedules (Admin only)"""
    scheduling_service = SchedulingService(db)
    schedules = await scheduling_service.get_schedules_by_date_range(start_date, end_date)
    return {"schedules": schedules}


@router.put("/schedules/{schedule_id}", response_model=MessageResponse, dependencies=[Depends(rate_limiter_moderate)])
async def update_schedule(
    schedule_id: int,
    data: dict,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update any employee schedule (Admin only)"""
    scheduling_service = SchedulingService(db)
    await scheduling_service.update_schedule(schedule_id, data)
    return {"message": f"Schedule {schedule_id} updated successfully"}


# ============================================================================
# PAYROLL MANAGEMENT (ADMIN FULL ACCESS)
# ============================================================================

@router.post("/payroll/calculate", dependencies=[Depends(rate_limiter_moderate)])
async def calculate_payroll(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate payroll for all employees (Admin only)"""
    payroll_service = PayrollService(db)
    results = await payroll_service.calculate_payroll(start_date, end_date)
    return {"payroll_results": results}


# ============================================================================
# ANALYTICS & REPORTS (ADMIN FULL ACCESS)
# ============================================================================

@router.get("/analytics/sales", dependencies=[Depends(rate_limiter_moderate)])
async def get_sales_analytics(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive sales analytics (Admin only)"""
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_sales_analytics(start_date, end_date)
    return {"analytics": analytics}


@router.get("/analytics/overview", dependencies=[Depends(rate_limiter_moderate)])
async def get_system_overview(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete system overview (Admin only)"""
    analytics_service = AnalyticsService(db)
    overview = await analytics_service.get_system_overview()
    return {"overview": overview}
