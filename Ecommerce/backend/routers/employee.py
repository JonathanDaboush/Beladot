"""
Employee Router
Handles employee self-scheduling with 5-staff minimum availability rule
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta
from typing import Optional, List

from database import get_db
from Utilities.auth import get_current_user
from Utilities.rate_limiting import rate_limiter_moderate
from Models.User import UserRole

router = APIRouter(prefix="/api/employee", tags=["Employee"])


@router.get("/availability", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_availability(
    start_date: Optional[date] = Query(None, description="Start date for availability range"),
    end_date: Optional[date] = Query(None, description="End date for availability range"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get employee's availability history and future scheduled shifts.
    
    Shows:
    - Past shifts worked
    - Future scheduled shifts
    - Availability status
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Set default date range if not provided
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today() + timedelta(days=90)
    
    # Get schedules in range
    result = await db.execute(
        select(EmployeeSchedule)
        .where(EmployeeSchedule.employee_id == employee.id)
        .where(EmployeeSchedule.schedule_date >= start_date)
        .where(EmployeeSchedule.schedule_date <= end_date)
        .order_by(EmployeeSchedule.schedule_date)
    )
    schedules = result.scalars().all()
    
    # Split into past and future
    today = date.today()
    past_shifts = [s for s in schedules if s.schedule_date < today]
    future_shifts = [s for s in schedules if s.schedule_date >= today]
    
    return {
        "employee_id": employee.id,
        "employee_number": employee.employee_number,
        "department": employee.department,
        "past_shifts": [
            {
                "date": shift.schedule_date,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "is_available": shift.is_available,
                "approved": shift.approved
            }
            for shift in past_shifts
        ],
        "future_shifts": [
            {
                "date": shift.schedule_date,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "is_available": shift.is_available,
                "approved": shift.approved
            }
            for shift in future_shifts
        ],
        "total_past": len(past_shifts),
        "total_future": len(future_shifts)
    }


@router.post("/availability", dependencies=[Depends(rate_limiter_moderate)])
async def set_availability(
    schedule_date: date,
    start_time: str,  # Format: "09:00"
    end_time: str,  # Format: "17:00"
    is_available: bool,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Employee marks availability for a specific date/time.
    
    5-STAFF MINIMUM RULE:
    - Before allowing employee to mark unavailable, system checks:
      - How many staff in same department are available for that shift
      - If < 5 staff would be available after this change, REJECT
      - This ensures minimum coverage at all times
    
    Workflow:
    1. Employee submits availability
    2. System checks department coverage
    3. If marking unavailable and would drop below 5 staff → REJECT
    4. Otherwise, save and await manager approval
    """
    from sqlalchemy import select, func
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # 5-STAFF MINIMUM CHECK (only if marking unavailable)
    if not is_available:
        # Count available staff in same department for this date
        result = await db.execute(
            select(func.count(EmployeeSchedule.id))
            .join(Employee, Employee.id == EmployeeSchedule.employee_id)
            .where(Employee.department == employee.department)
            .where(EmployeeSchedule.schedule_date == schedule_date)
            .where(EmployeeSchedule.is_available == True)
            .where(EmployeeSchedule.approved == True)
            .where(EmployeeSchedule.employee_id != employee.id)  # Exclude current employee
        )
        available_count = result.scalar() or 0
        
        MINIMUM_STAFF = 5
        if available_count < MINIMUM_STAFF:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot mark unavailable: Only {available_count} staff available in {employee.department} department. Minimum {MINIMUM_STAFF} required for coverage."
            )
    
    # Check if schedule already exists for this date
    result = await db.execute(
        select(EmployeeSchedule)
        .where(EmployeeSchedule.employee_id == employee.id)
        .where(EmployeeSchedule.schedule_date == schedule_date)
    )
    existing_schedule = result.scalar_one_or_none()
    
    if existing_schedule:
        # Update existing
        existing_schedule.start_time = start_time
        existing_schedule.end_time = end_time
        existing_schedule.is_available = is_available
        existing_schedule.approved = False  # Reset approval on change
        message = "Availability updated. Awaiting manager approval."
    else:
        # Create new
        schedule = EmployeeSchedule(
            employee_id=employee.id,
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            is_available=is_available,
            approved=False  # Requires manager approval
        )
        db.add(schedule)
        message = "Availability submitted. Awaiting manager approval."
    
    await db.commit()
    
    return {
        "employee_id": employee.id,
        "schedule_date": schedule_date,
        "is_available": is_available,
        "approved": False,
        "message": message
    }


@router.delete("/availability/{schedule_date}", dependencies=[Depends(rate_limiter_moderate)])
async def remove_availability(
    schedule_date: date,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove availability entry for specific date (before approval)"""
    from sqlalchemy import select
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get employee
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Get schedule
    result = await db.execute(
        select(EmployeeSchedule)
        .where(EmployeeSchedule.employee_id == employee.id)
        .where(EmployeeSchedule.schedule_date == schedule_date)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No availability entry found for this date"
        )
    
    if schedule.approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove approved schedule. Contact your manager."
        )
    
    await db.delete(schedule)
    await db.commit()
    
    return {
        "message": f"Availability entry for {schedule_date} removed successfully"
    }


@router.get("/who-is-working", dependencies=[Depends(rate_limiter_moderate)])
async def view_who_is_working(
    start_date: date,
    end_date: date,
    department: Optional[str] = None,
    position: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View who is working during a time frame.
    Helps employees pick shifts when they can see coworker schedules.
    """
    from sqlalchemy import select, and_
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Build query
    query = select(EmployeeSchedule, Employee).join(
        Employee, Employee.id == EmployeeSchedule.employee_id
    ).where(
        and_(
            EmployeeSchedule.schedule_date >= start_date,
            EmployeeSchedule.schedule_date <= end_date,
            EmployeeSchedule.is_available == True,
            EmployeeSchedule.approved == True
        )
    )
    
    # Filter by department if specified
    if department:
        query = query.where(Employee.department == department)
    
    # Filter by position if specified
    if position:
        query = query.where(Employee.position == position)
    
    query = query.order_by(EmployeeSchedule.schedule_date, EmployeeSchedule.start_time)
    
    result = await db.execute(query)
    schedules = result.all()
    
    # Group by date
    working_schedule = {}
    for schedule, employee in schedules:
        date_str = str(schedule.schedule_date)
        if date_str not in working_schedule:
            working_schedule[date_str] = []
        
        working_schedule[date_str].append({
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "department": employee.department,
            "position": employee.position,
            "start_time": schedule.start_time,
            "end_time": schedule.end_time
        })
    
    return {
        "working_schedule": working_schedule,
        "total_shifts": len(schedules)
    }


@router.post("/leave/pto", dependencies=[Depends(rate_limiter_moderate)])
async def request_pto(
    start_date: date,
    end_date: date,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request paid time off (PTO/vacation days).
    Requires manager approval.
    """
    from Services.LeaveManagementService import LeaveManagementService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    leave_service = LeaveManagementService(db)
    
    await leave_service.request_pto(
        employee_id=employee.id,
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )
    
    return {
        "message": "PTO request submitted. Awaiting manager approval.",
        "start_date": start_date,
        "end_date": end_date
    }


@router.post("/leave/holiday", dependencies=[Depends(rate_limiter_moderate)])
async def request_holiday_time_off(
    holiday_date: date,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request holiday day off.
    Requires manager approval.
    """
    from Services.LeaveManagementService import LeaveManagementService
    from sqlalchemy import select
    from Models.Employee import Employee
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    leave_service = LeaveManagementService(db)
    
    # Request as PTO but mark as holiday
    await leave_service.request_pto(
        employee_id=employee.id,
        start_date=holiday_date,
        end_date=holiday_date,
        reason=f"HOLIDAY: {reason}"
    )
    
    return {
        "message": "Holiday time off request submitted. Awaiting manager approval.",
        "holiday_date": holiday_date
    }


@router.get("/leave/my-requests", dependencies=[Depends(rate_limiter_moderate)])
async def view_my_leave_requests(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View all my leave requests (PTO, holidays, sick leave).
    Shows pending, approved, and denied requests.
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Models.PaidTimeOff import PaidTimeOff
    from Models.PaidSick import PaidSick
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Get PTO requests
    pto_result = await db.execute(
        select(PaidTimeOff)
        .where(PaidTimeOff.employee_id == employee.id)
        .order_by(PaidTimeOff.request_date.desc())
    )
    pto_requests = pto_result.scalars().all()
    
    # Get sick leave requests
    sick_result = await db.execute(
        select(PaidSick)
        .where(PaidSick.employee_id == employee.id)
        .order_by(PaidSick.request_date.desc())
    )
    sick_requests = sick_result.scalars().all()
    
    return {
        "pto_requests": [
            {
                "id": req.id,
                "start_date": req.start_date,
                "end_date": req.end_date,
                "hours": float(req.hours_requested),
                "reason": req.reason,
                "status": req.status,
                "request_date": req.request_date,
                "is_holiday": req.reason and req.reason.startswith("HOLIDAY:")
            }
            for req in pto_requests
        ],
        "sick_requests": [
            {
                "id": req.id,
                "start_date": req.start_date,
                "end_date": req.end_date,
                "hours": float(req.hours_requested),
                "reason": req.reason,
                "status": req.status,
                "request_date": req.request_date
            }
            for req in sick_requests
        ]
    }


@router.get("/shifts/past", dependencies=[Depends(rate_limiter_moderate)])
async def view_past_shifts(
    days_back: int = Query(30, description="Number of days to look back"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    View all past shifts worked by employee.
    Shows history for reference when applying for new shifts.
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    
    # Get past shifts
    result = await db.execute(
        select(EmployeeSchedule)
        .where(EmployeeSchedule.employee_id == employee.id)
        .where(EmployeeSchedule.schedule_date >= start_date)
        .where(EmployeeSchedule.schedule_date < end_date)
        .where(EmployeeSchedule.is_available == True)
        .where(EmployeeSchedule.approved == True)
        .order_by(EmployeeSchedule.schedule_date.desc())
    )
    past_shifts = result.scalars().all()
    
    return {
        "employee_id": employee.id,
        "employee_name": f"{employee.first_name} {employee.last_name}",
        "department": employee.department,
        "position": employee.position,
        "past_shifts": [
            {
                "shift_id": shift.id,
                "date": shift.schedule_date,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "location": shift.location,
                "department": shift.department,
                "position": shift.position
            }
            for shift in past_shifts
        ],
        "total_shifts": len(past_shifts)
    }


@router.get("/shifts/who-working", dependencies=[Depends(rate_limiter_moderate)])
async def see_who_is_working(
    target_date: date = Query(..., description="Date to check staffing"),
    start_time: Optional[str] = Query(None, description="Start time filter (HH:MM)"),
    end_time: Optional[str] = Query(None, description="End time filter (HH:MM)"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    See who is working during a specific time frame.
    Helps employees pick shifts when they know who else is working.
    Enforces 5-staff minimum visibility.
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get current employee
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    current_employee = result.scalar_one_or_none()
    
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Query schedules for the date
    query = select(EmployeeSchedule, Employee)\
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)\
        .where(EmployeeSchedule.schedule_date == target_date)\
        .where(EmployeeSchedule.is_available == True)\
        .where(EmployeeSchedule.approved == True)\
        .where(Employee.department == current_employee.department)
    
    # Apply time filters if provided
    if start_time:
        query = query.where(EmployeeSchedule.start_time <= start_time)
    if end_time:
        query = query.where(EmployeeSchedule.end_time >= end_time)
    
    result = await db.execute(query.order_by(EmployeeSchedule.start_time))
    schedule_employee_pairs = result.all()
    
    working_employees = []
    for schedule, employee in schedule_employee_pairs:
        working_employees.append({
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "position": employee.position,
            "shift_start": schedule.start_time,
            "shift_end": schedule.end_time,
            "location": schedule.location
        })
    
    staff_count = len(working_employees)
    MINIMUM_STAFF = 5
    
    return {
        "target_date": target_date,
        "department": current_employee.department,
        "time_range": {
            "start": start_time,
            "end": end_time
        },
        "working_employees": working_employees,
        "staff_count": staff_count,
        "minimum_required": MINIMUM_STAFF,
        "meets_minimum": staff_count >= MINIMUM_STAFF,
        "can_request_off": staff_count > MINIMUM_STAFF,
        "message": f"{'✅ Minimum staff met' if staff_count >= MINIMUM_STAFF else '⚠️ Below minimum staff'}"
    }


@router.post("/shifts/apply", dependencies=[Depends(rate_limiter_moderate)])
async def apply_for_shift(
    shift_date: date,
    shift_start: str,
    shift_end: str,
    reason: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply for a new shift.
    
    ENFORCES 5-STAFF MINIMUM RULE:
    - Checks current staffing for the requested date
    - Ensures adding this shift won't violate minimum coverage
    - Creates availability request awaiting manager approval
    
    Employee can see who else is working to make informed decisions.
    """
    from sqlalchemy import select, func
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Check if employee already has a schedule for this date
    result = await db.execute(
        select(EmployeeSchedule)
        .where(EmployeeSchedule.employee_id == employee.id)
        .where(EmployeeSchedule.schedule_date == shift_date)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a schedule entry for this date. Use the update endpoint instead."
        )
    
    # Check current staffing for the date
    result = await db.execute(
        select(func.count(EmployeeSchedule.id))
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(Employee.department == employee.department)
        .where(EmployeeSchedule.schedule_date == shift_date)
        .where(EmployeeSchedule.is_available == True)
        .where(EmployeeSchedule.approved == True)
    )
    current_staff_count = result.scalar() or 0
    
    MINIMUM_STAFF = 5
    
    # Create new availability request
    schedule = EmployeeSchedule(
        employee_id=employee.id,
        schedule_date=shift_date,
        start_time=shift_start,
        end_time=shift_end,
        is_available=True,
        approved=False,  # Requires manager approval
        location=employee.work_city,
        department=employee.department,
        position=employee.position,
        notes=reason
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    
    return {
        "message": "Shift application submitted for manager approval",
        "schedule_id": schedule.id,
        "shift_date": shift_date,
        "shift_start": shift_start,
        "shift_end": shift_end,
        "current_staff_count": current_staff_count,
        "minimum_required": MINIMUM_STAFF,
        "coverage_status": "adequate" if current_staff_count >= MINIMUM_STAFF else "below_minimum",
        "approval_status": "pending"
    }


@router.get("/shifts/coverage-status", dependencies=[Depends(rate_limiter_moderate)])
async def check_coverage_status(
    target_date: date = Query(..., description="Date to check coverage"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if the 5-staff minimum is met for a specific date.
    Helps employees decide if they can request time off or should pick up shifts.
    """
    from sqlalchemy import select, func
    from Models.Employee import Employee
    from Models.EmployeeSchedule import EmployeeSchedule
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    # Count current approved staff for the date
    result = await db.execute(
        select(func.count(EmployeeSchedule.id))
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(Employee.department == employee.department)
        .where(EmployeeSchedule.schedule_date == target_date)
        .where(EmployeeSchedule.is_available == True)
        .where(EmployeeSchedule.approved == True)
    )
    approved_count = result.scalar() or 0
    
    # Count pending requests
    result = await db.execute(
        select(func.count(EmployeeSchedule.id))
        .join(Employee, Employee.id == EmployeeSchedule.employee_id)
        .where(Employee.department == employee.department)
        .where(EmployeeSchedule.schedule_date == target_date)
        .where(EmployeeSchedule.is_available == True)
        .where(EmployeeSchedule.approved == False)
    )
    pending_count = result.scalar() or 0
    
    MINIMUM_STAFF = 5
    projected_count = approved_count + pending_count
    
    return {
        "target_date": target_date,
        "department": employee.department,
        "approved_staff": approved_count,
        "pending_requests": pending_count,
        "projected_total": projected_count,
        "minimum_required": MINIMUM_STAFF,
        "meets_minimum": approved_count >= MINIMUM_STAFF,
        "projected_meets_minimum": projected_count >= MINIMUM_STAFF,
        "can_request_off": approved_count > MINIMUM_STAFF,
        "slots_available": max(0, MINIMUM_STAFF - approved_count),
        "status": {
            "current": "adequate" if approved_count >= MINIMUM_STAFF else "understaffed",
            "projected": "adequate" if projected_count >= MINIMUM_STAFF else "understaffed"
        },
        "recommendation": "Can request time off" if approved_count > MINIMUM_STAFF else "Shifts needed - good time to pick up hours"
    }


@router.post("/clock-in", dependencies=[Depends(rate_limiter_moderate)])
async def clock_in(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Employee manually clocks in for shift.
    
    Creates a new HoursWorked entry with clock-in time.
    Employee must manually clock in at start of shift.
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Services.TimeTrackingService import TimeTrackingService
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    time_service = TimeTrackingService(db)
    
    try:
        hours_entry = await time_service.clock_in(employee.id)
        return {
            "message": "Clocked in successfully",
            "hours_id": hours_entry.id,
            "clocked_in_at": hours_entry.clock_in,
            "employee_id": employee.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/clock-out", dependencies=[Depends(rate_limiter_moderate)])
async def clock_out(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Employee manually clocks out from shift.
    
    Updates the active HoursWorked entry with clock-out time.
    Automatically calculates total hours worked.
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Services.TimeTrackingService import TimeTrackingService
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    time_service = TimeTrackingService(db)
    
    try:
        hours_entry = await time_service.clock_out(employee.id)
        return {
            "message": "Clocked out successfully",
            "hours_id": hours_entry.id,
            "clocked_in_at": hours_entry.clock_in,
            "clocked_out_at": hours_entry.clock_out,
            "total_hours": float(hours_entry.hours_worked or 0),
            "regular_hours": float(hours_entry.regular_hours or 0),
            "overtime_hours": float(hours_entry.overtime_hours or 0),
            "employee_id": employee.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/paycheck", dependencies=[Depends(rate_limiter_moderate)])
async def get_my_paycheck(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get employee's current/recent paycheck details.
    
    Shows:
    - Gross pay
    - Deductions
    - Net pay
    - Hours breakdown (regular, overtime, etc.)
    """
    from sqlalchemy import select
    from Models.Employee import Employee
    from Services.PayrollService import PayrollService
    
    # Get employee record
    result = await db.execute(
        select(Employee).where(Employee.email == current_user.email)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )
    
    payroll_service = PayrollService(db)
    
    try:
        # Calculate paycheck for current employee
        paycheck = await payroll_service.calculate_paycheck(
            employee_id=employee.id,
            pay_period_start=date.today() - timedelta(days=14),  # Last 2 weeks
            pay_period_end=date.today()
        )
        
        return {
            "employee_id": employee.id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_number": employee.employee_number,
            "pay_period": {
                "start": paycheck.get("pay_period_start"),
                "end": paycheck.get("pay_period_end")
            },
            "hours": {
                "regular": float(paycheck.get("regular_hours", 0)),
                "overtime": float(paycheck.get("overtime_hours", 0)),
                "double_time": float(paycheck.get("double_time_hours", 0)),
                "holiday": float(paycheck.get("holiday_hours", 0)),
                "total": float(paycheck.get("total_hours", 0))
            },
            "earnings": {
                "gross_pay": float(paycheck.get("gross_pay", 0)),
                "regular_pay": float(paycheck.get("regular_pay", 0)),
                "overtime_pay": float(paycheck.get("overtime_pay", 0)),
                "holiday_pay": float(paycheck.get("holiday_pay", 0))
            },
            "deductions": paycheck.get("deductions", {}),
            "net_pay": float(paycheck.get("net_pay", 0))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
