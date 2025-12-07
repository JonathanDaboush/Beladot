from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_, or_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession
from Models.Order import Order, OrderStatus
from Models.OrderItem import OrderItem
from Models.Product import Product
from Models.ProductVariant import ProductVariant
from Models.Seller import Seller
from Models.Employee import Employee
from Models.HoursWorked import HoursWorked
from Models.EmployeeSchedule import EmployeeSchedule
from Models.Payment import Payment
from Models.Refund import Refund
"""
Analytics Service - Business Intelligence
=========================================

Provides analytics and reporting for business metrics.

Business rules enforced at service layer

Dependencies:
- ReportRepository
    - MetricsCalculator

Author: Jonathan Daboush
Version: 2.0.0
"""



class AnalyticsService:
    """
    Comprehensive Analytics Service
    
    Amazon-style analytics covering:
    - Sales & revenue analytics
    - Product performance & comparison
    - Inventory & supply chain metrics
    - Customer behavior & marketplace analytics
    - Employee productivity tracking
    - Financial reporting
    - Demand forecasting
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== SALES & REVENUE ANALYTICS ====================
    
    async def get_sales_analytics(self, start_date: date, end_date: date) -> Dict:
        """
        Comprehensive sales analytics for the specified period.
        Similar to Amazon's seller central analytics.
        """
        # Get all orders in date range
        stmt = select(Order).where(
            and_(
                Order.created_at >= datetime.combine(start_date, datetime.min.time()),
                Order.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
        result = await self.db.execute(stmt)
        orders = result.scalars().all()
        
        # Calculate metrics
        total_orders = len(orders)
        completed_orders = [o for o in orders if o.status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]]
        pending_orders = [o for o in orders if o.status == OrderStatus.PENDING]
        cancelled_orders = [o for o in orders if o.status == OrderStatus.CANCELLED]
        
        total_revenue = sum(o.final_amount_cents for o in completed_orders) / 100
        total_refunds = sum(o.refund_amount_cents or 0 for o in orders) / 100
        net_revenue = total_revenue - total_refunds
        
        # Average order value
        aov = total_revenue / len(completed_orders) if completed_orders else 0
        
        # Get order items for product analysis
        order_ids = [o.id for o in orders]
        if order_ids:
            items_stmt = select(OrderItem).where(OrderItem.order_id.in_(order_ids))
            items_result = await self.db.execute(items_stmt)
            order_items = items_result.scalars().all()
            
            total_units_sold = sum(item.quantity for item in order_items)
        else:
            total_units_sold = 0
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "orders": {
                "total": total_orders,
                "completed": len(completed_orders),
                "pending": len(pending_orders),
                "cancelled": len(cancelled_orders),
                "completion_rate": len(completed_orders) / total_orders if total_orders else 0
            },
            "revenue": {
                "gross_revenue": round(total_revenue, 2),
                "refunds": round(total_refunds, 2),
                "net_revenue": round(net_revenue, 2),
                "average_order_value": round(aov, 2)
            },
            "products": {
                "total_units_sold": total_units_sold
            }
        }
    
    async def get_system_overview(self) -> Dict:
        """
        Complete system overview - high-level KPIs.
        Similar to Amazon's executive dashboard.
        """
        # Today's stats
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Order counts
        total_orders_stmt = select(func.count(Order.id))
        total_orders_result = await self.db.execute(total_orders_stmt)
        total_orders = total_orders_result.scalar()
        
        # Active products
        active_products_stmt = select(func.count(Product.id)).where(Product.is_active == True)
        active_products_result = await self.db.execute(active_products_stmt)
        active_products = active_products_result.scalar()
        
        # Total revenue (all time completed orders)
        revenue_stmt = select(func.sum(Order.final_amount_cents)).where(
            Order.status.in_([OrderStatus.DELIVERED, OrderStatus.SHIPPED])
        )
        revenue_result = await self.db.execute(revenue_stmt)
        total_revenue_cents = revenue_result.scalar() or 0
        
        # Active employees
        active_employees_stmt = select(func.count(Employee.id)).where(Employee.is_active == True)
        active_employees_result = await self.db.execute(active_employees_stmt)
        active_employees = active_employees_result.scalar()
        
        # Recent trends (last 7 days)
        recent_orders_stmt = select(func.count(Order.id)).where(
            Order.created_at >= datetime.combine(week_ago, datetime.min.time())
        )
        recent_orders_result = await self.db.execute(recent_orders_stmt)
        recent_orders = recent_orders_result.scalar()
        
        return {
            "snapshot_date": today.isoformat(),
            "totals": {
                "total_orders": total_orders,
                "active_products": active_products,
                "lifetime_revenue": round(total_revenue_cents / 100, 2),
                "active_employees": active_employees
            },
            "recent_activity": {
                "orders_last_7_days": recent_orders
            }
        }
    
    async def get_revenue_report(self, start_date: date, end_date: date) -> Dict:
        """
        Detailed revenue breakdown by payment method, status, etc.
        """
        # Get payments in date range
        stmt = select(Payment).where(
            and_(
                Payment.created_at >= datetime.combine(start_date, datetime.min.time()),
                Payment.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
        result = await self.db.execute(stmt)
        payments = result.scalars().all()
        
        # Get refunds
        refund_stmt = select(Refund).where(
            and_(
                Refund.created_at >= datetime.combine(start_date, datetime.min.time()),
                Refund.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
        refund_result = await self.db.execute(refund_stmt)
        refunds = refund_result.scalars().all()
        
        # Calculate revenue by payment method
        by_method = {}
        for payment in payments:
            method = payment.payment_method or "unknown"
            if method not in by_method:
                by_method[method] = {"count": 0, "total_cents": 0}
            by_method[method]["count"] += 1
            by_method[method]["total_cents"] += payment.amount_cents
        
        # Format by method
        revenue_by_method = {
            method: {
                "count": data["count"],
                "total": round(data["total_cents"] / 100, 2)
            }
            for method, data in by_method.items()
        }
        
        total_revenue = sum(p.amount_cents for p in payments) / 100
        total_refunded = sum(r.amount_cents for r in refunds) / 100
        net_revenue = total_revenue - total_refunded
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "revenue": {
                "gross_revenue": round(total_revenue, 2),
                "total_refunded": round(total_refunded, 2),
                "net_revenue": round(net_revenue, 2),
                "total_payments": len(payments)
            },
            "by_payment_method": revenue_by_method
        }
    
    async def get_expense_report(self, start_date: date, end_date: date) -> Dict:
        """
        Expense report including payroll costs.
        """
        # Get approved hours in date range
        stmt = select(HoursWorked).where(
            and_(
                HoursWorked.date >= start_date,
                HoursWorked.date <= end_date,
                HoursWorked.approval_status == "approved"
            )
        )
        result = await self.db.execute(stmt)
        hours_worked = result.scalars().all()
        
        # Get employee details for pay calculation
        employee_ids = list(set(h.employee_id for h in hours_worked))
        if employee_ids:
            employees_stmt = select(Employee).where(Employee.id.in_(employee_ids))
            employees_result = await self.db.execute(employees_stmt)
            employees = {e.id: e for e in employees_result.scalars().all()}
        else:
            employees = {}
        
        total_payroll = 0
        hours_breakdown = {}
        
        for hour_record in hours_worked:
            employee = employees.get(hour_record.employee_id)
            if not employee:
                continue
            
            # Get financial info (would need to join with EmployeeFinancial)
            # For now, estimate based on hours
            regular_hours = hour_record.regular_hours or 0
            overtime_hours = hour_record.overtime_hours or 0
            
            # Placeholder calculation (would use actual wage rates)
            estimated_cost = (regular_hours * 20) + (overtime_hours * 30)  # Example rates
            total_payroll += estimated_cost
            
            dept = employee.department
            if dept not in hours_breakdown:
                hours_breakdown[dept] = {"hours": 0, "estimated_cost": 0}
            hours_breakdown[dept]["hours"] += regular_hours + overtime_hours
            hours_breakdown[dept]["estimated_cost"] += estimated_cost
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "payroll": {
                "total_estimated_cost": round(total_payroll, 2),
                "total_hours_paid": sum(d["hours"] for d in hours_breakdown.values()),
                "employees_paid": len(employee_ids)
            },
            "by_department": hours_breakdown
        }
    
    async def get_profit_loss_report(self, start_date: date, end_date: date) -> Dict:
        """
        Profit & Loss statement.
        """
        revenue_data = await self.get_revenue_report(start_date, end_date)
        expense_data = await self.get_expense_report(start_date, end_date)
        
        revenue = revenue_data["revenue"]["net_revenue"]
        expenses = expense_data["payroll"]["total_estimated_cost"]
        profit = revenue - expenses
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "revenue": revenue,
            "expenses": expenses,
            "net_profit": round(profit, 2),
            "profit_margin_percent": round(profit_margin, 2)
        }
    
    async def get_seller_performance(self, seller_id: int) -> Dict:
        """
        Individual seller performance metrics.
        """
        # Get seller's products
        products_stmt = select(Product).where(Product.seller_id == seller_id)
        products_result = await self.db.execute(products_stmt)
        products = products_result.scalars().all()
        product_ids = [p.id for p in products]
        
        if not product_ids:
            return {
                "seller_id": seller_id,
                "products": {"total": 0},
                "sales": {"total_orders": 0, "total_revenue": 0}
            }
        
        # Get order items for these products
        items_stmt = select(OrderItem).where(OrderItem.product_id.in_(product_ids))
        items_result = await self.db.execute(items_stmt)
        order_items = items_result.scalars().all()
        
        # Get completed orders
        order_ids = list(set(item.order_id for item in order_items))
        if order_ids:
            orders_stmt = select(Order).where(
                and_(
                    Order.id.in_(order_ids),
                    Order.status.in_([OrderStatus.DELIVERED, OrderStatus.SHIPPED])
                )
            )
            orders_result = await self.db.execute(orders_stmt)
            completed_orders = orders_result.scalars().all()
        else:
            completed_orders = []
        
        # Calculate totals
        total_units_sold = sum(item.quantity for item in order_items)
        total_revenue = sum(
            item.price_cents * item.quantity for item in order_items
            if any(o.id == item.order_id for o in completed_orders)
        ) / 100
        
        return {
            "seller_id": seller_id,
            "products": {
                "total": len(products),
                "active": len([p for p in products if p.is_active])
            },
            "sales": {
                "total_orders": len(completed_orders),
                "total_units_sold": total_units_sold,
                "total_revenue": round(total_revenue, 2),
                "average_order_value": round(total_revenue / len(completed_orders), 2) if completed_orders else 0
            }
        }
    
    # ==================== PRODUCT ANALYTICS ====================
    
    async def compare_products(
        self,
        product_ids: List[int],
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Compare performance of multiple products over time.
        Amazon-style product comparison analytics.
        """
        comparisons = []
        
        for product_id in product_ids:
            # Get product
            product_stmt = select(Product).where(Product.id == product_id)
            product_result = await self.db.execute(product_stmt)
            product = product_result.scalar_one_or_none()
            
            if not product:
                continue
            
            # Get order items
            items_stmt = select(OrderItem).join(Order).where(
                and_(
                    OrderItem.product_id == product_id,
                    Order.created_at >= datetime.combine(start_date, datetime.min.time()),
                    Order.created_at <= datetime.combine(end_date, datetime.max.time()),
                    Order.status.in_([OrderStatus.DELIVERED, OrderStatus.SHIPPED])
                )
            )
            items_result = await self.db.execute(items_stmt)
            order_items = items_result.scalars().all()
            
            units_sold = sum(item.quantity for item in order_items)
            revenue = sum(item.price_cents * item.quantity for item in order_items) / 100
            orders_count = len(set(item.order_id for item in order_items))
            
            comparisons.append({
                "product_id": product_id,
                "product_name": product.name,
                "units_sold": units_sold,
                "revenue": round(revenue, 2),
                "orders": orders_count,
                "average_price": round(revenue / units_sold, 2) if units_sold > 0 else 0
            })
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "products": comparisons,
            "winner": max(comparisons, key=lambda x: x["revenue"]) if comparisons else None
        }
    
    async def get_product_performance_over_time(
        self,
        product_id: int,
        start_date: date,
        end_date: date,
        interval: str = "day"  # day, week, month
    ) -> Dict:
        """
        Time-series analysis of product performance.
        Track sales trends over time like Amazon's sales graphs.
        """
        # Get all order items for this product
        items_stmt = select(OrderItem, Order).join(Order).where(
            and_(
                OrderItem.product_id == product_id,
                Order.created_at >= datetime.combine(start_date, datetime.min.time()),
                Order.created_at <= datetime.combine(end_date, datetime.max.time()),
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.SHIPPED])
            )
        )
        items_result = await self.db.execute(items_stmt)
        items_with_orders = items_result.all()
        
        # Group by time interval
        time_series = {}
        
        for item, order in items_with_orders:
            order_date = order.created_at.date()
            
            # Determine bucket based on interval
            if interval == "day":
                bucket = order_date.isoformat()
            elif interval == "week":
                week_start = order_date - timedelta(days=order_date.weekday())
                bucket = week_start.isoformat()
            elif interval == "month":
                bucket = order_date.strftime("%Y-%m")
            else:
                bucket = order_date.isoformat()
            
            if bucket not in time_series:
                time_series[bucket] = {"units": 0, "revenue": 0, "orders": set()}
            
            time_series[bucket]["units"] += item.quantity
            time_series[bucket]["revenue"] += (item.price_cents * item.quantity) / 100
            time_series[bucket]["orders"].add(order.id)
        
        # Format output
        formatted_series = [
            {
                "period": period,
                "units_sold": data["units"],
                "revenue": round(data["revenue"], 2),
                "order_count": len(data["orders"])
            }
            for period, data in sorted(time_series.items())
        ]
        
        return {
            "product_id": product_id,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "interval": interval,
            "time_series": formatted_series
        }
    
    # ==================== INVENTORY & SUPPLY CHAIN ANALYTICS ====================
    
    async def get_inventory_metrics(self) -> Dict:
        """
        Inventory analytics similar to AWS Supply Chain Analytics.
        Stock levels, turnover, stockout predictions.
        """
        # Get all active products
        products_stmt = select(Product).where(Product.is_active == True)
        products_result = await self.db.execute(products_stmt)
        products = products_result.scalars().all()
        
        total_products = len(products)
        low_stock = [p for p in products if p.stock_quantity < 10]
        out_of_stock = [p for p in products if p.stock_quantity == 0]
        
        total_inventory_value = sum(
            (p.price_cents * p.stock_quantity) / 100 for p in products
        )
        
        return {
            "total_products": total_products,
            "low_stock_count": len(low_stock),
            "out_of_stock_count": len(out_of_stock),
            "total_inventory_value": round(total_inventory_value, 2),
            "low_stock_products": [
                {"id": p.id, "name": p.name, "stock": p.stock_quantity}
                for p in low_stock[:10]  # Top 10
            ]
        }
    
    # ==================== EMPLOYEE PRODUCTIVITY ANALYTICS ====================
    
    async def get_employee_productivity(
        self,
        start_date: date,
        end_date: date,
        department: Optional[str] = None
    ) -> Dict:
        """
        Employee productivity tracking similar to Amazon's warehouse metrics.
        Tracks hours worked, efficiency, and performance by department.
        """
        # Get hours worked
        stmt = select(HoursWorked).where(
            and_(
                HoursWorked.date >= start_date,
                HoursWorked.date <= end_date
            )
        )
        result = await self.db.execute(stmt)
        hours_records = result.scalars().all()
        
        # Get employees
        employee_ids = list(set(h.employee_id for h in hours_records))
        if employee_ids:
            employees_stmt = select(Employee).where(Employee.id.in_(employee_ids))
            employees_result = await self.db.execute(employees_stmt)
            employees = {e.id: e for e in employees_result.scalars().all()}
        else:
            employees = {}
        
        # Filter by department if specified
        if department:
            hours_records = [
                h for h in hours_records
                if employees.get(h.employee_id) and employees[h.employee_id].department == department
            ]
        
        # Calculate metrics
        by_department = {}
        
        for hour_record in hours_records:
            employee = employees.get(hour_record.employee_id)
            if not employee:
                continue
            
            dept = employee.department
            if dept not in by_department:
                by_department[dept] = {
                    "total_hours": 0,
                    "employees": set(),
                    "approved_hours": 0,
                    "pending_hours": 0
                }
            
            total_hours = (hour_record.regular_hours or 0) + (hour_record.overtime_hours or 0)
            by_department[dept]["total_hours"] += total_hours
            by_department[dept]["employees"].add(employee.id)
            
            if hour_record.approval_status == "approved":
                by_department[dept]["approved_hours"] += total_hours
            elif hour_record.approval_status == "pending":
                by_department[dept]["pending_hours"] += total_hours
        
        # Format output
        department_metrics = [
            {
                "department": dept,
                "total_hours": round(data["total_hours"], 2),
                "employee_count": len(data["employees"]),
                "avg_hours_per_employee": round(data["total_hours"] / len(data["employees"]), 2) if data["employees"] else 0,
                "approved_hours": round(data["approved_hours"], 2),
                "pending_hours": round(data["pending_hours"], 2)
            }
            for dept, data in by_department.items()
        ]
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "by_department": department_metrics,
            "summary": {
                "total_hours": sum(d["total_hours"] for d in department_metrics),
                "total_employees": len(employee_ids)
            }
        }
    
    # ==================== LEGACY METHODS (kept for compatibility) ====================
    
    def track_event(self, user_id: UUID | None, session_id: str | None, event: str, properties: dict) -> None:
        """Legacy event tracking - kept for compatibility"""
        pass
    
    def get_conversion_rate(self, user_id: UUID, start: date, end: date) -> float:
        """Legacy conversion rate - kept for compatibility"""
        return 0.0