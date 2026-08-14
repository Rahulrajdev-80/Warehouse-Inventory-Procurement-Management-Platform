from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime

from app.models.inventory import Inventory, InventoryHistory, TransactionType
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.alert import Alert, AlertType
from app.websockets.connection_manager import ws_manager
from app.utils.redis_client import redis_client

class InventoryService:
    @staticmethod
    async def get_or_create_inventory(db: AsyncSession, product_id: int, warehouse_id: int) -> Inventory:
        result = await db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.warehouse_id == warehouse_id
            )
        )
        inv = result.scalars().first()
        if not inv:
            inv = Inventory(
                product_id=product_id,
                warehouse_id=warehouse_id,
                available_quantity=0,
                reserved_quantity=0,
                damaged_quantity=0
            )
            db.add(inv)
            await db.flush()
        return inv

    @staticmethod
    async def stock_in(
        db: AsyncSession, product_id: int, warehouse_id: int, quantity: int,
        reference_id: Optional[str] = None, user_id: Optional[int] = None
    ) -> Inventory:
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

        inv = await InventoryService.get_or_create_inventory(db, product_id, warehouse_id)
        inv.available_quantity += quantity
        inv.last_updated = datetime.utcnow()

        history = InventoryHistory(
            inventory_id=inv.id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            change_quantity=quantity,
            transaction_type=TransactionType.STOCK_IN,
            reference_id=reference_id,
            created_by_id=user_id
        )
        db.add(history)
        await db.commit()
        await db.refresh(inv)

        await redis_client.delete("analytics:dashboard")
        await ws_manager.broadcast("inventory", {
            "event": "STOCK_IN",
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "new_available": inv.available_quantity
        })
        return inv

    @staticmethod
    async def stock_out(
        db: AsyncSession, product_id: int, warehouse_id: int, quantity: int,
        reference_id: Optional[str] = None, user_id: Optional[int] = None
    ) -> Inventory:
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

        inv = await InventoryService.get_or_create_inventory(db, product_id, warehouse_id)
        if inv.available_quantity < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory. Requested {quantity}, available {inv.available_quantity}"
            )

        inv.available_quantity -= quantity
        inv.last_updated = datetime.utcnow()

        history = InventoryHistory(
            inventory_id=inv.id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            change_quantity=-quantity,
            transaction_type=TransactionType.STOCK_OUT,
            reference_id=reference_id,
            created_by_id=user_id
        )
        db.add(history)

        # Check for low stock alert
        product_res = await db.execute(select(Product).where(Product.id == product_id))
        product = product_res.scalars().first()

        if product:
            if inv.available_quantity == 0:
                alert = Alert(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    alert_type=AlertType.OUT_OF_STOCK,
                    current_quantity=0,
                    threshold_quantity=product.reorder_level,
                    message=f"Product {product.name} (SKU: {product.sku}) is OUT OF STOCK in warehouse #{warehouse_id}"
                )
                db.add(alert)
                await ws_manager.broadcast("alerts", {"event": "OUT_OF_STOCK", "product_id": product_id, "warehouse_id": warehouse_id})
            elif inv.available_quantity <= product.reorder_level:
                alert = Alert(
                    product_id=product_id,
                    warehouse_id=warehouse_id,
                    alert_type=AlertType.LOW_STOCK,
                    current_quantity=inv.available_quantity,
                    threshold_quantity=product.reorder_level,
                    message=f"Product {product.name} (SKU: {product.sku}) reached reorder level ({inv.available_quantity} <= {product.reorder_level}) in warehouse #{warehouse_id}"
                )
                db.add(alert)
                await ws_manager.broadcast("alerts", {"event": "LOW_STOCK", "product_id": product_id, "warehouse_id": warehouse_id})

        await db.commit()
        await db.refresh(inv)

        await redis_client.delete("analytics:dashboard")
        await ws_manager.broadcast("inventory", {
            "event": "STOCK_OUT",
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": quantity,
            "new_available": inv.available_quantity
        })
        return inv

    @staticmethod
    async def adjust_inventory(
        db: AsyncSession, product_id: int, warehouse_id: int,
        available_quantity: Optional[int] = None,
        damaged_quantity: Optional[int] = None,
        reserved_quantity: Optional[int] = None,
        reason: Optional[str] = "Adjustment",
        user_id: Optional[int] = None
    ) -> Inventory:
        inv = await InventoryService.get_or_create_inventory(db, product_id, warehouse_id)

        old_available = inv.available_quantity
        if available_quantity is not None:
            inv.available_quantity = available_quantity
        if damaged_quantity is not None:
            inv.damaged_quantity = damaged_quantity
        if reserved_quantity is not None:
            inv.reserved_quantity = reserved_quantity

        inv.last_updated = datetime.utcnow()
        diff = inv.available_quantity - old_available

        history = InventoryHistory(
            inventory_id=inv.id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            change_quantity=diff,
            transaction_type=TransactionType.ADJUSTMENT,
            reference_id=reason,
            created_by_id=user_id
        )
        db.add(history)
        await db.commit()
        await db.refresh(inv)

        await redis_client.delete("analytics:dashboard")
        await ws_manager.broadcast("inventory", {
            "event": "INVENTORY_ADJUSTED",
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "new_available": inv.available_quantity
        })
        return inv
