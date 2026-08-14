from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.stock_transfer import StockTransfer, StockTransferItem, TransferStatus
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory, TransactionType, InventoryHistory
from app.schemas.stock_transfer import TransferCreate
from app.services.inventory_service import InventoryService
from app.websockets.connection_manager import ws_manager
from app.utils.redis_client import redis_client
from app.utils.email_notifier import EmailNotifier

class TransferService:
    @staticmethod
    async def create_transfer(db: AsyncSession, data: TransferCreate, user_id: int) -> StockTransfer:
        if data.source_warehouse_id == data.destination_warehouse_id:
            raise HTTPException(status_code=400, detail="Source and destination warehouses cannot be the same")

        wh_src = await db.execute(select(Warehouse).where(Warehouse.id == data.source_warehouse_id))
        wh_dst = await db.execute(select(Warehouse).where(Warehouse.id == data.destination_warehouse_id))
        if not wh_src.scalars().first() or not wh_dst.scalars().first():
            raise HTTPException(status_code=400, detail="Invalid source or destination warehouse")

        transfer_number = f"TR-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        transfer_items = []

        for item in data.items:
            # Check available stock at source
            inv_res = await db.execute(
                select(Inventory).where(
                    Inventory.product_id == item.product_id,
                    Inventory.warehouse_id == data.source_warehouse_id
                )
            )
            inv = inv_res.scalars().first()
            if not inv or inv.available_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient available quantity for product {item.product_id} at source warehouse"
                )

            transfer_items.append(
                StockTransferItem(
                    product_id=item.product_id,
                    quantity=item.quantity
                )
            )

        transfer = StockTransfer(
            transfer_number=transfer_number,
            source_warehouse_id=data.source_warehouse_id,
            destination_warehouse_id=data.destination_warehouse_id,
            status=TransferStatus.REQUESTED,
            requested_by_id=user_id,
            items=transfer_items
        )
        db.add(transfer)
        await db.commit()

        res = await db.execute(
            select(StockTransfer)
            .options(
                selectinload(StockTransfer.items),
                selectinload(StockTransfer.source_warehouse),
                selectinload(StockTransfer.destination_warehouse)
            )
            .where(StockTransfer.id == transfer.id)
        )
        return res.scalars().first()

    @staticmethod
    async def approve_transfer(db: AsyncSession, transfer_id: int, user_id: int) -> StockTransfer:
        res = await db.execute(
            select(StockTransfer)
            .options(
                selectinload(StockTransfer.items),
                selectinload(StockTransfer.source_warehouse),
                selectinload(StockTransfer.destination_warehouse)
            )
            .where(StockTransfer.id == transfer_id)
        )
        transfer = res.scalars().first()
        if not transfer:
            raise HTTPException(status_code=404, detail="Stock transfer not found")
        if transfer.status != TransferStatus.REQUESTED:
            raise HTTPException(status_code=400, detail=f"Cannot approve transfer in '{transfer.status}' state")

        # Reserve and deduct from source warehouse
        for item in transfer.items:
            await InventoryService.stock_out(
                db=db,
                product_id=item.product_id,
                warehouse_id=transfer.source_warehouse_id,
                quantity=item.quantity,
                reference_id=f"TRANSFER-OUT-{transfer.transfer_number}",
                user_id=user_id
            )

        transfer.status = TransferStatus.IN_TRANSIT
        transfer.approved_by_id = user_id
        transfer.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(transfer)

        await ws_manager.broadcast("transfers", {
            "event": "TRANSFER_APPROVED",
            "transfer_id": transfer.id,
            "transfer_number": transfer.transfer_number
        })
        return transfer

    @staticmethod
    async def receive_transfer(db: AsyncSession, transfer_id: int, user_id: int) -> StockTransfer:
        res = await db.execute(
            select(StockTransfer)
            .options(
                selectinload(StockTransfer.items),
                selectinload(StockTransfer.source_warehouse),
                selectinload(StockTransfer.destination_warehouse)
            )
            .where(StockTransfer.id == transfer_id)
        )
        transfer = res.scalars().first()
        if not transfer:
            raise HTTPException(status_code=404, detail="Stock transfer not found")
        if transfer.status != TransferStatus.IN_TRANSIT:
            raise HTTPException(status_code=400, detail=f"Cannot receive transfer in '{transfer.status}' state")

        # Stock in at destination warehouse
        for item in transfer.items:
            await InventoryService.stock_in(
                db=db,
                product_id=item.product_id,
                warehouse_id=transfer.destination_warehouse_id,
                quantity=item.quantity,
                reference_id=f"TRANSFER-IN-{transfer.transfer_number}",
                user_id=user_id
            )

        transfer.status = TransferStatus.RECEIVED
        transfer.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(transfer)

        await ws_manager.broadcast("transfers", {
            "event": "TRANSFER_RECEIVED",
            "transfer_id": transfer.id,
            "transfer_number": transfer.transfer_number
        })
        EmailNotifier.send_email(
            to_email="manager@warehouse.com",
            subject=f"Transfer Completed: {transfer.transfer_number}",
            body=f"Stock Transfer {transfer.transfer_number} received at destination warehouse."
        )
        return transfer
