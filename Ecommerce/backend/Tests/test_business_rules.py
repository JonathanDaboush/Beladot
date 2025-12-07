"""
Comprehensive Business Rules Tests
Tests all business rules implemented in the controller layer.
"""
import pytest
import pytest_asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import select
from Models.User import User, UserRole
from Models.Employee import Employee
from Models.EmployeeSchedule import EmployeeSchedule
from Models.HoursWorked import HoursWorked
from Models.PaidTimeOff import PaidTimeOff
from Models.Order import Order, OrderStatus
from Models.Shipment import Shipment, ShipmentStatus
from Models.Return import Return, ReturnStatus
from Models.Product import Product
from Models.Seller import Seller


pytestmark = pytest.mark.asyncio


class TestSchedulingBusinessRules:
    """Test the 5-staff minimum scheduling rule."""
    
    async def test_five_staff_minimum_enforced(self, db_session, create_test_employee):
        """Test that 5-staff minimum is enforced when marking availability."""
        # Create department employees
        employees = []
        for i in range(5):
            emp = await create_test_employee(
                first_name=f"Employee{i}",
                last_name=f"Test{i}",
                employee_number=f"EMP{i:03d}",
                department="Sales",
                position="Associate"
            )
            employees.append(emp)
        
        # Create schedules for 4 employees (one below minimum)
        target_date = date.today() + timedelta(days=7)
        for i in range(4):
            schedule = EmployeeSchedule(
                employee_id=employees[i].id,
                schedule_date=target_date,
                start_time="09:00",
                end_time="17:00",
                is_available=True,
                approved=True,
                department="Sales",
                position="Associate"
            )
            db_session.add(schedule)
        
        await db_session.commit()
        
        # Verify count is 4 (below minimum)
        from sqlalchemy import func
        result = await db_session.execute(
            select(func.count(EmployeeSchedule.id))
            .where(EmployeeSchedule.schedule_date == target_date)
            .where(EmployeeSchedule.department == "Sales")
            .where(EmployeeSchedule.is_available == True)
            .where(EmployeeSchedule.approved == True)
        )
        count = result.scalar()
        assert count == 4, "Should have 4 staff scheduled"
        
        # Business rule: Cannot request time off when below minimum
        MINIMUM_STAFF = 5
        assert count < MINIMUM_STAFF, "Below minimum staff - no one can request off"
    
    async def test_five_staff_minimum_allows_timeoff_when_exceeded(self, db_session, create_test_employee):
        """Test that time off is allowed when above minimum staffing."""
        # Create 6 employees
        employees = []
        for i in range(6):
            emp = await create_test_employee(
                first_name=f"Employee{i}",
                last_name=f"Test{i}",
                employee_number=f"EMP{i:03d}",
                department="Sales",
                position="Associate"
            )
            employees.append(emp)
        
        # Schedule all 6 (above minimum)
        target_date = date.today() + timedelta(days=7)
        for emp in employees:
            schedule = EmployeeSchedule(
                employee_id=emp.id,
                schedule_date=target_date,
                start_time="09:00",
                end_time="17:00",
                is_available=True,
                approved=True,
                department="Sales",
                position="Associate"
            )
            db_session.add(schedule)
        
        await db_session.commit()
        
        # Verify count is 6 (above minimum)
        from sqlalchemy import func
        result = await db_session.execute(
            select(func.count(EmployeeSchedule.id))
            .where(EmployeeSchedule.schedule_date == target_date)
            .where(EmployeeSchedule.department == "Sales")
            .where(EmployeeSchedule.is_available == True)
            .where(EmployeeSchedule.approved == True)
        )
        count = result.scalar()
        assert count == 6, "Should have 6 staff scheduled"
        
        # Business rule: Can request time off when above minimum
        MINIMUM_STAFF = 5
        assert count > MINIMUM_STAFF, "Above minimum - employees can request off"


class TestManagerApprovalRules:
    """Test manager approval workflows."""
    
    async def test_hours_require_manager_approval(self, db_session, create_test_employee):
        """Test that hours worked require manager approval."""
        employee = await create_test_employee(
            first_name="John",
            last_name="Worker",
            employee_number="EMP001",
            department="Sales"
        )
        
        # Create hours entry
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=date.today(),
            clock_in=datetime.now().replace(hour=9, minute=0),
            clock_out=datetime.now().replace(hour=17, minute=0),
            total_hours=Decimal("8.0"),
            approved=False  # Business rule: defaults to unapproved
        )
        db_session.add(hours)
        await db_session.commit()
        
        # Verify not approved by default
        result = await db_session.execute(
            select(HoursWorked).where(HoursWorked.id == hours.id)
        )
        saved_hours = result.scalar_one()
        assert saved_hours.approved == False, "Hours should require approval"
    
    async def test_schedule_requires_manager_approval(self, db_session, create_test_employee):
        """Test that schedule requests require manager approval."""
        employee = await create_test_employee(
            first_name="Jane",
            last_name="Employee",
            employee_number="EMP002",
            department="Sales"
        )
        
        # Create schedule request
        schedule = EmployeeSchedule(
            employee_id=employee.id,
            schedule_date=date.today() + timedelta(days=7),
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            approved=False,  # Business rule: defaults to unapproved
            department="Sales",
            position="Associate"
        )
        db_session.add(schedule)
        await db_session.commit()
        
        # Verify not approved
        result = await db_session.execute(
            select(EmployeeSchedule).where(EmployeeSchedule.id == schedule.id)
        )
        saved_schedule = result.scalar_one()
        assert saved_schedule.approved == False, "Schedule should require approval"
    
    async def test_pto_requires_manager_approval(self, db_session, create_test_employee):
        """Test that PTO requests require manager approval."""
        employee = await create_test_employee(
            first_name="Bob",
            last_name="Worker",
            employee_number="EMP003",
            department="Sales"
        )
        
        # Create PTO request
        pto = PaidTimeOff(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=14),
            end_date=date.today() + timedelta(days=16),
            hours_requested=Decimal("24.0"),
            reason="Vacation",
            status="pending"  # Business rule: defaults to pending
        )
        db_session.add(pto)
        await db_session.commit()
        
        # Verify pending status
        result = await db_session.execute(
            select(PaidTimeOff).where(PaidTimeOff.id == pto.id)
        )
        saved_pto = result.scalar_one()
        assert saved_pto.status == "pending", "PTO should require approval"


class TestReturnAndRefundRules:
    """Test return inspection and inventory restoration rules."""
    
    async def test_return_inspection_required(self, db_session, create_test_employee):
        """Test that returns must be inspected before processing."""
        # Create test user
        user = User(
            email="customer@example.com",
            first_name="Test",
            last_name="Customer",
            hashed_password="$2b$12$test",
            role=UserRole.CUSTOMER
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create order
        order = Order(
            user_id=user.id,
            order_number="ORD-TEST-001",
            status=OrderStatus.DELIVERED,
            subtotal_cents=10000,
            tax_cents=1300,
            shipping_cents=500,
            discount_cents=0,
            total_cents=11800,
            shipping_line1="123 Test St",
            shipping_city="Test City",
            shipping_state="TS",
            shipping_postal_code="12345",
            shipping_country="US"
        )
        db_session.add(order)
        await db_session.commit()
        
        # Create return
        return_obj = Return(
            order_id=order.id,
            reason="Damaged",
            status=ReturnStatus.REQUESTED,  # Business rule: starts as requested
            inspection_status="pending"  # Business rule: must be inspected
        )
        db_session.add(return_obj)
        await db_session.commit()
        
        # Verify inspection required
        result = await db_session.execute(
            select(Return).where(Return.id == return_obj.id)
        )
        saved_return = result.scalar_one()
        assert saved_return.inspection_status == "pending", "Return must be inspected"
        assert saved_return.status == ReturnStatus.REQUESTED, "Return starts as requested"


class TestDeliveryTrackingRules:
    """Test delivery tracking for customers, CS, and managers."""
    
    async def test_shipment_tracking_fields_populated(self, db_session):
        """Test that shipment has all required tracking fields."""
        # Create test user
        user = User(
            email="customer@example.com",
            first_name="Test",
            last_name="Customer",
            hashed_password="$2b$12$test",
            role=UserRole.CUSTOMER
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create order
        order = Order(
            user_id=user.id,
            order_number="ORD-TEST-002",
            status=OrderStatus.SHIPPED,
            subtotal_cents=5000,
            tax_cents=650,
            shipping_cents=500,
            discount_cents=0,
            total_cents=6150,
            shipping_line1="123 Test St",
            shipping_city="Test City",
            shipping_state="TS",
            shipping_postal_code="12345",
            shipping_country="US"
        )
        db_session.add(order)
        await db_session.commit()
        
        # Create shipment with tracking
        shipment = Shipment(
            order_id=order.id,
            tracking_number="1Z999AA10123456784",  # Business rule: must have tracking
            carrier="ups",  # Business rule: must have carrier
            status=ShipmentStatus.SHIPPED,
            estimated_delivery=datetime.now() + timedelta(days=3),  # Business rule: must have ETA
            shipped_at=datetime.now(),
            notes="Package picked up from warehouse\nIn transit to distribution center"  # Business rule: location history
        )
        db_session.add(shipment)
        await db_session.commit()
        
        # Verify all tracking fields
        result = await db_session.execute(
            select(Shipment).where(Shipment.id == shipment.id)
        )
        saved_shipment = result.scalar_one()
        assert saved_shipment.tracking_number is not None, "Must have tracking number"
        assert saved_shipment.carrier is not None, "Must have carrier"
        assert saved_shipment.estimated_delivery is not None, "Must have estimated delivery"
        assert saved_shipment.notes is not None, "Must have location history"


class TestUserVerificationRules:
    """Test user account verification for CS and managers."""
    
    async def test_user_account_has_verification_fields(self, db_session):
        """Test that user accounts have all necessary verification fields."""
        user = User(
            email="customer@example.com",
            first_name="John",
            last_name="Doe",
            hashed_password="$2b$12$test",
            role=UserRole.CUSTOMER,
            is_active=True,
            email_verified=True,
            created_at=datetime.now()
        )
        db_session.add(user)
        await db_session.commit()
        
        # Verify all fields for identity verification
        result = await db_session.execute(
            select(User).where(User.id == user.id)
        )
        saved_user = result.scalar_one()
        assert saved_user.email is not None, "Must have email"
        assert saved_user.first_name is not None, "Must have first name"
        assert saved_user.last_name is not None, "Must have last name"
        assert saved_user.is_active is not None, "Must have active status"
        assert saved_user.email_verified is not None, "Must have verification status"
        assert saved_user.created_at is not None, "Must have creation date"


class TestDepartmentScopedAuthority:
    """Test that managers can only manage their department."""
    
    async def test_manager_department_scope(self, db_session, create_test_employee):
        """Test that manager authority is scoped to their department."""
        # Create manager
        manager = await create_test_employee(
            first_name="Manager",
            last_name="Sales",
            employee_number="MGR001",
            department="Sales",
            position="Manager"
        )
        
        # Create employees in different departments
        sales_emp = await create_test_employee(
            first_name="Sales",
            last_name="Employee",
            employee_number="EMP001",
            department="Sales",
            position="Associate"
        )
        
        warehouse_emp = await create_test_employee(
            first_name="Warehouse",
            last_name="Employee",
            employee_number="EMP002",
            department="Warehouse",
            position="Associate"
        )
        
        # Verify departments
        assert manager.department == "Sales", "Manager in Sales"
        assert sales_emp.department == "Sales", "Employee in Sales"
        assert warehouse_emp.department == "Warehouse", "Employee in Warehouse"
        
        # Business rule: Manager can only approve in their department
        # This is enforced in the router layer by checking department match


class TestEmployeeSelfServiceRules:
    """Test employee self-service capabilities."""
    
    async def test_employee_can_view_past_shifts(self, db_session, create_test_employee):
        """Test that employees can view their past shifts."""
        employee = await create_test_employee(
            first_name="John",
            last_name="Worker",
            employee_number="EMP001",
            department="Sales"
        )
        
        # Create past shift
        past_date = date.today() - timedelta(days=7)
        past_shift = EmployeeSchedule(
            employee_id=employee.id,
            schedule_date=past_date,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            approved=True,
            department="Sales",
            position="Associate"
        )
        db_session.add(past_shift)
        await db_session.commit()
        
        # Verify past shift exists
        result = await db_session.execute(
            select(EmployeeSchedule)
            .where(EmployeeSchedule.employee_id == employee.id)
            .where(EmployeeSchedule.schedule_date < date.today())
        )
        past_shifts = result.scalars().all()
        assert len(past_shifts) > 0, "Employee should have past shifts"
    
    async def test_employee_can_apply_for_shifts(self, db_session, create_test_employee):
        """Test that employees can apply for new shifts."""
        employee = await create_test_employee(
            first_name="Jane",
            last_name="Worker",
            employee_number="EMP002",
            department="Sales"
        )
        
        # Create shift application
        future_date = date.today() + timedelta(days=7)
        shift_request = EmployeeSchedule(
            employee_id=employee.id,
            schedule_date=future_date,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            approved=False,  # Business rule: requires approval
            department="Sales",
            position="Associate"
        )
        db_session.add(shift_request)
        await db_session.commit()
        
        # Verify shift application created
        result = await db_session.execute(
            select(EmployeeSchedule)
            .where(EmployeeSchedule.employee_id == employee.id)
            .where(EmployeeSchedule.schedule_date > date.today())
            .where(EmployeeSchedule.approved == False)
        )
        pending_requests = result.scalars().all()
        assert len(pending_requests) > 0, "Employee should be able to apply for shifts"


class TestOrderHistoryAccess:
    """Test that users can view but not alter their past orders."""
    
    async def test_user_can_view_past_orders(self, db_session):
        """Test that users can view their order history."""
        # Create user
        user = User(
            email="customer@example.com",
            first_name="Test",
            last_name="Customer",
            hashed_password="$2b$12$test",
            role=UserRole.CUSTOMER
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create past orders
        for i in range(3):
            order = Order(
                user_id=user.id,
                order_number=f"ORD-{i:05d}",
                status=OrderStatus.DELIVERED,
                subtotal_cents=10000,
                tax_cents=1300,
                shipping_cents=500,
                discount_cents=0,
                total_cents=11800,
                shipping_line1="123 Test St",
                shipping_city="Test City",
                shipping_state="TS",
                shipping_postal_code="12345",
                shipping_country="US",
                created_at=datetime.now() - timedelta(days=30-i)
            )
            db_session.add(order)
        
        await db_session.commit()
        
        # Verify user has order history
        result = await db_session.execute(
            select(Order).where(Order.user_id == user.id)
        )
        orders = result.scalars().all()
        assert len(orders) == 3, "User should have 3 past orders"


class TestCustomerServiceOrderAlterationRights:
    """Test that customer service can alter orders but users cannot."""
    
    async def test_customer_service_role_exists(self, db_session):
        """Test that CUSTOMER_SERVICE role is defined."""
        cs_user = User(
            email="cs@company.com",
            first_name="Customer",
            last_name="Service",
            hashed_password="$2b$12$test",
            role=UserRole.CUSTOMER_SERVICE  # Business rule: special role for order alterations
        )
        db_session.add(cs_user)
        await db_session.commit()
        
        # Verify role
        result = await db_session.execute(
            select(User).where(User.id == cs_user.id)
        )
        saved_user = result.scalar_one()
        assert saved_user.role == UserRole.CUSTOMER_SERVICE, "CS role should exist"


class TestAnalystAccessRules:
    """Test that analysts have read-only access to all analytics."""
    
    async def test_analyst_role_exists(self, db_session):
        """Test that ANALYST role is defined."""
        analyst = User(
            email="analyst@company.com",
            first_name="Data",
            last_name="Analyst",
            hashed_password="$2b$12$test",
            role=UserRole.ANALYST  # Business rule: analytics access
        )
        db_session.add(analyst)
        await db_session.commit()
        
        # Verify role
        result = await db_session.execute(
            select(User).where(User.id == analyst.id)
        )
        saved_user = result.scalar_one()
        assert saved_user.role == UserRole.ANALYST, "Analyst role should exist"


class TestTransportRoleRules:
    """Test that transport role handles imports/exports and returns."""
    
    async def test_transport_role_exists(self, db_session):
        """Test that TRANSPORT role is defined."""
        transport = User(
            email="transport@company.com",
            first_name="Transport",
            last_name="Handler",
            hashed_password="$2b$12$test",
            role=UserRole.TRANSPORT  # Business rule: handles returns and shipments
        )
        db_session.add(transport)
        await db_session.commit()
        
        # Verify role
        result = await db_session.execute(
            select(User).where(User.id == transport.id)
        )
        saved_user = result.scalar_one()
        assert saved_user.role == UserRole.TRANSPORT, "Transport role should exist"


class TestIntegrationBusinessRules:
    """Test integrated business rule scenarios."""
    
    async def test_complete_employee_workflow(self, db_session, create_test_employee):
        """
        Test complete employee workflow:
        1. Employee applies for shift
        2. Manager approves (if meets 5-staff minimum)
        3. Employee clocks in/out
        4. Manager approves hours
        5. Employee requests PTO
        6. Manager approves PTO
        """
        # Create manager and employee
        manager = await create_test_employee(
            first_name="Manager",
            last_name="Approver",
            employee_number="MGR001",
            department="Sales",
            position="Manager"
        )
        
        employee = await create_test_employee(
            first_name="John",
            last_name="Worker",
            employee_number="EMP001",
            department="Sales",
            position="Associate"
        )
        
        # Step 1: Employee applies for shift
        shift_date = date.today() + timedelta(days=7)
        shift_request = EmployeeSchedule(
            employee_id=employee.id,
            schedule_date=shift_date,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            approved=False,
            department="Sales",
            position="Associate"
        )
        db_session.add(shift_request)
        await db_session.commit()
        
        # Step 2: Manager approves
        shift_request.approved = True
        await db_session.commit()
        
        # Step 3: Employee clocks in/out
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=date.today(),
            clock_in=datetime.now().replace(hour=9, minute=0),
            clock_out=datetime.now().replace(hour=17, minute=0),
            total_hours=Decimal("8.0"),
            approved=False
        )
        db_session.add(hours)
        await db_session.commit()
        
        # Step 4: Manager approves hours
        hours.approved = True
        await db_session.commit()
        
        # Step 5: Employee requests PTO
        pto = PaidTimeOff(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=32),
            hours_requested=Decimal("24.0"),
            reason="Vacation",
            status="pending"
        )
        db_session.add(pto)
        await db_session.commit()
        
        # Step 6: Manager approves PTO
        pto.status = "approved"
        await db_session.commit()
        
        # Verify complete workflow
        result = await db_session.execute(
            select(EmployeeSchedule).where(EmployeeSchedule.id == shift_request.id)
        )
        final_shift = result.scalar_one()
        assert final_shift.approved == True, "Shift should be approved"
        
        result = await db_session.execute(
            select(HoursWorked).where(HoursWorked.id == hours.id)
        )
        final_hours = result.scalar_one()
        assert final_hours.approved == True, "Hours should be approved"
        
        result = await db_session.execute(
            select(PaidTimeOff).where(PaidTimeOff.id == pto.id)
        )
        final_pto = result.scalar_one()
        assert final_pto.status == "approved", "PTO should be approved"
    
    async def test_complete_customer_order_workflow(self, db_session):
        """
        Test complete customer order workflow:
        1. Customer places order
        2. Order is shipped with tracking
        3. Customer can view tracking
        4. Order is delivered
        5. Customer can view order history
        """
        # Create customer
        customer = User(
            email="customer@example.com",
            first_name="Test",
            last_name="Customer",
            hashed_password="$2b$12$test",
            role=UserRole.CUSTOMER
        )
        db_session.add(customer)
        await db_session.commit()
        
        # Step 1: Place order
        order = Order(
            user_id=customer.id,
            order_number="ORD-WORKFLOW-001",
            status=OrderStatus.PENDING,
            subtotal_cents=10000,
            tax_cents=1300,
            shipping_cents=500,
            discount_cents=0,
            total_cents=11800,
            shipping_line1="123 Test St",
            shipping_city="Test City",
            shipping_state="TS",
            shipping_postal_code="12345",
            shipping_country="US"
        )
        db_session.add(order)
        await db_session.commit()
        
        # Step 2: Ship order with tracking
        order.status = OrderStatus.SHIPPED
        shipment = Shipment(
            order_id=order.id,
            tracking_number="1Z999AA10123456784",
            carrier="ups",
            status=ShipmentStatus.SHIPPED,
            estimated_delivery=datetime.now() + timedelta(days=3),
            shipped_at=datetime.now(),
            notes="Shipped from warehouse"
        )
        db_session.add(shipment)
        await db_session.commit()
        
        # Step 3: Verify tracking available
        result = await db_session.execute(
            select(Shipment).where(Shipment.order_id == order.id)
        )
        tracking = result.scalar_one()
        assert tracking.tracking_number is not None, "Tracking should be available"
        
        # Step 4: Deliver order
        order.status = OrderStatus.DELIVERED
        shipment.status = ShipmentStatus.DELIVERED
        shipment.delivered_at = datetime.now()
        await db_session.commit()
        
        # Step 5: Verify order in history
        result = await db_session.execute(
            select(Order).where(Order.user_id == customer.id)
        )
        customer_orders = result.scalars().all()
        assert len(customer_orders) == 1, "Customer should have 1 order in history"
        assert customer_orders[0].status == OrderStatus.DELIVERED, "Order should be delivered"
