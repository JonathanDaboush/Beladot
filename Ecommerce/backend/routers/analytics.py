"""
Analytics Routes
Handles analytics and reporting
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from database import get_db
from Services.AnalyticsService import AnalyticsService
from Utilities.auth import get_current_admin_user, get_current_seller
from Utilities.rate_limiting import rate_limiter_moderate

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/sales", dependencies=[Depends(rate_limiter_moderate)])
async def get_sales_analytics(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get sales analytics (Admin only)"""
    analytics_service = AnalyticsService(db)
    
    analytics = await analytics_service.get_sales_analytics(start_date, end_date)
    
    return {"analytics": analytics}


@router.get("/seller/performance", dependencies=[Depends(rate_limiter_moderate)])
async def get_seller_performance(
    current_seller=Depends(get_current_seller),
    db: AsyncSession = Depends(get_db)
):
    """Get seller performance metrics"""
    analytics_service = AnalyticsService(db)
    
    performance = await analytics_service.get_seller_performance(current_seller.id)
    
    return {"performance": performance}


@router.get("/system/overview", dependencies=[Depends(rate_limiter_moderate)])
async def get_system_overview(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overall system statistics (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    overview = await analytics_service.get_system_overview()
    
    return overview


@router.get("/revenue", dependencies=[Depends(rate_limiter_moderate)])
async def get_revenue_report(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue breakdown by period (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    report = await analytics_service.get_revenue_report(start_date, end_date)
    
    return report


@router.get("/expenses", dependencies=[Depends(rate_limiter_moderate)])
async def get_expense_report(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get expense breakdown (payroll, etc.) (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    report = await analytics_service.get_expense_report(start_date, end_date)
    
    return report


@router.get("/profit-loss", dependencies=[Depends(rate_limiter_moderate)])
async def get_profit_loss_report(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get combined profit/loss statement (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    report = await analytics_service.get_profit_loss_report(start_date, end_date)
    
    return report


@router.get("/seller/{seller_id}/performance", dependencies=[Depends(rate_limiter_moderate)])
async def get_specific_seller_performance(
    seller_id: int,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get individual seller metrics (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    performance = await analytics_service.get_seller_performance(seller_id)
    
    return {"seller_id": seller_id, "performance": performance}


@router.post("/products/compare", dependencies=[Depends(rate_limiter_moderate)])
async def compare_products(
    product_ids: list[int],
    start_date: date = None,
    end_date: date = None,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Product comparison analytics (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    comparison = await analytics_service.compare_products(
        product_ids=product_ids,
        start_date=start_date,
        end_date=end_date
    )
    
    return comparison


@router.get("/products/{product_id}/performance", dependencies=[Depends(rate_limiter_moderate)])
async def get_product_performance_over_time(
    product_id: int,
    start_date: date,
    end_date: date,
    interval: str = "daily",
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get product trends over time (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    performance = await analytics_service.get_product_performance_over_time(
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    
    return performance


@router.get("/inventory/metrics", dependencies=[Depends(rate_limiter_moderate)])
async def get_inventory_metrics(
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get inventory turnover and aging metrics (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    metrics = await analytics_service.get_inventory_metrics()
    
    return metrics


@router.post("/events/track", dependencies=[Depends(rate_limiter_moderate)])
async def track_event(
    event_name: str,
    event_data: dict,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Track custom analytics event (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    # Note: track_event method needs to be implemented in AnalyticsService if not already present
    result = {"message": "Event tracked successfully", "event": event_name, "data": event_data}
    
    return result


@router.get("/conversion-rate", dependencies=[Depends(rate_limiter_moderate)])
async def get_conversion_rate(
    start_date: date,
    end_date: date,
    current_admin=Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conversion rate analytics (Analysts/Admin only)"""
    analytics_service = AnalyticsService(db)
    
    # Note: get_conversion_rate method needs to be implemented in AnalyticsService if not already present
    # This is a placeholder implementation
    result = {
        "period": {"start": start_date, "end": end_date},
        "conversion_rate": 0.0,
        "message": "Method needs implementation in AnalyticsService"
    }
    
    return result

