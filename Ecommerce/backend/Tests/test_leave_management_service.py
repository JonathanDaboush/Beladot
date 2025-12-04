"""
Comprehensive tests for LeaveManagementService.

Tests cover:
- PTO requests
- Sick leave requests
- Balance tracking
- Approval workflow
- Accrual calculations
- Conflict detection
- Edge cases and validation
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from Services.LeaveManagementService import LeaveManagementService
from Models.PaidTimeOff import PTOStatus
from Models.PaidSick import SickLeaveStatus


@pytest.mark.asyncio
class TestLeaveManagementService:
    """Test suite for LeaveManagementService."""
    
    async def test_request_pto_success(self, db_session, create_test_employee):
        """Test successful PTO request."""
        employee = await create_test_employee(
            employee_number="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            position="Worker",
            department="IT",
            pto_balance=80.0
        )
        
        service = LeaveManagementService(db_session)
        
        pto_request = await service.request_pto(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=9),
            hours_requested=24.0,  # 3 days * 8 hours
            pto_type="vacation",
            notes="Family vacation"
        )
        
        assert pto_request is not None
        assert pto_request.employee_id == employee.id
        assert pto_request.hours_requested == Decimal("24.0")
        assert pto_request.status == PTOStatus.PENDING
    
    async def test_request_pto_insufficient_balance(self, db_session, create_test_employee):
        """Test PTO request with insufficient balance."""
        employee = await create_test_employee(
            employee_number="EMP002",
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            position="Worker",
            department="Sales",
            pto_balance=8.0  # Only 1 day available
        )
        
        service = LeaveManagementService(db_session)
        
        # Request more than available
        with pytest.raises(ValueError, match="insufficient balance"):
            await service.request_pto(
                employee_id=employee.id,
                start_date=date.today() + timedelta(days=7),
                end_date=date.today() + timedelta(days=11),
                hours_requested=40.0,  # 5 days
                pto_type="vacation"
            )
    
    async def test_request_pto_invalid_dates(self, db_session, create_test_employee):
        """Test PTO request with end date before start date."""
        employee = await create_test_employee(
            employee_number="EMP003",
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.com",
            position="Worker",
            department="Operations",
            pto_balance=80.0
        )
        
        service = LeaveManagementService(db_session)
        
        with pytest.raises(ValueError):
            await service.request_pto(
                employee_id=employee.id,
                start_date=date.today() + timedelta(days=10),
                end_date=date.today() + timedelta(days=5),
                hours_requested=40.0,
                pto_type="vacation"
            )
    
    async def test_approve_pto_request(self, db_session, create_test_employee):
        """Test approving a PTO request."""
        employee = await create_test_employee(
            employee_number="EMP004",
            first_name="Alice",
            last_name="Williams",
            email="alice@test.com",
            position="Worker",
            department="HR",
            pto_balance=80.0
        )
        
        manager = await create_test_employee(
            employee_number="MGR001",
            first_name="Manager",
            last_name="Brown",
            email="manager@test.com",
            position="Manager",
            department="HR"
        )
        
        service = LeaveManagementService(db_session)
        
        # Create PTO request
        pto_request = await service.request_pto(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=14),
            end_date=date.today() + timedelta(days=18),
            hours_requested=40.0,
            pto_type="vacation"
        )
        
        # Approve request
        approved = await service.approve_pto(pto_request.id, manager.id)
        
        assert approved.status == PTOStatus.APPROVED
        assert approved.reviewed_by == manager.id
        assert approved.reviewed_at is not None
        
        # Verify balance deducted
        from Repositories.EmployeeRepository import EmployeeRepository
        employee_repo = EmployeeRepository(db_session)
        updated_employee = await employee_repo.get_by_id(employee.id)
        assert updated_employee.pto_balance == 40.0  # 80 - 40
    
    async def test_deny_pto_request(self, db_session, create_test_employee):
        """Test denying a PTO request."""
        employee = await create_test_employee(
            employee_number="EMP005",
            first_name="Charlie",
            last_name="Davis",
            email="charlie@test.com",
            position="Worker",
            department="Production",
            pto_balance=80.0
        )
        
        manager = await create_test_employee(
            employee_number="MGR002",
            first_name="Supervisor",
            last_name="Garcia",
            email="supervisor@test.com",
            position="Manager",
            department="Production"
        )
        
        service = LeaveManagementService(db_session)
        
        pto_request = await service.request_pto(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=3),
            end_date=date.today() + timedelta(days=5),
            hours_requested=24.0,
            pto_type="vacation"
        )
        
        # Deny request
        denied = await service.deny_pto(
            pto_request.id, 
            manager.id, 
            reason="Insufficient coverage"
        )
        
        assert denied.status == PTOStatus.DENIED
        assert denied.reviewed_by == manager.id
        assert denied.denial_reason == "Insufficient coverage"
        
        # Verify balance unchanged
        from Repositories.EmployeeRepository import EmployeeRepository
        employee_repo = EmployeeRepository(db_session)
        updated_employee = await employee_repo.get_by_id(employee.id)
        assert updated_employee.pto_balance == 80.0
    
    async def test_request_sick_leave(self, db_session, create_test_employee):
        """Test sick leave request."""
        employee = await create_test_employee(
            employee_number="EMP006",
            first_name="Diana",
            last_name="Martinez",
            email="diana@test.com",
            position="Worker",
            department="Warehouse",
            sick_balance=40.0
        )
        
        service = LeaveManagementService(db_session)
        
        sick_request = await service.request_sick_leave(
            employee_id=employee.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            hours_requested=16.0,  # 2 days
            sick_type="illness",
            notes="Flu symptoms"
        )
        
        assert sick_request is not None
        assert sick_request.employee_id == employee.id
        assert sick_request.hours_requested == Decimal("16.0")
        assert sick_request.status == SickLeaveStatus.PENDING
    
    async def test_approve_sick_leave(self, db_session, create_test_employee):
        """Test approving sick leave."""
        employee = await create_test_employee(
            employee_number="EMP007",
            first_name="Eve",
            last_name="Lopez",
            email="eve@test.com",
            position="Worker",
            department="Customer Service",
            sick_balance=40.0
        )
        
        manager = await create_test_employee(
            employee_number="MGR003",
            first_name="CS",
            last_name="Manager",
            email="csmanager@test.com",
            position="Manager",
            department="Customer Service"
        )
        
        service = LeaveManagementService(db_session)
        
        sick_request = await service.request_sick_leave(
            employee_id=employee.id,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today(),
            hours_requested=16.0,
            sick_type="illness"
        )
        
        approved = await service.approve_sick_leave(sick_request.id, manager.id)
        
        assert approved.status == SickLeaveStatus.APPROVED
        assert approved.reviewed_by == manager.id
        
        # Verify balance deducted
        from Repositories.EmployeeRepository import EmployeeRepository
        employee_repo = EmployeeRepository(db_session)
        updated_employee = await employee_repo.get_by_id(employee.id)
        assert updated_employee.sick_balance == 24.0  # 40 - 16
    
    async def test_get_pto_balance(self, db_session, create_test_employee):
        """Test retrieving PTO balance."""
        employee = await create_test_employee(
            employee_number="EMP008",
            first_name="Frank",
            last_name="Taylor",
            email="frank@test.com",
            position="Worker",
            department="IT",
            pto_balance=120.0
        )
        
        service = LeaveManagementService(db_session)
        balance = await service.get_pto_balance(employee.id)
        
        assert balance == Decimal("120.0")
    
    async def test_get_sick_balance(self, db_session, create_test_employee):
        """Test retrieving sick leave balance."""
        employee = await create_test_employee(
            employee_number="EMP009",
            first_name="Grace",
            last_name="Anderson",
            email="grace@test.com",
            position="Worker",
            department="Sales",
            sick_balance=56.0
        )
        
        service = LeaveManagementService(db_session)
        balance = await service.get_sick_balance(employee.id)
        
        assert balance == Decimal("56.0")
    
    async def test_accrue_pto(self, db_session, create_test_employee):
        """Test PTO accrual."""
        employee = await create_test_employee(
            employee_number="EMP010",
            first_name="Henry",
            last_name="Thomas",
            email="henry@test.com",
            position="Worker",
            department="Operations",
            pto_balance=40.0
        )
        
        service = LeaveManagementService(db_session)
        
        # Accrue 8 hours
        new_balance = await service.accrue_pto(employee.id, hours=8.0)
        
        assert new_balance == Decimal("48.0")
    
    async def test_accrue_sick_leave(self, db_session, create_test_employee):
        """Test sick leave accrual."""
        employee = await create_test_employee(
            employee_number="EMP011",
            first_name="Ivy",
            last_name="Miller",
            email="ivy@test.com",
            position="Worker",
            department="HR",
            sick_balance=24.0
        )
        
        service = LeaveManagementService(db_session)
        
        # Accrue 4 hours
        new_balance = await service.accrue_sick_leave(employee.id, hours=4.0)
        
        assert new_balance == Decimal("28.0")
    
    async def test_cancel_pto_request(self, db_session, create_test_employee):
        """Test canceling a PTO request."""
        employee = await create_test_employee(
            employee_number="EMP012",
            first_name="Jack",
            last_name="Davis",
            email="jack@test.com",
            position="Worker",
            department="Finance",
            pto_balance=80.0
        )
        
        service = LeaveManagementService(db_session)
        
        pto_request = await service.request_pto(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=32),
            hours_requested=24.0,
            pto_type="vacation"
        )
        
        # Cancel request
        cancelled = await service.cancel_pto_request(pto_request.id, employee.id)
        
        assert cancelled.status == "cancelled"
    
    async def test_check_leave_conflicts(self, db_session, create_test_employee):
        """Test detecting conflicting leave requests."""
        employee = await create_test_employee(
            employee_number="EMP013",
            first_name="Kate",
            last_name="Wilson",
            email="kate@test.com",
            position="Worker",
            department="Marketing",
            pto_balance=120.0
        )
        
        manager = await create_test_employee(
            employee_number="MGR004",
            first_name="Marketing",
            last_name="Director",
            email="marketing@test.com",
            position="Manager",
            department="Marketing"
        )
        
        service = LeaveManagementService(db_session)
        
        # Create and approve first PTO
        pto1 = await service.request_pto(
            employee_id=employee.id,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            hours_requested=24.0,
            pto_type="vacation"
        )
        await service.approve_pto(pto1.id, manager.id)
        
        # Attempt overlapping request
        with pytest.raises(ValueError, match="conflict"):
            await service.request_pto(
                employee_id=employee.id,
                start_date=date.today() + timedelta(days=11),
                end_date=date.today() + timedelta(days=13),
                hours_requested=24.0,
                pto_type="vacation"
            )
    
    async def test_get_leave_history(self, db_session, create_test_employee):
        """Test retrieving leave history."""
        employee = await create_test_employee(
            employee_number="EMP014",
            first_name="Leo",
            last_name="Moore",
            email="leo@test.com",
            position="Worker",
            department="Logistics",
            pto_balance=80.0
        )
        
        service = LeaveManagementService(db_session)
        
        # Create multiple PTO requests
        for i in range(3):
            await service.request_pto(
                employee_id=employee.id,
                start_date=date.today() + timedelta(days=20 + i*10),
                end_date=date.today() + timedelta(days=22 + i*10),
                hours_requested=24.0,
                pto_type="vacation"
            )
        
        # Get history
        history = await service.get_leave_history(
            employee.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60)
        )
        
        assert len(history["pto_requests"]) == 3
    
    async def test_batch_accrual_processing(self, db_session):
        """Test batch PTO accrual for multiple employees."""
        from Repositories.EmployeeRepository import EmployeeRepository
        from Models.Employee import Employee
        
        employee_repo = EmployeeRepository(db_session)
        
        # Create employees
        employees = []
        for i in range(5):
            emp = Employee(
                employee_number=f"ACCRUE{i:03d}",
                first_name=f"Worker{i}",
                last_name="Accrual",
                email=f"accrue{i}@test.com",
                position="Worker",
                department="Operations",
                pto_balance=40.0
            )
            emp = await employee_repo.create(emp)
            employees.append(emp)
        
        service = LeaveManagementService(db_session)
        
        # Batch accrue 8 hours for all
        results = await service.batch_accrue_pto(
            [emp.id for emp in employees],
            hours=8.0
        )
        
        assert len(results) == 5
        assert all(r["new_balance"] == Decimal("48.0") for r in results)
    
    async def test_pto_request_requires_notice(self, db_session, create_test_employee):
        """Test that PTO requests require advance notice."""
        employee = await create_test_employee(
            employee_number="EMP015",
            first_name="Mary",
            last_name="Jackson",
            email="mary@test.com",
            position="Worker",
            department="Retail",
            pto_balance=80.0
        )
        
        service = LeaveManagementService(db_session)
        
        # Request PTO for tomorrow (insufficient notice)
        with pytest.raises(ValueError, match="advance notice"):
            await service.request_pto(
                employee_id=employee.id,
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=1),
                hours_requested=8.0,
                pto_type="vacation",
                minimum_notice_days=7
            )
