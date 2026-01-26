import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure backend is importable when running from project root
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)


@pytest.fixture(scope="session")
def client():
    from backend.app import app
    return TestClient(app)


@pytest.fixture(scope="function")
def setup_test_database():
    # Ensure we use test settings and Alembic to create full schema
        os.environ["ENV"] = "test"
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/divina_dev"
    # Start from a clean database file to avoid stale schemas
    try:
        if os.path.exists("test.db"):
            os.remove("test.db")
    except Exception:
        pass
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config(
        os.path.join(os.path.dirname(__file__), "../../alembic.ini")
    )
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../migrations"))
    alembic_cfg.set_main_option("script_location", migrations_dir)
    command.upgrade(alembic_cfg, "head")
    # Ensure any tables missing from migrations are created from ORM metadata
    try:
        from backend.db.base import Base
        from backend.persistance.base import get_engine
        Base.metadata.create_all(get_engine())
    except Exception:
        pass
    # Debug: list tables present after migration
    try:
        import sqlite3
        conn = sqlite3.connect("test.db")
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("Tables:", sorted(tables))
        conn.close()
    except Exception:
        pass
    yield


def seed_product_and_variant():
    from backend.persistance.base import SessionLocal
    from backend.persistance.product import Product
    from backend.persistance.product_variant import ProductVariant
    from backend.persistance.user import User
    from backend.persistance.category import Category
    import datetime as dt

    db = SessionLocal()
    # Ensure a clean state for the fixed variant_id used in tests
    try:
        existing = db.query(ProductVariant).filter(ProductVariant.variant_id == 1).first()
        if existing:
            db.delete(existing)
            db.commit()
    except Exception:
        pass
    # Ensure required FK parents exist
    # Reuse existing seller user if present to avoid unique email collisions
    u = db.query(User).filter(User.email == "seller@example.com").first()
    if not u:
        u = User(
            full_name="Seller One",
            dob=dt.date(1980, 1, 1),
            password="x",
            phone_number="0000000000",
            email="seller@example.com",
            created_at=dt.date.today(),
            img_location="",
            account_status="True",
        )
        db.add(u)
        db.commit()
        db.refresh(u)

    c = Category(category_id=1, name="General", image_url=None)
    try:
        db.add(c)
        db.commit()
    except Exception:
        db.rollback()

    p = Product(
        title="Test Product",
        description="Desc",
        price=9.99,
        currency="USD",
        is_active=True,
        created_at=dt.datetime.now(),
        updated_at=dt.datetime.now(),
        seller_id=u.user_id,
        category_id=1,
        subcategory_id=None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    v = ProductVariant(
        variant_id=1,
        product_id=p.product_id,
        variant_name="Red",
        price=12.34,
        quantity=2,
        is_active=True,
    )
    db.add(v)
    # Also add an inactive product to test invalid case
    p_inactive = Product(
        title="Inactive",
        description="",
        price=5.00,
        currency="USD",
        is_active=False,
        created_at=dt.datetime.now(),
        updated_at=dt.datetime.now(),
        seller_id=u.user_id,
        category_id=1,
        subcategory_id=None,
    )
    db.add(p_inactive)
    db.commit()
    pid = p.product_id
    db.close()
    return pid


def headers_user():
    return {
        "X-Auth-Role": "user",
        "X-Auth-Id": "1",
    }


def test_browse_parity_list(setup_test_database, client):
    # Seed at least one product
    seed_product_and_variant()
    r_guest = client.get("/api/v1/catalog/products")
    r_user = client.get("/api/v1/catalog/products", headers=headers_user())
    assert r_guest.status_code == 200
    assert r_user.status_code == 200
    assert r_guest.json() == r_user.json()


def test_browse_parity_detail(setup_test_database, client):
    pid = seed_product_and_variant()
    r_guest = client.get(f"/api/v1/catalog/products/{pid}")
    r_user = client.get(f"/api/v1/catalog/products/{pid}", headers=headers_user())
    assert r_guest.status_code == 200
    assert r_user.status_code == 200
    assert r_guest.json() == r_user.json()


def test_validate_cart_public_and_auth(setup_test_database, client):
    pid = seed_product_and_variant()
    # Guest validation
    payload = {
        "items": [
            {"product_id": pid, "quantity": 3},  # non-variant
            {"product_id": pid, "variant_id": 1, "quantity": 5},  # exceeds stock
            {"product_id": pid + 999, "quantity": 1},  # missing product
            {"product_id": pid, "variant_id": 9999, "quantity": 1},  # missing variant
        ]
    }
    r_guest = client.post("/api/v1/catalog/validate-cart", json=payload)
    assert r_guest.status_code == 200
    data_guest = r_guest.json()["items"]
    # Non-variant allowed as requested
    assert data_guest[0]["allowed_quantity"] == 3
    assert data_guest[0]["available"] is True
    # Variant reduced to available stock (2)
    assert data_guest[1]["allowed_quantity"] == 2
    assert data_guest[1]["available"] is True
    assert "reduced" in (data_guest[1]["message"] or "")
    # Missing product is unavailable
    assert data_guest[2]["available"] is False
    # Missing variant is unavailable
    assert data_guest[3]["available"] is False

    # Auth user should receive identical validation results
    r_user = client.post("/api/v1/catalog/validate-cart", json=payload, headers=headers_user())
    assert r_user.status_code == 200
    assert r_user.json() == r_guest.json()


def test_checkout_requires_auth(setup_test_database, client):
    # Attempt to add to customer cart without auth -> forbidden
    r_guest = client.post("/api/v1/customer/cart/items", json={"product_id": 1, "quantity": 1})
    assert r_guest.status_code in (401, 403)
    # With auth, allowed (service seeds stub product in tests if missing)
    r_user = client.post(
        "/api/v1/customer/cart/items",
        json={"product_id": 1, "quantity": 1},
        headers=headers_user(),
    )
    assert r_user.status_code == 200