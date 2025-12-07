"""
Tests for Fulfillment and Shipment Tracking Endpoints
Tests shipment creation and tracking access control.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from Models.User import User, UserRole
from Models.Order import Order, OrderStatus
from Models.Shipment import Shipment, ShipmentStatus
from Models.Employee import Employee


@pytest.mark.asyncio
class TestShipmentTracking:
    """Test shipment tracking with role-based access"""
    
    async def test_customer_track_own_shipment(
        self,
        client: AsyncClient,
        customer_token: str,
        customer_user: User,
        db: AsyncSession
    ):
        """Customer can track their own shipments"""
        # Create order and shipment
        order = Order(
            user_id=customer_user.id,
            status=OrderStatus.CONFIRMED,
            total_price_cents=5000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        shipment = Shipment(
            order_id=order.id,
            tracking_number="TEST123456",
            carrier="purolator",
            status=ShipmentStatus.SHIPPED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)
        
        response = await client.get(
            f"/api/shipments/{shipment.id}/track",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tracking_number"] == "TEST123456"
        assert data["carrier"] == "purolator"
        assert data["status"] == "shipped"
    
    async def test_customer_cannot_track_other_shipment(
        self,
        client: AsyncClient,
        customer_token: str,
        db: AsyncSession
    ):
        """Customer cannot track shipments they don't own"""
        # Create order for different user
        order = Order(
            user_id=999,  # Different user
            status=OrderStatus.CONFIRMED,
            total_price_cents=5000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        
        shipment = Shipment(
            order_id=order.id,
            tracking_number="OTHER123",
            carrier="fedex",
            status=ShipmentStatus.SHIPPED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)
        
        response = await client.get(
            f"/api/shipments/{shipment.id}/track",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_shipping_employee_track_any_shipment(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """Shipping department employees can track any shipment"""
        # Create shipping employee
        employee_user = User(
            email="shipping@test.com",
            hashed_password="hashed",
            role=UserRole.EMPLOYEE
        )
        db.add(employee_user)
        await db.commit()
        await db.refresh(employee_user)
        
        employee = Employee(
            user_id=employee_user.id,
            department="SHIPPING",
            job_id=1,
            hire_date=datetime.now(timezone.utc).date()
        )
        db.add(employee)
        await db.commit()
        
        # Create shipment
        order = Order(
            user_id=999,
            status=OrderStatus.CONFIRMED,
            total_price_cents=5000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        
        shipment = Shipment(
            order_id=order.id,
            tracking_number="SHIP123",
            carrier="ups",
            status=ShipmentStatus.IN_TRANSIT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)
        
        # Create token for employee (mock)
        from Utilities.auth import create_access_token
        token = create_access_token({"sub": employee_user.email})
        
        response = await client.get(
            f"/api/shipments/{shipment.id}/track",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tracking_number"] == "SHIP123"
    
    async def test_cs_staff_track_any_shipment(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """Customer service staff can track any shipment"""
        # Create CS user
        cs_user = User(
            email="cs@test.com",
            hashed_password="hashed",
            role=UserRole.CUSTOMER_SERVICE
        )
        db.add(cs_user)
        await db.commit()
        await db.refresh(cs_user)
        
        # Create shipment
        order = Order(
            user_id=999,
            status=OrderStatus.CONFIRMED,
            total_price_cents=5000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        
        shipment = Shipment(
            order_id=order.id,
            tracking_number="CS123",
            carrier="dhl",
            status=ShipmentStatus.OUT_FOR_DELIVERY,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)
        
        from Utilities.auth import create_access_token
        token = create_access_token({"sub": cs_user.email})
        
        response = await client.get(
            f"/api/shipments/{shipment.id}/track",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["carrier"] == "dhl"
    
    async def test_manager_track_any_shipment(
        self,
        client: AsyncClient,
        manager_token: str,
        db: AsyncSession
    ):
        """Managers can track any shipment"""
        # Create shipment
        order = Order(
            user_id=999,
            status=OrderStatus.CONFIRMED,
            total_price_cents=5000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        
        shipment = Shipment(
            order_id=order.id,
            tracking_number="MGR123",
            carrier="canadapost",
            status=ShipmentStatus.DELIVERED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(shipment)
        await db.commit()
        await db.refresh(shipment)
        
        response = await client.get(
            f"/api/shipments/{shipment.id}/track",
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "delivered"


@pytest.mark.asyncio
class TestGetOrderShipments:
    """Test retrieving all shipments for an order"""
    
    async def test_customer_get_own_order_shipments(
        self,
        client: AsyncClient,
        customer_token: str,
        customer_user: User,
        db: AsyncSession
    ):
        """Customer can get shipments for their own orders"""
        # Create order with multiple shipments (partial shipments)
        order = Order(
            user_id=customer_user.id,
            status=OrderStatus.CONFIRMED,
            total_price_cents=10000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        shipment1 = Shipment(
            order_id=order.id,
            tracking_number="PART1",
            carrier="purolator",
            status=ShipmentStatus.DELIVERED,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        shipment2 = Shipment(
            order_id=order.id,
            tracking_number="PART2",
            carrier="fedex",
            status=ShipmentStatus.IN_TRANSIT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add_all([shipment1, shipment2])
        await db.commit()
        
        response = await client.get(
            f"/api/shipments/order/{order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order.id
        assert len(data["shipments"]) == 2
        assert data["shipments"][0]["tracking_number"] in ["PART1", "PART2"]
    
    async def test_customer_cannot_get_other_order_shipments(
        self,
        client: AsyncClient,
        customer_token: str,
        db: AsyncSession
    ):
        """Customer cannot get shipments for others' orders"""
        order = Order(
            user_id=999,
            status=OrderStatus.CONFIRMED,
            total_price_cents=5000,
            created_at=datetime.now(timezone.utc)
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        response = await client.get(
            f"/api/shipments/order/{order.id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestAutoShipmentCreation:
    """Test automatic shipment creation on order confirmation"""
    
    async def test_shipment_created_on_checkout(
        self,
        client: AsyncClient,
        customer_token: str,
        db: AsyncSession
    ):
        """Shipment should be auto-created when order is confirmed"""
        # This tests the integration in checkout.py
        # Would need full checkout flow with cart, payment, etc.
        # This is a placeholder for integration testing
        pass
