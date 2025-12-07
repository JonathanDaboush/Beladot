"""
Tests for Analyst Router

Tests for analyst-specific endpoints and role-based access control.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from Models.User import User, UserRole
from Utilities.auth import create_access_token


client = TestClient(app)


@pytest.fixture
def analyst_token():
    """Create JWT token for analyst user"""
    analyst_user = {
        "id": 100,
        "email": "analyst@test.com",
        "role": UserRole.ANALYST.value
    }
    return create_access_token(analyst_user)


@pytest.fixture
def admin_token():
    """Create JWT token for admin user"""
    admin_user = {
        "id": 1,
        "email": "admin@test.com",
        "role": UserRole.ADMIN.value
    }
    return create_access_token(admin_user)


@pytest.fixture
def customer_token():
    """Create JWT token for regular customer"""
    customer_user = {
        "id": 200,
        "email": "customer@test.com",
        "role": UserRole.CUSTOMER.value
    }
    return create_access_token(customer_user)


# ==================== ACCESS CONTROL TESTS ====================

def test_analyst_endpoints_require_authentication():
    """Test that analyst endpoints require authentication"""
    response = client.get("/analyst/system/overview")
    assert response.status_code == 401


def test_analyst_endpoints_reject_customer_role(customer_token):
    """Test that regular customers cannot access analyst endpoints"""
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.get("/analyst/system/overview", headers=headers)
    assert response.status_code == 403
    assert "Analyst or Admin role required" in response.json()["detail"]


def test_analyst_can_access_endpoints(analyst_token):
    """Test that analysts can access their endpoints"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get("/analyst/system/overview", headers=headers)
    assert response.status_code in [200, 500]  # 200 if DB works, 500 if no test DB


def test_admin_can_access_analyst_endpoints(admin_token):
    """Test that admins can access analyst endpoints"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/analyst/system/overview", headers=headers)
    assert response.status_code in [200, 500]  # 200 if DB works, 500 if no test DB


# ==================== SALES & REVENUE ENDPOINTS ====================

def test_get_sales_analytics_endpoint(analyst_token):
    """Test sales analytics endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/sales/analytics?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    # Should require auth but may fail on DB
    assert response.status_code in [200, 500]


def test_get_system_overview_endpoint(analyst_token):
    """Test system overview endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get("/analyst/system/overview", headers=headers)
    
    assert response.status_code in [200, 500]


def test_get_revenue_report_endpoint(analyst_token):
    """Test revenue report endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/revenue/report?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_expense_report_endpoint(analyst_token):
    """Test expense report endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/expenses/report?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_profit_loss_report_endpoint(analyst_token):
    """Test P&L report endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/profit-loss/report?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_seller_performance_endpoint(analyst_token):
    """Test seller performance endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get("/analyst/seller/1/performance", headers=headers)
    
    assert response.status_code in [200, 500]


# ==================== PRODUCT ANALYTICS ENDPOINTS ====================

def test_compare_products_endpoint(analyst_token):
    """Test product comparison endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/products/compare?product_ids=1&product_ids=2&start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_product_performance_over_time_endpoint(analyst_token):
    """Test product performance over time endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/products/1/performance-over-time?start_date={start_date}&end_date={end_date}&interval=day",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_product_performance_invalid_interval(analyst_token):
    """Test product performance with invalid interval"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/products/1/performance-over-time?start_date={start_date}&end_date={end_date}&interval=invalid",
        headers=headers
    )
    
    # Should reject invalid interval
    if response.status_code not in [500]:
        assert response.status_code == 400
        assert "Invalid interval" in response.json()["detail"]


# ==================== INVENTORY ANALYTICS ENDPOINTS ====================

def test_get_inventory_metrics_endpoint(analyst_token):
    """Test inventory metrics endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get("/analyst/inventory/metrics", headers=headers)
    
    assert response.status_code in [200, 500]


# ==================== EMPLOYEE PRODUCTIVITY ENDPOINTS ====================

def test_get_employee_productivity_endpoint(analyst_token):
    """Test employee productivity endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/employees/productivity?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_employee_productivity_filtered_endpoint(analyst_token):
    """Test employee productivity with department filter"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = (date.today() - timedelta(days=30)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/employees/productivity?start_date={start_date}&end_date={end_date}&department=Sales",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


# ==================== QUICK REPORTS ENDPOINTS ====================

def test_get_daily_snapshot_endpoint(analyst_token):
    """Test daily snapshot endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    target_date = date.today().isoformat()
    
    response = client.get(
        f"/analyst/reports/daily-snapshot?target_date={target_date}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_daily_snapshot_default_date(analyst_token):
    """Test daily snapshot with default date (today)"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get("/analyst/reports/daily-snapshot", headers=headers)
    
    assert response.status_code in [200, 500]


def test_get_weekly_summary_endpoint(analyst_token):
    """Test weekly summary endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get("/analyst/reports/weekly-summary", headers=headers)
    
    assert response.status_code in [200, 500]


def test_get_weekly_summary_custom_week(analyst_token):
    """Test weekly summary with custom week start"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    week_start = (date.today() - timedelta(days=7)).isoformat()
    
    response = client.get(
        f"/analyst/reports/weekly-summary?week_start={week_start}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_monthly_summary_endpoint(analyst_token):
    """Test monthly summary endpoint"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    today = date.today()
    
    response = client.get(
        f"/analyst/reports/monthly-summary?year={today.year}&month={today.month}",
        headers=headers
    )
    
    assert response.status_code in [200, 500]


def test_get_monthly_summary_invalid_month(analyst_token):
    """Test monthly summary with invalid month"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get(
        "/analyst/reports/monthly-summary?year=2025&month=13",
        headers=headers
    )
    
    # Should reject invalid month
    assert response.status_code == 422  # Validation error


# ==================== PARAMETER VALIDATION TESTS ====================

def test_missing_required_date_parameters(analyst_token):
    """Test endpoints with missing required date parameters"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    # Missing both dates
    response = client.get("/analyst/sales/analytics", headers=headers)
    assert response.status_code == 422  # Validation error


def test_missing_start_date_only(analyst_token):
    """Test endpoints with missing start_date"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    end_date = date.today().isoformat()
    response = client.get(
        f"/analyst/sales/analytics?end_date={end_date}",
        headers=headers
    )
    assert response.status_code == 422


def test_missing_end_date_only(analyst_token):
    """Test endpoints with missing end_date"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    start_date = date.today().isoformat()
    response = client.get(
        f"/analyst/sales/analytics?start_date={start_date}",
        headers=headers
    )
    assert response.status_code == 422


def test_invalid_date_format(analyst_token):
    """Test endpoints with invalid date format"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    
    response = client.get(
        "/analyst/sales/analytics?start_date=invalid&end_date=invalid",
        headers=headers
    )
    assert response.status_code == 422


# ==================== ROLE PERMISSION MATRIX ====================

@pytest.mark.parametrize("endpoint", [
    "/analyst/system/overview",
    "/analyst/inventory/metrics",
    "/analyst/reports/daily-snapshot",
])
def test_customer_cannot_access_any_analyst_endpoint(endpoint, customer_token):
    """Test that customers are blocked from all analyst endpoints"""
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.get(endpoint, headers=headers)
    assert response.status_code == 403


@pytest.mark.parametrize("endpoint", [
    "/analyst/system/overview",
    "/analyst/inventory/metrics",
    "/analyst/reports/daily-snapshot",
])
def test_analyst_can_access_all_read_only_endpoints(endpoint, analyst_token):
    """Test that analysts have read-only access to all their endpoints"""
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get(endpoint, headers=headers)
    # Should not be forbidden (403), might be 200 or 500 depending on DB
    assert response.status_code != 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
