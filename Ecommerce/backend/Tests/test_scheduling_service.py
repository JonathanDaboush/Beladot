"""
Comprehensive tests for SchedulingService.

Tests cover:
- Shift creation and management
- Shift overlaps detection
- Employee availability
- Shift swaps and trades
- Coverage requirements
- Schedule conflicts
- Edge cases and validation
"""
import pytest
from datetime import date, time, datetime, timedelta
from Services.SchedulingService import SchedulingService


@pytest.mark.asyncio
class TestSchedulingService:
    """Test suite for SchedulingService."""
    
    async def test_create_shift_success(self, db_session, create_test_employee):
        """Test successful shift creation."""
        employee = await create_test_employee(
            employee_number="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            position="Worker",
            department="Operations"
        )
        
        manager = await create_test_employee(
            employee_number="MGR001",
            first_name="Manager",
            last_name="Smith",
            email="manager@test.com",
            position="Manager",
            department="Operations"
        )
        
        service = SchedulingService(db_session)
        shift = await service.create_shift(
            employee_id=employee.id,
            shift_date=date.today() + timedelta(days=1),
            shift_start=time(9, 0),
            shift_end=time(17, 0),
            created_by=manager.id,
            shift_type="full_day",
            location="Main Office",
            department="Operations"
        )
        
        assert shift is not None
        assert shift.employee_id == employee.id
        assert shift.shift_date == date.today() + timedelta(days=1)
        assert shift.shift_start == time(9, 0)
        assert shift.shift_end == time(17, 0)
    
    async def test_create_shift_overlap_detection(self, db_session, create_test_employee):
        """Test that overlapping shifts are detected and rejected."""
        employee = await create_test_employee(
            employee_number="EMP002",
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            position="Worker",
            department="Sales"
        )
        
        manager = await create_test_employee(
            employee_number="MGR002",
            first_name="Boss",
            last_name="Johnson",
            email="boss@test.com",
            position="Manager",
            department="Sales"
        )
        
        service = SchedulingService(db_session)
        shift_date = date.today() + timedelta(days=2)
        
        # Create first shift
        await service.create_shift(
            employee_id=employee.id,
            shift_date=shift_date,
            shift_start=time(9, 0),
            shift_end=time(17, 0),
            created_by=manager.id
        )
        
        # Attempt to create overlapping shift
        with pytest.raises(ValueError, match="overlap"):
            await service.create_shift(
                employee_id=employee.id,
                shift_date=shift_date,
                shift_start=time(14, 0),
                shift_end=time(22, 0),
                created_by=manager.id
            )
    
    async def test_create_shift_invalid_time_range(self, db_session, create_test_employee):
        """Test that invalid time ranges are rejected."""
        employee = await create_test_employee(
            employee_number="EMP003",
            first_name="Bob",
            last_name="Wilson",
            email="bob@test.com",
            position="Worker",
            department="IT"
        )
        
        manager = await create_test_employee(
            employee_number="MGR003",
            first_name="Admin",
            last_name="Davis",
            email="admin@test.com",
            position="Manager",
            department="IT"
        )
        
        service = SchedulingService(db_session)
        
        # End time before start time
        with pytest.raises(ValueError):
            await service.create_shift(
                employee_id=employee.id,
                shift_date=date.today() + timedelta(days=3),
                shift_start=time(17, 0),
                shift_end=time(9, 0),
                created_by=manager.id
            )
    
    async def test_get_employee_schedule(self, db_session, create_test_employee):
        """Test retrieving employee schedule for date range."""
        employee = await create_test_employee(
            employee_number="EMP004",
            first_name="Alice",
            last_name="Brown",
            email="alice@test.com",
            position="Worker",
            department="Production"
        )
        
        manager = await create_test_employee(
            employee_number="MGR004",
            first_name="Supervisor",
            last_name="Miller",
            email="supervisor@test.com",
            position="Manager",
            department="Production"
        )
        
        service = SchedulingService(db_session)
        
        # Create multiple shifts
        start_date = date.today() + timedelta(days=1)
        for i in range(5):
            await service.create_shift(
                employee_id=employee.id,
                shift_date=start_date + timedelta(days=i),
                shift_start=time(9, 0),
                shift_end=time(17, 0),
                created_by=manager.id
            )
        
        # Retrieve schedule
        end_date = start_date + timedelta(days=6)
        schedule = await service.get_employee_schedule(employee.id, start_date, end_date)
        
        assert len(schedule) == 5
        assert all(s.employee_id == employee.id for s in schedule)
    
    async def test_request_shift_swap(self, db_session, create_test_employee):
        """Test shift swap request."""
        employee1 = await create_test_employee(
            employee_number="EMP005",
            first_name="Charlie",
            last_name="Davis",
            email="charlie@test.com",
            position="Worker",
            department="Retail"
        )
        
        employee2 = await create_test_employee(
            employee_number="EMP006",
            first_name="Diana",
            last_name="Garcia",
            email="diana@test.com",
            position="Worker",
            department="Retail"
        )
        
        manager = await create_test_employee(
            employee_number="MGR005",
            first_name="Store",
            last_name="Manager",
            email="store@test.com",
            position="Manager",
            department="Retail"
        )
        
        service = SchedulingService(db_session)
        shift_date = date.today() + timedelta(days=5)
        
        # Create shifts for both employees
        shift1 = await service.create_shift(
            employee_id=employee1.id,
            shift_date=shift_date,
            shift_start=time(9, 0),
            shift_end=time(17, 0),
            created_by=manager.id
        )
        
        shift2 = await service.create_shift(
            employee_id=employee2.id,
            shift_date=shift_date,
            shift_start=time(17, 0),
            shift_end=time(23, 0),
            created_by=manager.id
        )
        
        # Request swap
        swap = await service.request_shift_swap(
            requesting_shift_id=shift1.id,
            target_shift_id=shift2.id,
            reason="Personal commitment"
        )
        
        assert swap is not None
        assert swap.requesting_shift_id == shift1.id
        assert swap.target_shift_id == shift2.id
        assert swap.status == "pending"
    
    async def test_approve_shift_swap(self, db_session, create_test_employee):
        """Test approving a shift swap."""
        employee1 = await create_test_employee(
            employee_number="EMP007",
            first_name="Eve",
            last_name="Martinez",
            email="eve@test.com",
            position="Worker",
            department="Warehouse"
        )
        
        employee2 = await create_test_employee(
            employee_number="EMP008",
            first_name="Frank",
            last_name="Lopez",
            email="frank@test.com",
            position="Worker",
            department="Warehouse"
        )
        
        manager = await create_test_employee(
            employee_number="MGR006",
            first_name="Warehouse",
            last_name="Supervisor",
            email="warehouse@test.com",
            position="Manager",
            department="Warehouse"
        )
        
        service = SchedulingService(db_session)
        shift_date = date.today() + timedelta(days=7)
        
        # Create shifts
        shift1 = await service.create_shift(
            employee_id=employee1.id,
            shift_date=shift_date,
            shift_start=time(6, 0),
            shift_end=time(14, 0),
            created_by=manager.id
        )
        
        shift2 = await service.create_shift(
            employee_id=employee2.id,
            shift_date=shift_date,
            shift_start=time(14, 0),
            shift_end=time(22, 0),
            created_by=manager.id
        )
        
        # Request and approve swap
        swap = await service.request_shift_swap(
            requesting_shift_id=shift1.id,
            target_shift_id=shift2.id
        )
        
        approved_swap = await service.approve_shift_swap(swap.id, manager.id)
        
        assert approved_swap.status == "approved"
    
    async def test_cancel_shift(self, db_session, create_test_employee):
        """Test canceling a scheduled shift."""
        employee = await create_test_employee(
            employee_number="EMP009",
            first_name="Grace",
            last_name="Taylor",
            email="grace@test.com",
            position="Worker",
            department="Customer Service"
        )
        
        manager = await create_test_employee(
            employee_number="MGR007",
            first_name="CS",
            last_name="Manager",
            email="csmanager@test.com",
            position="Manager",
            department="Customer Service"
        )
        
        service = SchedulingService(db_session)
        shift_date = date.today() + timedelta(days=10)
        
        shift = await service.create_shift(
            employee_id=employee.id,
            shift_date=shift_date,
            shift_start=time(10, 0),
            shift_end=time(18, 0),
            created_by=manager.id
        )
        
        # Cancel shift
        cancelled = await service.cancel_shift(shift.id, manager.id, reason="Overstaffed")
        
        assert cancelled.status == "cancelled"
    
    async def test_check_coverage_requirements(self, db_session):
        """Test checking if department has adequate coverage."""
        from Repositories.EmployeeRepository import EmployeeRepository
        from Models.Employee import Employee
        
        employee_repo = EmployeeRepository(db_session)
        
        # Create multiple employees
        employees = []
        for i in range(5):
            emp = Employee(
                employee_number=f"COV{i:03d}",
                first_name=f"Worker{i}",
                last_name="Coverage",
                email=f"worker{i}@test.com",
                position="Associate",
                department="Sales Floor"
            )
            emp = await employee_repo.create(emp)
            employees.append(emp)
        
        manager = Employee(
            employee_number="COVMGR",
            first_name="Coverage",
            last_name="Manager",
            email="covmgr@test.com",
            position="Manager",
            department="Sales Floor"
        )
        manager = await employee_repo.create(manager)
        
        service = SchedulingService(db_session)
        check_date = date.today() + timedelta(days=14)
        
        # Schedule 3 employees
        for i in range(3):
            await service.create_shift(
                employee_id=employees[i].id,
                shift_date=check_date,
                shift_start=time(9, 0),
                shift_end=time(17, 0),
                created_by=manager.id
            )
        
        # Check coverage
        coverage = await service.check_coverage(
            department="Sales Floor",
            shift_date=check_date,
            required_staff=3
        )
        
        assert coverage["scheduled"] == 3
        assert coverage["meets_requirement"] is True
    
    async def test_create_recurring_shifts(self, db_session, create_test_employee):
        """Test creating recurring shifts."""
        employee = await create_test_employee(
            employee_number="EMP010",
            first_name="Henry",
            last_name="Anderson",
            email="henry@test.com",
            position="Worker",
            department="Maintenance"
        )
        
        manager = await create_test_employee(
            employee_number="MGR008",
            first_name="Facility",
            last_name="Manager",
            email="facility@test.com",
            position="Manager",
            department="Maintenance"
        )
        
        service = SchedulingService(db_session)
        start_date = date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=14)
        
        # Calculate expected number of weekdays
        expected_count = 0
        check_date = start_date
        while check_date <= end_date:
            if check_date.weekday() in [0, 1, 2, 3, 4]:  # Monday-Friday
                expected_count += 1
            check_date += timedelta(days=1)
        
        # Create recurring shifts (Monday-Friday)
        shifts = await service.create_recurring_shifts(
            employee_id=employee.id,
            start_date=start_date,
            end_date=end_date,
            shift_start=time(7, 0),
            shift_end=time(15, 0),
            created_by=manager.id,
            days_of_week=[0, 1, 2, 3, 4]  # Monday-Friday
        )
        
        assert len(shifts) == expected_count  # Should create correct number of weekday shifts
        assert all(s.employee_id == employee.id for s in shifts)
    
    async def test_update_shift_time(self, db_session, create_test_employee):
        """Test updating shift times."""
        employee = await create_test_employee(
            employee_number="EMP011",
            first_name="Ivy",
            last_name="Thomas",
            email="ivy@test.com",
            position="Worker",
            department="Reception"
        )
        
        manager = await create_test_employee(
            employee_number="MGR009",
            first_name="Office",
            last_name="Manager",
            email="office@test.com",
            position="Manager",
            department="Reception"
        )
        
        service = SchedulingService(db_session)
        shift_date = date.today() + timedelta(days=20)
        
        shift = await service.create_shift(
            employee_id=employee.id,
            shift_date=shift_date,
            shift_start=time(9, 0),
            shift_end=time(17, 0),
            created_by=manager.id
        )
        
        # Update shift times
        updated = await service.update_shift_time(
            shift_id=shift.id,
            new_start=time(8, 0),
            new_end=time(16, 0),
            updated_by=manager.id
        )
        
        assert updated.shift_start == time(8, 0)
        assert updated.shift_end == time(16, 0)
    
    async def test_get_available_employees_for_shift(self, db_session):
        """Test finding available employees for a shift."""
        from Repositories.EmployeeRepository import EmployeeRepository
        from Models.Employee import Employee
        
        employee_repo = EmployeeRepository(db_session)
        
        # Create employees
        employees = []
        for i in range(4):
            emp = Employee(
                employee_number=f"AVAIL{i:03d}",
                first_name=f"Available{i}",
                last_name="Employee",
                email=f"avail{i}@test.com",
                position="Staff",
                department="Operations"
            )
            emp = await employee_repo.create(emp)
            employees.append(emp)
        
        manager = Employee(
            employee_number="AVAILMGR",
            first_name="Ops",
            last_name="Manager",
            email="opsmgr@test.com",
            position="Manager",
            department="Operations"
        )
        manager = await employee_repo.create(manager)
        
        service = SchedulingService(db_session)
        shift_date = date.today() + timedelta(days=30)
        
        # Schedule one employee
        await service.create_shift(
            employee_id=employees[0].id,
            shift_date=shift_date,
            shift_start=time(9, 0),
            shift_end=time(17, 0),
            created_by=manager.id
        )
        
        # Find available employees
        available = await service.get_available_employees(
            department="Operations",
            shift_date=shift_date,
            shift_start=time(9, 0),
            shift_end=time(17, 0),
            employee_number_filter="AVAIL"  # Only get employees with AVAIL prefix
        )
        
        # Should return 3 available employees (4 total - 1 scheduled)
        assert len(available) == 3
