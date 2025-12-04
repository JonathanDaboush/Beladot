"""
Comprehensive tests for PayrollService.

Tests cover:
- Paycheck calculation
- Tax withholding
- Overtime calculation
- PTO/sick leave integration
- Batch payroll processing
- Edge cases and validation
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from Services.PayrollService import PayrollService


@pytest.mark.asyncio
class TestPayrollService:
    """Test suite for PayrollService."""
    
    async def test_calculate_paycheck_hourly_no_overtime(self, db_session, create_test_employee):
        """Test paycheck calculation for hourly employee without overtime."""
        # Create employee and financial record
        employee = await create_test_employee(
            employee_number="EMP001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            position="Developer",
            department="IT",
            hire_date=date.today() - timedelta(days=365)
        )
        
        from Repositories.EmployeeFinancialRepository import EmployeeFinancialRepository
        from Models.EmployeeFinancial import EmployeeFinancial
        
        financial_repo = EmployeeFinancialRepository(db_session)
        financial = EmployeeFinancial(
            employee_id=employee.id,
            pay_rate=Decimal("25.00"),
            is_salary=False,
            overtime_eligible=True,
            payment_frequency="bi_weekly",
            payment_method="direct_deposit",
            federal_tax_rate=Decimal("0.15"),
            provincial_tax_rate=Decimal("0.10"),
            cpp_contribution_rate=Decimal("0.0595"),
            ei_contribution_rate=Decimal("0.0166")
        )
        await financial_repo.create(financial)
        
        # Create hours worked
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        from datetime import datetime
        
        hours_repo = HoursWorkedRepository(db_session)
        start_date = date.today() - timedelta(days=14)
        end_date = date.today()
        
        # Add 80 hours of regular work (no overtime)
        for day in range(10):
            work_date = start_date + timedelta(days=day)
            hours = HoursWorked(
                employee_id=employee.id,
                work_date=work_date,
                clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9),
                clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=17),
                hours_worked=Decimal("8.0"),
                overtime_hours=Decimal("0.0"),
                status="approved"
            )
            await hours_repo.create(hours)
        
        # Calculate paycheck
        service = PayrollService(db_session)
        paycheck = await service.calculate_paycheck(employee.id, start_date, end_date)
        
        assert paycheck is not None
        assert paycheck["gross_pay"] == Decimal("2000.00")  # 80 hours * $25
        assert paycheck["federal_tax"] > 0
        assert paycheck["provincial_tax"] > 0
        assert paycheck["cpp"] > 0
        assert paycheck["ei"] > 0
        assert paycheck["net_pay"] < paycheck["gross_pay"]
    
    async def test_calculate_paycheck_with_overtime(self, db_session, create_test_employee):
        """Test paycheck calculation with overtime."""
        employee = await create_test_employee(
            employee_number="EMP002",
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            position="Manager",
            department="Sales",
            hire_date=date.today() - timedelta(days=365)
        )
        
        from Repositories.EmployeeFinancialRepository import EmployeeFinancialRepository
        from Models.EmployeeFinancial import EmployeeFinancial
        
        financial_repo = EmployeeFinancialRepository(db_session)
        financial = EmployeeFinancial(
            employee_id=employee.id,
            pay_rate=Decimal("30.00"),
            is_salary=False,
            overtime_eligible=True,
            overtime_rate_multiplier=Decimal("1.5"),
            payment_frequency="bi_weekly",
            payment_method="direct_deposit",
            federal_tax_rate=Decimal("0.15"),
            provincial_tax_rate=Decimal("0.10"),
            cpp_contribution_rate=Decimal("0.0595"),
            ei_contribution_rate=Decimal("0.0166")
        )
        await financial_repo.create(financial)
        
        # Create hours with overtime
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        from datetime import datetime
        
        hours_repo = HoursWorkedRepository(db_session)
        start_date = date.today() - timedelta(days=14)
        end_date = date.today()
        
        work_date = start_date
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=20),
            hours_worked=Decimal("11.0"),
            overtime_hours=Decimal("3.0"),  # 3 hours overtime
            status="approved"
        )
        await hours_repo.create(hours)
        
        service = PayrollService(db_session)
        paycheck = await service.calculate_paycheck(employee.id, start_date, end_date)
        
        # Regular: 8 hours * $30 = $240
        # Overtime: 3 hours * $30 * 1.5 = $135
        # Total: $375
        expected_gross = Decimal("375.00")
        assert paycheck["gross_pay"] == expected_gross
        assert "overtime_pay" in paycheck
        assert paycheck["overtime_pay"] == Decimal("135.00")
    
    async def test_calculate_paycheck_salary_employee(self, db_session, create_test_employee):
        """Test paycheck calculation for salaried employee."""
        employee = await create_test_employee(
            employee_number="EMP003",
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.com",
            position="Director",
            department="Executive",
            hire_date=date.today() - timedelta(days=365)
        )
        
        from Repositories.EmployeeFinancialRepository import EmployeeFinancialRepository
        from Models.EmployeeFinancial import EmployeeFinancial
        
        financial_repo = EmployeeFinancialRepository(db_session)
        financial = EmployeeFinancial(
            employee_id=employee.id,
            pay_rate=Decimal("100000.00"),  # Annual salary
            is_salary=True,
            overtime_eligible=False,
            payment_frequency="bi_weekly",
            payment_method="direct_deposit",
            federal_tax_rate=Decimal("0.20"),
            provincial_tax_rate=Decimal("0.12"),
            cpp_contribution_rate=Decimal("0.0595"),
            ei_contribution_rate=Decimal("0.0166")
        )
        await financial_repo.create(financial)
        
        service = PayrollService(db_session)
        start_date = date.today() - timedelta(days=14)
        end_date = date.today()
        
        paycheck = await service.calculate_paycheck(employee.id, start_date, end_date)
        
        # Bi-weekly salary: $100,000 / 26 periods
        expected_gross = Decimal("100000.00") / 26
        assert abs(paycheck["gross_pay"] - expected_gross) < Decimal("0.01")
        assert "overtime_pay" not in paycheck or paycheck["overtime_pay"] == 0
    
    async def test_calculate_paycheck_no_financial_record(self, db_session, create_test_employee):
        """Test paycheck calculation fails without financial record."""
        employee = await create_test_employee(
            employee_number="EMP004",
            first_name="Alice",
            last_name="Williams",
            email="alice@test.com",
            position="Intern",
            department="IT"
        )
        
        service = PayrollService(db_session)
        start_date = date.today() - timedelta(days=14)
        end_date = date.today()
        
        with pytest.raises(Exception):  # Should raise error for missing financial record
            await service.calculate_paycheck(employee.id, start_date, end_date)
    
    async def test_tax_withholding_calculations(self, db_session, create_test_employee):
        """Test that tax withholdings are calculated correctly."""
        employee = await create_test_employee(
            employee_number="EMP005",
            first_name="Charlie",
            last_name="Brown",
            email="charlie@test.com",
            position="Analyst",
            department="Finance"
        )
        
        from Repositories.EmployeeFinancialRepository import EmployeeFinancialRepository
        from Models.EmployeeFinancial import EmployeeFinancial
        
        financial_repo = EmployeeFinancialRepository(db_session)
        financial = EmployeeFinancial(
            employee_id=employee.id,
            pay_rate=Decimal("1000.00"),  # Simple number for calculations
            is_salary=False,
            payment_frequency="bi_weekly",
            payment_method="direct_deposit",
            federal_tax_rate=Decimal("0.15"),  # 15%
            provincial_tax_rate=Decimal("0.10"),  # 10%
            cpp_contribution_rate=Decimal("0.0595"),  # 5.95%
            ei_contribution_rate=Decimal("0.0166")  # 1.66%
        )
        await financial_repo.create(financial)
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        from datetime import datetime
        
        hours_repo = HoursWorkedRepository(db_session)
        start_date = date.today() - timedelta(days=14)
        end_date = date.today()
        
        work_date = start_date
        hours = HoursWorked(
            employee_id=employee.id,
            work_date=work_date,
            clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=9),
            clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=10),
            hours_worked=Decimal("1.0"),
            overtime_hours=Decimal("0.0"),
            status="approved"
        )
        await hours_repo.create(hours)
        
        service = PayrollService(db_session)
        paycheck = await service.calculate_paycheck(employee.id, start_date, end_date)
        
        gross = Decimal("1000.00")
        
        # Verify deductions are within expected ranges
        assert paycheck["federal_tax"] == gross * Decimal("0.15")
        assert paycheck["provincial_tax"] == gross * Decimal("0.10")
        assert paycheck["cpp"] == gross * Decimal("0.0595")
        assert paycheck["ei"] == gross * Decimal("0.0166")
        
        # Net pay should be gross minus all deductions
        total_deductions = (
            paycheck["federal_tax"] + 
            paycheck["provincial_tax"] + 
            paycheck["cpp"] + 
            paycheck["ei"]
        )
        assert paycheck["net_pay"] == gross - total_deductions
    
    async def test_calculate_paycheck_negative_hours_rejected(self, db_session, create_test_employee):
        """Test that negative hours worked are rejected."""
        employee = await create_test_employee(
            employee_number="EMP006",
            first_name="David",
            last_name="Miller",
            email="david@test.com",
            position="Clerk",
            department="Admin"
        )
        
        from Repositories.HoursWorkedRepository import HoursWorkedRepository
        from Models.HoursWorked import HoursWorked
        from datetime import datetime
        
        hours_repo = HoursWorkedRepository(db_session)
        work_date = date.today()
        
        with pytest.raises(Exception):  # Should reject negative hours
            hours = HoursWorked(
                employee_id=employee.id,
                work_date=work_date,
                clock_in=datetime.combine(work_date, datetime.min.time()).replace(hour=17),
                clock_out=datetime.combine(work_date, datetime.min.time()).replace(hour=9),
                hours_worked=Decimal("-8.0"),  # Negative hours
                overtime_hours=Decimal("0.0"),
                status="pending"
            )
            await hours_repo.create(hours)
    
    async def test_batch_payroll_processing(self, db_session):
        """Test processing payroll for multiple employees."""
        from Repositories.EmployeeRepository import EmployeeRepository
        from Repositories.EmployeeFinancialRepository import EmployeeFinancialRepository
        from Models.Employee import Employee
        from Models.EmployeeFinancial import EmployeeFinancial
        
        employee_repo = EmployeeRepository(db_session)
        financial_repo = EmployeeFinancialRepository(db_session)
        
        # Create multiple employees
        employees = []
        for i in range(5):
            emp = Employee(
                employee_number=f"EMP{100+i}",
                first_name=f"Employee{i}",
                last_name="Test",
                email=f"emp{i}@test.com",
                position="Worker",
                department="Production",
                hire_date=date.today() - timedelta(days=365)
            )
            emp = await employee_repo.create(emp)
            employees.append(emp)
            
            # Add financial records
            financial = EmployeeFinancial(
                employee_id=emp.id,
                pay_rate=Decimal("20.00"),
                is_salary=False,
                payment_frequency="bi_weekly",
                payment_method="direct_deposit",
                federal_tax_rate=Decimal("0.15"),
                provincial_tax_rate=Decimal("0.10"),
                cpp_contribution_rate=Decimal("0.0595"),
                ei_contribution_rate=Decimal("0.0166")
            )
            await financial_repo.create(financial)
        
        service = PayrollService(db_session)
        start_date = date.today() - timedelta(days=14)
        end_date = date.today()
        
        # Process batch
        results = await service.process_batch_payroll(
            [emp.id for emp in employees],
            start_date,
            end_date
        )
        
        assert len(results) == 5
        for result in results:
            assert "employee_id" in result
            assert "gross_pay" in result
            assert "net_pay" in result
    
    async def test_paycheck_validation_date_range(self, db_session, create_test_employee):
        """Test paycheck calculation with invalid date range."""
        employee = await create_test_employee(
            employee_number="EMP007",
            first_name="Eve",
            last_name="Davis",
            email="eve@test.com",
            position="Tester",
            department="QA"
        )
        
        service = PayrollService(db_session)
        
        # End date before start date
        with pytest.raises(ValueError):
            await service.calculate_paycheck(
                employee.id,
                date.today(),
                date.today() - timedelta(days=14)
            )
