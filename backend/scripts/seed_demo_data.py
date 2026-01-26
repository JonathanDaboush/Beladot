import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from datetime import date, datetime, UTC
import secrets
import string

from sqlalchemy import select, func

## Removed ensure_sqlite_schema import; not needed for Postgres
from backend.persistance.base import get_sessionmaker
from backend.persistance.user import User
from backend.persistance.department import Department
from backend.persistance.employee import Employee
from backend.persistance.manager import Manager
from backend.persistance.finance_employee import FinanceEmployee


ROLES_TO_CREATE = {
    # human users (not employees)
    "user": 5,
    "seller": 5,
    # employees by department
    "customer_service": 5,
    "shipping": 5,
    "finance": 5,
}

DEPARTMENTS = [
    (1, "Customer Service"),
    (2, "Shipping"),
    (3, "Finance"),
]


def upsert_departments(session):
    created = []
    for dep_id, name in DEPARTMENTS:
        existing = session.execute(
            select(Department).where(Department.department_id == dep_id)
        ).scalar_one_or_none()
        if not existing:
            d = Department(department_id=dep_id, name=name)
            session.add(d)
            created.append(d)
    if created:
        session.flush()
    return created


def _next_pk(session, model, pk_attr):
    current_max = session.execute(select(func.max(pk_attr))).scalar()
    return (current_max or 0) + 1


def gen_password(prefix: str, unique: int | str) -> str:
    # Generate a secure, unique password with a stable prefix and 12 random chars
    alphabet = string.ascii_letters + string.digits
    rand = ''.join(secrets.choice(alphabet) for _ in range(12))
    return f"{prefix}-{unique}-{rand}!"


def create_user(session, full_name: str, email: str, password: str) -> User:
    existing = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        # Idempotent: do not modify existing user credentials
        return existing
    u = User(
        full_name=full_name,
        dob=date(1990, 1, 1),
        password=password,
        phone_number="555-0100",
        email=email,
        created_at=date.today(),
        img_location="",
        account_status="True",
    )
    session.add(u)
    session.flush()
    return u


def create_employee(session, user_id: int, department_id: int) -> Employee:
    existing = session.execute(
        select(Employee).where(Employee.user_id == user_id, Employee.department_id == department_id)
    ).scalars().first()
    if existing:
        return existing
    emp_id = _next_pk(session, Employee, Employee.emp_id)
    e = Employee(emp_id=emp_id, user_id=user_id, department_id=department_id, notes=None)
    session.add(e)
    session.flush()
    return e


def create_manager(session, user_id: int, department_id: int) -> Manager:
    existing = session.execute(
        select(Manager).where(Manager.user_id == user_id, Manager.department_id == department_id)
    ).scalars().first()
    if existing:
        return existing
    manager_id = _next_pk(session, Manager, Manager.manager_id)
    now = datetime.now(UTC)
    m = Manager(
        manager_id=manager_id,
        user_id=user_id,
        department_id=department_id,
        is_active=True,
        created_at=now,
        last_active_at=now,
    )
    session.add(m)
    session.flush()
    return m


def create_finance_employee(session, emp: Employee) -> FinanceEmployee:
    existing = session.execute(
        select(FinanceEmployee).where(FinanceEmployee.emp_id == emp.emp_id)
    ).scalars().first()
    if existing:
        return existing
    fe_id = _next_pk(session, FinanceEmployee, FinanceEmployee.finance_emp_id)
    now = datetime.now(UTC)
    fe = FinanceEmployee(
        finance_emp_id=fe_id,
        emp_id=emp.emp_id,
        is_active=True,
        created_at=now,
        last_active_at=now,
    )
    session.add(fe)
    session.flush()
    return fe


def main():
    # No schema creation needed for Postgres
    Session = get_sessionmaker()

    credentials = []
    with Session() as session:
        # Departments
        upsert_departments(session)

        # Human users (customers)
        for i in range(1, ROLES_TO_CREATE["user"] + 1):
            name = f"Demo User {i}"
            email = f"user{i}@example.com"
            password = gen_password("usr", i)
            u = create_user(session, name, email, password)
            credentials.append(("user", email, password))

        # Sellers (as regular users; app uses headers for roles)
        for i in range(1, ROLES_TO_CREATE["seller"] + 1):
            name = f"Demo Seller {i}"
            email = f"seller{i}@example.com"
            password = gen_password("slr", i)
            u = create_user(session, name, email, password)
            credentials.append(("seller", email, password))

        # Employees by department
        dep_map = {
            "customer_service": 1,
            "shipping": 2,
            "finance": 3,
        }

        for role_key, dep_id in dep_map.items():
            for i in range(1, ROLES_TO_CREATE[role_key] + 1):
                name = f"{role_key.replace('_', ' ').title()} Emp {i}"
                email = f"{role_key}{i}@example.com"
                password = gen_password(role_key[:3], i)
                u = create_user(session, name, email, password)
                emp = create_employee(session, u.user_id, dep_id)
                if role_key == "finance":
                    create_finance_employee(session, emp)
                credentials.append((role_key, email, password))

        # Managers: 3 per department
        for dep_id, dep_name in DEPARTMENTS:
            for i in range(1, 4):
                name = f"{dep_name} Manager {i}"
                email = f"mgr_{dep_id}_{i}@example.com"
                password = gen_password("mgr", f"{dep_id}{i}")
                u = create_user(session, name, email, password)
                create_manager(session, u.user_id, dep_id)
                credentials.append((f"manager:{dep_name}", email, password))

        session.commit()

    # Print a friendly summary of credentials
    print("\n=== Seeded Demo Accounts ===")
    for role, email, pwd in credentials:
        print(f"{role}: {email} | {pwd}")


if __name__ == "__main__":
    # Default ENV to dev if not set to ensure local-safe settings
    os.environ.setdefault("ENV", "dev")
    main()
