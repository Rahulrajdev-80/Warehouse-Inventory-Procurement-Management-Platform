import pytest

@pytest.mark.asyncio
async def test_purchase_order_lifecycle(client, super_admin_headers):
    # Setup Warehouse, Supplier, Product
    wh_id = (await client.post("/api/v1/warehouses", headers=super_admin_headers, json={"name": "WH 1", "code": "W1", "address": "Addr"})).json()["id"]
    sup_id = (await client.post("/api/v1/suppliers", headers=super_admin_headers, json={"name": "Supplier A", "contact_person": "Jane", "email": "supa@test.com", "phone": "123", "gst_number": "GST1", "address": "A1"})).json()["id"]
    prod_id = (await client.post("/api/v1/products", headers=super_admin_headers, json={"sku": "SKU-PO-1", "name": "PO Item", "category": "General", "brand": "B1", "cost_price": 10.0, "selling_price": 20.0})).json()["id"]

    # 1. Create PO
    po_resp = await client.post(
        "/api/v1/purchase-orders",
        headers=super_admin_headers,
        json={
            "supplier_id": sup_id,
            "warehouse_id": wh_id,
            "items": [{"product_id": prod_id, "quantity": 50, "unit_price": 10.0}]
        }
    )
    assert po_resp.status_code == 201
    po_data = po_resp.json()
    assert po_data["status"] == "DRAFT"
    po_id = po_data["id"]

    # 2. Approve PO
    app_resp = await client.post(f"/api/v1/purchase-orders/{po_id}/approve", headers=super_admin_headers)
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "APPROVED"

    # 3. Receive Goods (Partial & Complete)
    recv_resp = await client.post(
        f"/api/v1/purchase-orders/{po_id}/receive",
        headers=super_admin_headers,
        json={"items": [{"product_id": prod_id, "received_quantity": 50}]}
    )
    assert recv_resp.status_code == 200
    assert recv_resp.json()["status"] == "COMPLETED"

    # Verify inventory automatically incremented to 50
    inv_resp = await client.get(f"/api/v1/inventory?warehouse_id={wh_id}&product_id={prod_id}", headers=super_admin_headers)
    assert inv_resp.json()[0]["available_quantity"] == 50
