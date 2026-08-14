import pytest

@pytest.mark.asyncio
async def test_stock_transfer_flow(client, super_admin_headers):
    # Setup Source WH, Dest WH, Product
    wh1_id = (await client.post("/api/v1/warehouses", headers=super_admin_headers, json={"name": "Src WH", "code": "W-SRC", "address": "Addr 1"})).json()["id"]
    wh2_id = (await client.post("/api/v1/warehouses", headers=super_admin_headers, json={"name": "Dst WH", "code": "W-DST", "address": "Addr 2"})).json()["id"]
    prod_id = (await client.post("/api/v1/products", headers=super_admin_headers, json={"sku": "SKU-TR-1", "name": "Transfer Item", "category": "General", "brand": "B1", "cost_price": 5.0, "selling_price": 10.0})).json()["id"]

    # Stock in 100 at Source
    await client.post("/api/v1/inventory/stock-in", headers=super_admin_headers, json={"product_id": prod_id, "warehouse_id": wh1_id, "quantity": 100})

    # Create Transfer Request for 40 units
    tr_resp = await client.post(
        "/api/v1/transfers",
        headers=super_admin_headers,
        json={
            "source_warehouse_id": wh1_id,
            "destination_warehouse_id": wh2_id,
            "items": [{"product_id": prod_id, "quantity": 40}]
        }
    )
    assert tr_resp.status_code == 201
    tr_id = tr_resp.json()["id"]

    # Approve Transfer (Deducts 40 from Source)
    app_resp = await client.post(f"/api/v1/transfers/{tr_id}/approve", headers=super_admin_headers)
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "IN_TRANSIT"

    # Verify Source WH has 60 remaining
    inv1 = (await client.get(f"/api/v1/inventory?warehouse_id={wh1_id}", headers=super_admin_headers)).json()[0]
    assert inv1["available_quantity"] == 60

    # Receive Transfer (Adds 40 to Destination)
    recv_resp = await client.post(f"/api/v1/transfers/{tr_id}/receive", headers=super_admin_headers)
    assert recv_resp.status_code == 200
    assert recv_resp.json()["status"] == "RECEIVED"

    # Verify Dest WH has 40
    inv2 = (await client.get(f"/api/v1/inventory?warehouse_id={wh2_id}", headers=super_admin_headers)).json()[0]
    assert inv2["available_quantity"] == 40
