from fastapi.testclient import TestClient
from backend.app import app


def test_catalog_list_products_public_ok():
    client = TestClient(app)
    res = client.get("/api/v1/catalog/products")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert isinstance(data["items"], list)


def test_catalog_get_product_alias_404_when_missing():
    client = TestClient(app)
    res = client.get("/api/product/999999")
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data


def test_catalog_get_product_public_404_when_missing():
    client = TestClient(app)
    res = client.get("/api/v1/catalog/products/999999")
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
