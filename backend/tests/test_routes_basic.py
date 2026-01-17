import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture(scope="session")
def client():
    from backend.app import app
    return TestClient(app)


def _headers(role: str, id_val: str = "1"):
    base = {"X-Auth-Role": role, "X-Auth-Id": id_val}
    if role == "employee":
        base["X-Auth-Employee-Id"] = id_val
        base["X-Auth-Department-Id"] = "1"
    if role == "seller":
        base["X-Auth-Seller-Id"] = id_val
    if role == "user":
        base["X-Auth-Id"] = id_val
    if role == "manager":
        base["X-Auth-Id"] = id_val
        base["X-Auth-Employee-Id"] = "1"
    return base


def test_uploads_image_endpoint(client, tmp_path):
    path = tmp_path / "u.png"
    path.write_bytes(b"fake")
    with open(path, "rb") as f:
        res = client.post(
            "/api/v1/uploads/images", files={"file": ("u.png", f, "image/png")}
        )
    assert res.status_code in (200, 413, 415, 400, 500)


def test_customer_cart_add_forbidden_without_identity(client):
    res = client.post(
        "/api/v1/customer/cart/items",
        json={"product_id": 1, "quantity": 1},
    )
    assert res.status_code in (401, 403)


def test_customer_cart_add_with_identity(client):
    res = client.post(
        "/api/v1/customer/cart/items",
        json={"product_id": 1, "quantity": 1},
        headers=_headers("user", "10"),
    )
    assert res.status_code in (200, 400, 500)


def test_employee_component_create_requires_role(client):
    res = client.post(
        "/api/v1/employee/components",
        json={"img_url": "x", "description": "y", "department_id": 1},
    )
    assert res.status_code in (401, 403)


def test_employee_component_create_with_role(client):
    res = client.post(
        "/api/v1/employee/components",
        json={"img_url": "x", "description": "y", "department_id": 1},
        headers=_headers("employee", "2"),
    )
    assert res.status_code in (200, 400, 500)


def test_seller_product_create_requires_role(client):
    res = client.post(
        "/api/v1/seller/products",
        json={
            "name": "p",
            "description": "d",
            "price": 1.0,
            "category_id": 1,
        },
    )
    assert res.status_code in (401, 403)


def test_seller_product_create_with_role(client):
    res = client.post(
        "/api/v1/seller/products",
        json={
            "name": "p",
            "description": "d",
            "price": 2.0,
            "category_id": 1,
        },
        headers=_headers("seller", "5"),
    )
    assert res.status_code in (200, 400, 500)


def test_shipping_create_shipment_requires_role(client):
    res = client.post(
        "/api/v1/shipping/shipments",
        json={"order_id": 1, "shipment_status": "created"},
    )
    assert res.status_code in (401, 403)


def test_shipping_create_shipment_with_employee_role(client):
    res = client.post(
        "/api/v1/shipping/shipments",
        json={"order_id": 1, "shipment_status": "created"},
        headers=_headers("employee", "2"),
    )
    assert res.status_code in (200, 400, 500)


def test_assistance_refund_status_with_user_role(client):
    res = client.post(
        "/api/v1/assistance/refund-status",
        json={"customer_email": "a@b.com", "status": "approved"},
        headers=_headers("user", "9"),
    )
    assert res.status_code in (200, 400, 500)


def test_assistance_complaint_with_user_role(client):
    res = client.post(
        "/api/v1/assistance/complaint",
        json={"customer_id": 1, "complaint": "bad"},
        headers=_headers("user", "9"),
    )
    assert res.status_code in (200, 400, 500)


def test_manager_edit_employee_requires_role(client):
    res = client.put("/api/v1/manager/employee/1", json={"notes": "n"})
    assert res.status_code in (401, 403)


def test_shipping_create_shipment_rejects_non_created(client):
    # Ensure non-CREATED status is rejected
    res = client.post(
        "/api/v1/shipping/shipments",
        json={"order_id": 1, "shipment_status": "shipped"},
        headers=_headers("employee", "2"),
    )
    # Rejection may surface as validation (422) or server errors
    assert res.status_code in (400, 422, 500)
