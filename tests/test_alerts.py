import pytest

@pytest.mark.asyncio
async def test_low_stock_alert_trigger(client, super_admin_headers):
    wh_id = (await client.post("/api/v1/warehouses", headers=super_admin_headers, json={"name": "WH Alert", "code": "W-ALT", "address": "Addr"})).json()["id"]
    prod_id = (await client.post("/api/v1/products", headers=super_admin_headers, json={"sku": "SKU-ALT-1", "name": "Alert Item", "category": "General", "brand": "B1", "cost_price": 5.0, "selling_price": 10.0, "reorder_level": 20})).json()["id"]

    # Stock in 30
    await client.post("/api/v1/inventory/stock-in", headers=super_admin_headers, json={"product_id": prod_id, "warehouse_id": wh_id, "quantity": 30})

    # Stock out 15 (stock becomes 15, which is <= reorder level 20)
    await client.post("/api/v1/inventory/stock-out", headers=super_admin_headers, json={"product_id": prod_id, "warehouse_id": wh_id, "quantity": 15})

    # Verify Alert was created
    alerts_resp = await client.get("/api/v1/alerts", headers=super_admin_headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    assert alerts[0]["alert_type"] in ["LOW_STOCK", "OUT_OF_STOCK"]
    assert alerts[0]["is_acknowledged"] is False

    # Acknowledge Alert
    ack_resp = await client.put(f"/api/v1/alerts/{alerts[0]['id']}/acknowledge", headers=super_admin_headers)
    assert ack_resp.status_code == 200
    assert ack_resp.json()["is_acknowledged"] is True
