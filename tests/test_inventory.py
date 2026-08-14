import pytest

@pytest.mark.asyncio
async def test_stock_in_and_stock_out(client, super_admin_headers):
    # Create Warehouse
    wh_resp = await client.post(
        "/api/v1/warehouses",
        headers=super_admin_headers,
        json={"name": "Central Hub", "code": "WH-01", "address": "123 Street", "capacity": 5000.0}
    )
    assert wh_resp.status_code == 201
    wh_id = wh_resp.json()["id"]

    # Create Product
    prod_resp = await client.post(
        "/api/v1/products",
        headers=super_admin_headers,
        json={
            "sku": "PROD-100",
            "name": "Industrial Sensor",
            "category": "Electronics",
            "brand": "TechCorp",
            "cost_price": 50.0,
            "selling_price": 80.0,
            "reorder_level": 15
        }
    )
    assert prod_resp.status_code == 201
    prod_id = prod_resp.json()["id"]

    # Stock In 100 units
    st_in_resp = await client.post(
        "/api/v1/inventory/stock-in",
        headers=super_admin_headers,
        json={"product_id": prod_id, "warehouse_id": wh_id, "quantity": 100}
    )
    assert st_in_resp.status_code == 200
    assert st_in_resp.json()["available_quantity"] == 100

    # Stock Out 30 units
    st_out_resp = await client.post(
        "/api/v1/inventory/stock-out",
        headers=super_admin_headers,
        json={"product_id": prod_id, "warehouse_id": wh_id, "quantity": 30}
    )
    assert st_out_resp.status_code == 200
    assert st_out_resp.json()["available_quantity"] == 70

    # History test
    hist_resp = await client.get("/api/v1/inventory/history", headers=super_admin_headers)
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()) == 2
