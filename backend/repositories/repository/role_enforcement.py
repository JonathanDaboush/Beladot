def manager_department_required(employee_repo):
"""
role_enforcement.py

Role-based access control utilities for API endpoints.
Includes decorators for enforcing manager department restrictions.
"""

from functools import wraps
from quart import g, jsonify

async def get_employee_department(employee_repo, employee_id):
    """
    Retrieve the department ID for a given employee.
    Args:
        employee_repo: Repository for employee data.
        employee_id: ID of the employee.
    Returns:
        int or None: Department ID if found, else None.
    """
    employee = await employee_repo.get_by_id(employee_id)
    if not employee:
        return None
    return getattr(employee, 'department_id', None)

def manager_department_required(employee_repo):
    """
    Decorator for endpoints: Only allow managers to act on employees in their own department.
    Assumes g.user is set with 'role', 'user_id', and 'department_id'.
    Args:
        employee_repo: Repository for employee data.
    Returns:
        function: Decorator for endpoint function.
    """
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            current_user = g.user
            if current_user.role != 'manager':
                return jsonify({'error': 'Forbidden'}), 403
            data = await args[0].get_json() if args else kwargs.get('data')
            employee_id = data.get('employee_id') if data else kwargs.get('employee_id')
            if not employee_id:
                return jsonify({'error': 'employee_id required'}), 400
            emp_dept = await get_employee_department(employee_repo, employee_id)
            if emp_dept != current_user.department_id:
                return jsonify({'error': 'Forbidden'}), 403
            return await f(*args, **kwargs)
        return wrapper
    return decorator

# Usage in app.py:
# from backend.repository.role_enforcement import manager_department_required
# @app.route('/api/create_pto', methods=['POST'])
# @manager_department_required(employeeServices.employee_repo)
# async def ctrl_create_pto():
#     ...
