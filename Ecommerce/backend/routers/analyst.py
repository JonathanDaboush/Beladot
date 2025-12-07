"""
Analyst Router - Comprehensive Analytics & Reporting

Provides analysts with read-only access to all system metrics and analytics.
Similar to Amazon's internal analytics tools for data analysis teams.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, timedelta
from database import get_db
from Utilities.auth import get_current_user
from Models.User import User, UserRole
from Services.AnalyticsService import AnalyticsService


router = APIRouter(prefix="/analyst", tags=["Analyst Analytics"])


def get_current_analyst(current_user: User = Depends(get_current_user)) -> User:
    """Verify user has analyst or admin role"""
    if current_user.role not in [UserRole.ANALYST, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Analyst or Admin role required."
        )
    return current_user


# ==================== SALES & REVENUE ANALYTICS ====================

@router.get("/sales/analytics")
async def get_sales_analytics(
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive sales analytics for specified period.
    
    Returns:
    - Order counts (total, completed, pending, cancelled)
    - Revenue metrics (gross, net, refunds, AOV)
    - Units sold
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_sales_analytics(start_date, end_date)
    return result


@router.get("/system/overview")
async def get_system_overview(
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Get high-level system overview - executive dashboard KPIs.
    
    Returns:
    - Total orders, products, revenue
    - Active employees
    - Recent activity trends
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_system_overview()
    return result


@router.get("/revenue/report")
async def get_revenue_report(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Detailed revenue breakdown by payment method and status.
    
    Returns:
    - Gross/net revenue
    - Revenue by payment method
    - Refund totals
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_revenue_report(start_date, end_date)
    return result


@router.get("/expenses/report")
async def get_expense_report(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Expense report including payroll costs by department.
    
    Returns:
    - Total payroll costs
    - Hours paid by department
    - Employee counts
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_expense_report(start_date, end_date)
    return result


@router.get("/profit-loss/report")
async def get_profit_loss_report(
    start_date: date = Query(..., description="Start date for P&L"),
    end_date: date = Query(..., description="End date for P&L"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Profit & Loss statement for specified period.
    
    Returns:
    - Revenue vs expenses
    - Net profit
    - Profit margin percentage
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_profit_loss_report(start_date, end_date)
    return result


@router.get("/seller/{seller_id}/performance")
async def get_seller_performance(
    seller_id: int,
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Individual seller performance metrics.
    
    Returns:
    - Product counts
    - Sales volume
    - Revenue totals
    - Average order value
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_seller_performance(seller_id)
    return result


# ==================== PRODUCT ANALYTICS ====================

@router.get("/products/compare")
async def compare_products(
    product_ids: List[int] = Query(..., description="List of product IDs to compare"),
    start_date: date = Query(..., description="Start date for comparison"),
    end_date: date = Query(..., description="End date for comparison"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare performance of multiple products over time.
    Amazon-style product comparison.
    
    Useful for:
    - A/B testing product variations
    - Category winners analysis
    - Seasonal performance comparison
    
    Returns:
    - Units sold per product
    - Revenue per product
    - Winner identification
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.compare_products(product_ids, start_date, end_date)
    return result


@router.get("/products/{product_id}/performance-over-time")
async def get_product_performance_over_time(
    product_id: int,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    interval: str = Query("day", description="Time interval: day, week, or month"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Time-series analysis of product performance.
    Track sales trends like Amazon's sales graphs.
    
    Useful for:
    - Identifying seasonal trends
    - Measuring promotion effectiveness
    - Demand forecasting
    
    Returns:
    - Sales data grouped by time interval
    - Revenue trends
    - Order volume patterns
    """
    if interval not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Invalid interval. Use 'day', 'week', or 'month'")
    
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_product_performance_over_time(
        product_id, start_date, end_date, interval
    )
    return result


# ==================== INVENTORY & SUPPLY CHAIN ANALYTICS ====================

@router.get("/inventory/metrics")
async def get_inventory_metrics(
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Inventory analytics similar to AWS Supply Chain Analytics.
    
    Returns:
    - Stock levels across all products
    - Low stock alerts
    - Out of stock items
    - Total inventory value
    - Stockout predictions
    
    Useful for:
    - Identifying reorder needs
    - Inventory optimization
    - Supply chain planning
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_inventory_metrics()
    return result


# ==================== EMPLOYEE PRODUCTIVITY ANALYTICS ====================

@router.get("/employees/productivity")
async def get_employee_productivity(
    start_date: date = Query(..., description="Start date for productivity analysis"),
    end_date: date = Query(..., description="End date for productivity analysis"),
    department: Optional[str] = Query(None, description="Filter by department"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Employee productivity tracking similar to Amazon's warehouse metrics.
    
    Tracks:
    - Hours worked by department
    - Employee efficiency metrics
    - Approval rates
    - Department performance
    
    Returns:
    - Total hours by department
    - Average hours per employee
    - Approved vs pending hours
    - Employee counts
    
    Useful for:
    - Workforce optimization
    - Department capacity planning
    - Productivity benchmarking
    """
    analytics_service = AnalyticsService(db)
    result = await analytics_service.get_employee_productivity(
        start_date, end_date, department
    )
    return result


# ==================== QUICK REPORTS ====================

@router.get("/reports/daily-snapshot")
async def get_daily_snapshot(
    target_date: date = Query(default_factory=date.today, description="Date for snapshot"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick daily snapshot - today's key metrics at a glance.
    
    Returns same-day metrics for rapid decision making.
    """
    analytics_service = AnalyticsService(db)
    
    # Get today's sales
    sales = await analytics_service.get_sales_analytics(target_date, target_date)
    
    # Get inventory status
    inventory = await analytics_service.get_inventory_metrics()
    
    return {
        "date": target_date.isoformat(),
        "sales": sales,
        "inventory_alerts": {
            "low_stock_count": inventory["low_stock_count"],
            "out_of_stock_count": inventory["out_of_stock_count"]
        }
    }


@router.get("/reports/weekly-summary")
async def get_weekly_summary(
    week_start: date = Query(None, description="Start of week (defaults to current week)"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Weekly summary report - full week metrics.
    
    Defaults to current week (Monday-Sunday).
    """
    if not week_start:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=6)
    
    analytics_service = AnalyticsService(db)
    
    # Get week's sales
    sales = await analytics_service.get_sales_analytics(week_start, week_end)
    
    # Get week's expenses
    expenses = await analytics_service.get_expense_report(week_start, week_end)
    
    # Get week's P&L
    pl = await analytics_service.get_profit_loss_report(week_start, week_end)
    
    return {
        "week": {
            "start": week_start.isoformat(),
            "end": week_end.isoformat()
        },
        "sales": sales,
        "expenses": expenses,
        "profit_loss": pl
    }


@router.get("/reports/monthly-summary")
async def get_monthly_summary(
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_analyst: User = Depends(get_current_analyst),
    db: AsyncSession = Depends(get_db)
):
    """
    Monthly summary report - full month metrics.
    """
    from calendar import monthrange
    
    month_start = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    month_end = date(year, month, last_day)
    
    analytics_service = AnalyticsService(db)
    
    # Get month's sales
    sales = await analytics_service.get_sales_analytics(month_start, month_end)
    
    # Get month's revenue
    revenue = await analytics_service.get_revenue_report(month_start, month_end)
    
    # Get month's P&L
    pl = await analytics_service.get_profit_loss_report(month_start, month_end)
    
    return {
        "month": {
            "year": year,
            "month": month,
            "start": month_start.isoformat(),
            "end": month_end.isoformat()
        },
        "sales": sales,
        "revenue": revenue,
        "profit_loss": pl
    }
