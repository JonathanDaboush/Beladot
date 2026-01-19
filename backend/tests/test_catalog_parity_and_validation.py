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


@pytest.fixture(scope="session")
def setup_test_database():
    from alembic.config import Config
    from alembic import command

    # Use a synchronous SQLite URL for Alembic
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

    alembic_cfg = Config(
        os.path.join(os.path.dirname(__file__), "../../alembic.ini")
    )
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../migrations"))
    alembic_cfg.set_main_option("script_location", migrations_dir)
    command.upgrade(alembic_cfg, "head")

    # Import models so SQLAlchemy metadata is registered
    import backend.persistance.product
    import backend.persistance.product_variant
    import backend.persistance.product_image
    import backend.persistance.product_variant_image

    from backend.persistance.base import Base, engine as sync_engine
    # Clean slate
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)

    yield


def seed_product_and_variant():
    from backend.persistance.base import SessionLocal
    from backend.persistance.product import Product
    from backend.persistance.product_variant import ProductVariant
    import datetime as dt

    db = SessionLocal()
    p = Product(
        title="Test Product",
        description="Desc",
        price=9.99,
        currency="USD",
        is_active=True,
        created_at=dt.datetime.now(),
        updated_at=dt.datetime.now(),
        seller_id=1,
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
        seller_id=1,
        category_id=1,
        subcategory_id=None,
    )
    db.add(p_inactive)
    db.commit()
    db.close()
    return p


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
    p = seed_product_and_variant()
    r_guest = client.get(f"/api/v1/catalog/products/{p.product_id}")
    r_user = client.get(f"/api/v1/catalog/products/{p.product_id}", headers=headers_user())
    assert r_guest.status_code == 200
    assert r_user.status_code == 200
    assert r_guest.json() == r_user.json()


def test_validate_cart_public_and_auth(setup_test_database, client):
    p = seed_product_and_variant()
    # Guest validation
    payload = {
        "items": [
            {"product_id": p.product_id, "quantity": 3},  # non-variant
            {"product_id": p.product_id, "variant_id": 1, "quantity": 5},  # exceeds stock
            {"product_id": p.product_id + 999, "quantity": 1},  # missing product
            {"product_id": p.product_id, "variant_id": 9999, "quantity": 1},  # missing variant
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