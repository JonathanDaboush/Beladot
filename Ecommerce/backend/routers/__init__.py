"""
API Routers
All application routers organized by functionality
"""

# Import all routers for easy access
from . import (
    # Core e-commerce
    auth,
    cart,
    cart_extended,
    products,
    orders,
    checkout,
    checkout_extended,
    payments,
    payments_extended,
    payment_methods,
    shipping,
    search,
    
    # Seller functionality
    seller,
    seller_extended,
    
    # Internal operations
    customer_service,
    transfer,
    
    # Finance & payroll
    finance,
    payroll,
    payroll_extended,
    
    # Scheduling & time tracking
    scheduling,
    scheduling_extended,
    leave,
    manager,
    manager_approvals,
    employee,
    
    # Analytics & reporting
    analytics,
    analyst,
    
    # Administration
    admin,
)

__all__ = [
    "auth",
    "cart",
    "cart_extended",
    "products",
    "orders",
    "checkout",
    "checkout_extended",
    "payments",
    "payments_extended",
    "payment_methods",
    "shipping",
    "search",
    "seller",
    "seller_extended",
    "customer_service",
    "transfer",
    "finance",
    "payroll",
    "payroll_extended",
    "scheduling",
    "scheduling_extended",
    "leave",
    "manager",
    "manager_approvals",
    "employee",
    "analytics",
    "analyst",
    "admin",
]
