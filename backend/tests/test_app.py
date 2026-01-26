import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure backend is importable when running from project root
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

# -------------------------------------------------------------------
# FIXTURE: FastAPI client (DELAYED app import)
# -------------------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    from backend.app import app
    return TestClient(app)


# -------------------------------------------------------------------
# FIXTURE: Database setup (explicit, not autouse)
# -------------------------------------------------------------------

@pytest.fixture(scope="session")
def setup_test_database():
    from alembic.config import Config
    from alembic import command

    # Use a synchronous SQLite URL for Alembic
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/divina_dev"

    alembic_cfg = Config(
        os.path.join(os.path.dirname(__file__), "../../alembic.ini")
    )
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../migrations"))
    alembic_cfg.set_main_option("script_location", migrations_dir)
    command.upgrade(alembic_cfg, "head")

    # Import models so SQLAlchemy metadata is registered
    import backend.persistance.department
    import backend.persistance.user
    import backend.persistance.employee
    import backend.persistance.manager
    import backend.persistance.shift
    import backend.persistance.incident
    import backend.persistance.cart
    import backend.persistance.order
    import backend.persistance.shipment
    import backend.persistance.product
    import backend.persistance.product_variant
    import backend.persistance.order_item
    import backend.persistance.shipment_item
    import backend.persistance.category
    import backend.persistance.subcategory
    import backend.persistance.product_image
    import backend.persistance.product_variant_image
    import backend.persistance.wishlist
    import backend.persistance.wishlist_item

    # Ensure all ORM models are materialized in the test database
    # using the synchronous engine that points to the same SQLite file.
    from backend.persistance.base import Base, engine as sync_engine
    # Start from a clean slate to avoid cross-test contamination
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    import backend.persistance.payment
    import backend.persistance.payment_snapshot

    yield


# -------------------------------------------------------------------
# BASIC API TESTS
# -------------------------------------------------------------------

def test_api_finance_issues_catalog(client):
    response = client.get("/api/finance/issues")
    assert response.status_code in (200, 401)


def test_api_finance_create_issue_missing_fields(client):
    response = client.post("/api/finance/issues", json={})
    assert response.status_code in (400, 401)
    assert "detail" in response.json()


def test_api_employee_components_for_employee_forbidden(client):
    response = client.get("/api/employee_components/for_employee")
    assert response.status_code in (401, 403)


def test_api_get_cart_items(client):
    response = client.get("/api/get_cart_items")
    assert response.status_code in (200, 401)


def test_api_add_item_to_cart_missing(client):
    response = client.post("/api/add_item_to_cart", json={})
    assert response.status_code in (400, 401)


# -------------------------------------------------------------------
# DATABASE-DEPENDENT TESTS
# -------------------------------------------------------------------

def test_api_manager_edit_employee_info(
    setup_test_database, client, monkeypatch
):
    from backend.persistance.base import SessionLocal
    from backend.persistance.department import Department
    from backend.persistance.user import User
    from backend.persistance.manager import Manager
    from backend.persistance.employee import Employee
    from backend.persistance.shift import Shift
    import datetime as dt

    db = SessionLocal()

    db.add(Department(department_id=1, name="Test Department"))

    db.add_all([
        User(
            user_id=1,
            full_name="Manager User",
            dob=dt.date(1990, 1, 1),
            password="pass",
            phone_number="123",
            email="manager@example.com",
            created_at=dt.date.today(),
            img_location="",
            account_status="True",
        ),
        User(
            user_id=2,
            full_name="Employee User",
            dob=dt.date(1992, 2, 2),
            password="pass",
            phone_number="456",
            email="employee@example.com",
            created_at=dt.date.today(),
            img_location="",
            account_status="True",
        ),
    ])

    db.add_all([
        Manager(
            manager_id=1,
            user_id=1,
            department_id=1,
            is_active=True,
            created_at=dt.datetime.now(),
            last_active_at=dt.datetime.now(),
        ),
        Employee(emp_id=1, user_id=2, department_id=1),
    ])

    db.add(
        Shift(
            department_id=1,
            assigned_emp_id=None,
            start_time=dt.datetime.now(),
            end_time=dt.datetime.now() + dt.timedelta(hours=8),
            created_by_manager_id=1,
            status="scheduled",
        )
    )

    db.commit()
    db.close()

    import backend.services.managerServices as manager_services
    monkeypatch.setattr(
        manager_services,
        "get_current_user",
        lambda: {"manager_id": 1},
        raising=False,
    )

    response = client.put(
        "/api/v1/manager/employee/1",
        json={"notes": "Test update"},
        headers={"Authorization": "Bearer testtoken"} # Add auth if needed
    )

    assert response.status_code in (200, 401)


def test_api_employee_book_shift(setup_test_database, client):
    from backend.persistance.base import SessionLocal
    from backend.persistance.shift import Shift

    db = SessionLocal()
    shift = db.query(Shift).order_by(Shift.shift_id.desc()).first()
    db.close()

    assert shift is not None

    response = client.post(
        "/api/book_shift",
        json={"employee_id": 1, "shift_id": shift.shift_id},
    )

    assert response.status_code in (200, 401)


# -------------------------------------------------------------------
# INTEGRATION TEST
# -------------------------------------------------------------------

@pytest.mark.integration
def test_upload_image(tmp_path, client):
    file_path = tmp_path / "test.jpg"
    file_path.write_bytes(b"test image")

    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/uploads/images",
            files={"file": ("test.jpg", f, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data
    assert "image_id" in data
