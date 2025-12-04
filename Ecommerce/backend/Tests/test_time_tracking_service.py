"""
Comprehensive tests for TimeTrackingService.

Tests cover:
- Clock in/out operations
- Hours calculation
- Overtime tracking
- Timesheet approval
- Break time handling
- Edge cases and validation
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from Services.TimeTrackingService import TimeTrackingService


@pytest.mark.asyncio
class TestTimeTrackingService:
    """Test suite for TimeTrackingService."""
    
    async def test_clock_in_success(self, db_session, create_test_employee):
        """Test successful clock in."""
        employee = await create_test_employee(
            employee_number="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            position="Worker",
            department="Production"
        )
        
        service = TimeTrackingService(db_session)
        hours_record = await service.clock_in(employee.id)
        
        assert hours_record is not None
        assert hours_record.employee_id == employee.id
        assert hours_record.clock_in is not None
        assert hours_record.clock_out is None
        assert hours_record.work_date == date.today()
    
    async def test_clock_in_already_clocked_in(self, db_session, create_test_employee):
        """Test that clocking in twice is rejected."""
        employee = await create_test_employee(
            employee_number="EMP002",
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            position="Worker",
            department="Sales"
        )
        
        service = TimeTrackingService(db_session)
        
        # First clock in
        await service.clock_in(employee.id)
        
        # Second clock in should fail
        with pytest.raises(ValueError, match="already clocked in"):
            await service.clock_in(employee.id)
    
    async def test_clock_out_success(self, db_session, create_test_employee):
        """Test successful clock out."""
        employee = await create_test_employee(
            employee_number="EMP003",
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.com",
            position="Worker",
            department="IT"
        )
        
        service = TimeTrackingService(db_session)
        
        # Clock in
        await service.clock_in(employee.id)
        
        # Clock out after some time
        hours_record = await service.clock_out(employee.id)
        
        assert hours_record.clock_out is not None
        assert hours_record.total_hours > Decimal("0")
        assert hours_record.clock_out > hours_record.clock_in
    
    async def test_clock_out_not_clocked_in(self, db_session, create_test_employee):
        """Test that clocking out without clocking in is rejected."""
        employee = await create_test_employee(
            employee_number="EMP004",
            first_name="Alice",
            last_name="Williams",
            email="alice@test.com",
            position="Worker",
            department="HR"
        )
        
        service = TimeTrackingService(db_session)
        
        with pytest.raises(ValueError, match="not clocked in"):
            await service.clock_out(employee.id)
    
    async def test_calculate_hours_worked(self, db_session, create_test_employee):
        """Test hours calculation."""
        employee = await create_test_employee(
            employee_number="EMP005",
            first_name="Charlie",
            last_name="Brown",
            email="charlie@test.com",
            position="Worker",
            department="Operations"
        )
        
        service = TimeTrackingService(db_session)
        
        # Create hours record manually with specific times
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today()
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=30),
            regular_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            total_hours=Decimal("0")
        )
        hours = await hours_repo.create(hours)
        
        # Calculate hours
        calculated = await service.calculate_hours(hours.id)
        
        assert calculated.total_hours == Decimal("8.5")
        assert calculated.regular_hours == Decimal("8.0")
        assert calculated.overtime_hours == Decimal("0.5")
    
    async def test_calculate_hours_with_overtime(self, db_session, create_test_employee):
        """Test hours calculation with significant overtime."""
        employee = await create_test_employee(
            employee_number="EMP006",
            first_name="Diana",
            last_name="Garcia",
            email="diana@test.com",
            position="Worker",
            department="Manufacturing"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today()
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=7, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=19, minute=0),
            regular_hours=Decimal("0"),
            overtime_hours=Decimal("0"),
            total_hours=Decimal("0")
        )
        hours = await hours_repo.create(hours)
        
        # Calculate hours (12 hours total: 8 regular + 4 overtime)
        calculated = await service.calculate_hours(hours.id)
        
        assert calculated.total_hours == Decimal("12.0")
        assert calculated.regular_hours == Decimal("8.0")
        assert calculated.overtime_hours == Decimal("4.0")
    
    async def test_approve_hours(self, db_session, create_test_employee):
        """Test approving hours worked."""
        employee = await create_test_employee(
            employee_number="EMP007",
            first_name="Eve",
            last_name="Martinez",
            email="eve@test.com",
            position="Worker",
            department="Logistics"
        )
        
        manager = await create_test_employee(
            employee_number="MGR001",
            first_name="Manager",
            last_name="Lopez",
            email="manager@test.com",
            position="Manager",
            department="Logistics"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today() - timedelta(days=1)
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
            regular_hours=Decimal("8.0"),
            overtime_hours=Decimal("0.0"),
            total_hours=Decimal("8.0"),
            status="pending"
        )
        hours = await hours_repo.create(hours)
        
        # Approve hours
        approved = await service.approve_hours(hours.id, manager.id)
        
        assert approved.status == "approved"
        assert approved.approved_by == manager.id
        assert approved.approved_at is not None
    
    async def test_reject_hours(self, db_session, create_test_employee):
        """Test rejecting hours worked."""
        employee = await create_test_employee(
            employee_number="EMP008",
            first_name="Frank",
            last_name="Taylor",
            email="frank@test.com",
            position="Worker",
            department="Warehouse"
        )
        
        manager = await create_test_employee(
            employee_number="MGR002",
            first_name="Supervisor",
            last_name="Anderson",
            email="supervisor@test.com",
            position="Manager",
            department="Warehouse"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today() - timedelta(days=2)
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
            regular_hours=Decimal("8.0"),
            overtime_hours=Decimal("0.0"),
            total_hours=Decimal("8.0"),
            status="pending"
        )
        hours = await hours_repo.create(hours)
        
        # Reject hours
        rejected = await service.reject_hours(
            hours.id, 
            manager.id, 
            reason="Clock times don't match schedule"
        )
        
        assert rejected.status == "rejected"
        assert rejected.rejected_by == manager.id
        assert rejected.rejection_reason == "Clock times don't match schedule"
    
    async def test_get_timesheet_for_period(self, db_session, create_test_employee):
        """Test retrieving timesheet for a pay period."""
        employee = await create_test_employee(
            employee_number="EMP009",
            first_name="Grace",
            last_name="Thomas",
            email="grace@test.com",
            position="Worker",
            department="Customer Service"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        start_date = date.today() - timedelta(days=14)
        
        # Create 10 days of hours
        for i in range(10):
            work_date = start_date + timedelta(days=i)
            hours = HoursWorked(
                employee_id=employee.id,
                work_date=work_date,
                clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
                clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
                regular_hours=Decimal("8.0"),
                overtime_hours=Decimal("0.0"),
                total_hours=Decimal("8.0"),
                status="approved"
            )
            await hours_repo.create(hours)
        
        # Get timesheet
        end_date = date.today()
        timesheet = await service.get_timesheet(employee.id, start_date, end_date)
        
        assert len(timesheet["entries"]) == 10
        assert timesheet["total_hours"] == Decimal("80.0")
        assert timesheet["total_regular_hours"] == Decimal("80.0")
        assert timesheet["total_overtime_hours"] == Decimal("0.0")
    
    async def test_edit_hours_before_approval(self, db_session, create_test_employee):
        """Test editing hours before approval."""
        employee = await create_test_employee(
            employee_number="EMP010",
            first_name="Henry",
            last_name="Miller",
            email="henry@test.com",
            position="Worker",
            department="Maintenance"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today() - timedelta(days=1)
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
            regular_hours=Decimal("8.0"),
            overtime_hours=Decimal("0.0"),
            total_hours=Decimal("8.0"),
            status="pending"
        )
        hours = await hours_repo.create(hours)
        
        # Edit hours
        new_clock_out = datetime.combine(work_date, datetime.min.time()).replace(hour=18, minute=0)
        edited = await service.edit_hours(
            hours.id,
            clock_out=new_clock_out
        )
        
        assert edited.clock_out == new_clock_out
        # Total hours should be recalculated
        assert edited.total_hours == Decimal("9.0")
    
    async def test_edit_hours_after_approval_rejected(self, db_session, create_test_employee):
        """Test that editing approved hours is rejected."""
        employee = await create_test_employee(
            employee_number="EMP011",
            first_name="Ivy",
            last_name="Davis",
            email="ivy@test.com",
            position="Worker",
            department="Admin"
        )
        
        manager = await create_test_employee(
            employee_number="MGR003",
            first_name="Admin",
            last_name="Manager",
            email="adminmgr@test.com",
            position="Manager",
            department="Admin"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today() - timedelta(days=3)
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
            regular_hours=Decimal("8.0"),
            overtime_hours=Decimal("0.0"),
            total_hours=Decimal("8.0"),
            status="approved",
            approved_by=manager.id
        )
        hours = await hours_repo.create(hours)
        
        # Attempt to edit approved hours
        with pytest.raises(ValueError, match="approved"):
            await service.edit_hours(hours.id, clock_out=datetime.now())
    
    async def test_add_break_time(self, db_session, create_test_employee):
        """Test adding break time to hours record."""
        employee = await create_test_employee(
            employee_number="EMP012",
            first_name="Jack",
            last_name="Wilson",
            email="jack@test.com",
            position="Worker",
            department="Production"
        )
        
        service = TimeTrackingService(db_session)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today()
        
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
            regular_hours=Decimal("8.0"),
            overtime_hours=Decimal("0.0"),
            total_hours=Decimal("8.0"),
            break_time_minutes=0
        )
        hours = await hours_repo.create(hours)
        
        # Add 30-minute lunch break
        updated = await service.add_break_time(hours.id, break_minutes=30)
        
        assert updated.break_time_minutes == 30
        # Total hours should be reduced by break time
        assert updated.total_hours == Decimal("7.5")
    
    async def test_batch_approve_hours(self, db_session):
        """Test batch approval of hours."""
        from Repositories.EmployeeRepository import EmployeeRepository
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.Employee import Employee
        from Models.HoursWorked import HoursWorked
        
        employee_repo = EmployeeRepository(db_session)
        hours_repo = HoursWorkedRepository(db_session)
        
        # Create employees and hours
        hours_ids = []
        for i in range(5):
            emp = Employee(
                employee_number=f"BATCH{i:03d}",
                first_name=f"Worker{i}",
                last_name="Batch",
                email=f"batch{i}@test.com",
                position="Worker",
                department="Operations"
            )
            emp = await employee_repo.create(emp)
            
            work_date = date.today() - timedelta(days=1)
            hours = HoursWorked(
                employee_id=emp.id,
                work_date=work_date,
                clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9, minute=0),
                clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17, minute=0),
                regular_hours=Decimal("8.0"),
                overtime_hours=Decimal("0.0"),
                total_hours=Decimal("8.0"),
                status="pending"
            )
            hours = await hours_repo.create(hours)
            hours_ids.append(hours.id)
        
        # Create manager
        manager = Employee(
            employee_number="BATCHMGR",
            first_name="Batch",
            last_name="Manager",
            email="batchmgr@test.com",
            position="Manager",
            department="Operations"
        )
        manager = await employee_repo.create(manager)
        
        service = TimeTrackingService(db_session)
        
        # Batch approve
        results = await service.batch_approve_hours(hours_ids, manager.id)
        
        assert len(results) == 5
        assert all(r["status"] == "approved" for r in results)
