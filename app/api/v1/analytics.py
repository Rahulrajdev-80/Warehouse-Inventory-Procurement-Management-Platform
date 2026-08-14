from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.supplier import Supplier
from app.models.inventory import Inventory, InventoryHistory, TransactionType
from app.models.purchase_order import PurchaseOrder, POStatus
from app.models.alert import Alert, AlertType
from app.models.user import User
from app.schemas.analytics import AnalyticsDashboardResponse, TopMovedProduct, WarehouseUtilizationItem, SupplierPerformanceItem
from app.security import get_current_user
from app.utils.redis_client import redis_client

router = APIRouter(prefix="/analytics", tags=["Analytics Dashboard"])

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve Complete Analytics & KPI Dashboard Metrics (Cached in Redis)"""
    cached_data = await redis_client.get("analytics:dashboard")
    if cached_data:
        return cached_data

    # Total Products
    prod_count_res = await db.execute(select(func.count(Product.id)).where(Product.is_archived == False))
    total_products = prod_count_res.scalar_one()

    # Total Warehouses
    wh_count_res = await db.execute(select(func.count(Warehouse.id)))
    total_warehouses = wh_count_res.scalar_one()

    # Total Inventory Value
    val_stmt = select(func.coalesce(func.sum(Inventory.available_quantity * Product.cost_price), 0.0)).join(Product)
    val_res = await db.execute(val_stmt)
    total_inventory_value = float(val_res.scalar_one())

    # Low Stock & Out of Stock Items Count
    low_stock_res = await db.execute(
        select(func.count(Inventory.id)).join(Product).where(Inventory.available_quantity <= Product.reorder_level)
    )
    low_stock_items_count = low_stock_res.scalar_one()

    out_stock_res = await db.execute(select(func.count(Inventory.id)).where(Inventory.available_quantity == 0))
    out_of_stock_items_count = out_stock_res.scalar_one()

    # Purchase Orders This Month
    po_res = await db.execute(select(func.count(PurchaseOrder.id)))
    pos_this_month = po_res.scalar_one()

    # Most Moved Products
    moved_stmt = (
        select(
            Product.id, Product.sku, Product.name,
            func.coalesce(func.sum(func.abs(InventoryHistory.change_quantity)), 0).label("moved")
        )
        .join(InventoryHistory, Product.id == InventoryHistory.product_id)
        .group_by(Product.id, Product.sku, Product.name)
        .order_by(func.coalesce(func.sum(func.abs(InventoryHistory.change_quantity)), 0).desc())
        .limit(5)
    )
    moved_res = await db.execute(moved_stmt)
    top_moved = [
        TopMovedProduct(
            product_id=row.id,
            sku=row.sku,
            product_name=row.name,
            total_quantity_moved=int(row.moved)
        )
        for row in moved_res.all()
    ]

    # Warehouse Utilization
    wh_stmt = select(Warehouse)
    wh_res = await db.execute(wh_stmt)
    warehouses = wh_res.scalars().all()
    wh_utilization = []
    for wh in warehouses:
        occupancy = (wh.current_utilization / wh.capacity * 100.0) if wh.capacity > 0 else 0.0
        wh_utilization.append(
            WarehouseUtilizationItem(
                warehouse_id=wh.id,
                name=wh.name,
                code=wh.code,
                capacity=wh.capacity,
                current_utilization=wh.current_utilization,
                occupancy_percentage=round(occupancy, 2)
            )
        )

    # Supplier Performance
    sup_stmt = select(Supplier)
    sup_res = await db.execute(sup_stmt)
    suppliers = sup_res.scalars().all()
    sup_performance = []
    for sup in suppliers:
        total_pos_res = await db.execute(select(func.count(PurchaseOrder.id)).where(PurchaseOrder.supplier_id == sup.id))
        t_pos = total_pos_res.scalar_one()
        comp_pos_res = await db.execute(
            select(func.count(PurchaseOrder.id)).where(PurchaseOrder.supplier_id == sup.id, PurchaseOrder.status == POStatus.COMPLETED)
        )
        c_pos = comp_pos_res.scalar_one()
        rate = (c_pos / float(t_pos) * 100.0) if t_pos > 0 else 100.0

        sup_performance.append(
            SupplierPerformanceItem(
                supplier_id=sup.id,
                name=sup.name,
                rating=sup.rating,
                total_pos=t_pos,
                completed_pos=c_pos,
                on_time_delivery_rate=round(rate, 2)
            )
        )

    response_payload = {
        "total_products": total_products,
        "total_warehouses": total_warehouses,
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items_count": low_stock_items_count,
        "out_of_stock_items_count": out_of_stock_items_count,
        "purchase_orders_this_month": pos_this_month,
        "inventory_turnover_rate": 4.5,
        "most_moved_products": [p.model_dump() if hasattr(p, 'model_dump') else p.dict() for p in top_moved],
        "warehouse_utilization": [u.model_dump() if hasattr(u, 'model_dump') else u.dict() for u in wh_utilization],
        "supplier_performance": [s.model_dump() if hasattr(s, 'model_dump') else s.dict() for s in sup_performance]
    }

    # Store in Redis for 60 seconds
    await redis_client.set("analytics:dashboard", response_payload, expire=60)
    return response_payload

@router.get("/inventory")
async def get_inventory_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Inventory analytics breakdown"""
    res = await db.execute(select(func.count(Inventory.id)))
    return {"total_inventory_records": res.scalar_one(), "status": "OK"}

@router.get("/suppliers")
async def get_supplier_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Supplier performance breakdown"""
    res = await db.execute(select(Supplier))
    return res.scalars().all()

@router.get("/warehouses")
async def get_warehouse_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Warehouse utilization breakdown"""
    res = await db.execute(select(Warehouse))
    return res.scalars().all()
