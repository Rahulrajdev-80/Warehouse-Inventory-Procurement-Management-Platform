from datetime import datetime
from typing import List
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
    POStatus,
)
from app.models.supplier import Supplier, SupplierStatus
from app.models.warehouse import Warehouse
from app.models.product import Product

from app.schemas.purchase_order import (
    POCreate,
    POReceiveRequest,
)

from app.services.inventory_service import InventoryService
from app.websockets.connection_manager import ws_manager
from app.utils.email_notifier import EmailNotifier


class POService:

    # ============================================================
    # COMMON PURCHASE ORDER LOADER
    # ============================================================

    @staticmethod
    async def _get_po(
        db: AsyncSession,
        po_id: int,
    ) -> PurchaseOrder | None:
        """
        Load a Purchase Order together with every relationship
        required by POResponse / POItemResponse.

        IMPORTANT:
        PurchaseOrderItem.product MUST be eagerly loaded.
        Otherwise FastAPI/Pydantic can trigger MissingGreenlet
        during response serialization.
        """

        result = await db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items)
                .selectinload(PurchaseOrderItem.product),

                selectinload(PurchaseOrder.supplier),

                selectinload(PurchaseOrder.warehouse),
            )
            .where(PurchaseOrder.id == po_id)
        )

        return result.scalars().first()

    # ============================================================
    # CREATE PURCHASE ORDER
    # ============================================================

    @staticmethod
    async def create_po(
        db: AsyncSession,
        data: POCreate,
        user_id: int,
    ) -> PurchaseOrder:

        # --------------------------------------------------------
        # Check supplier
        # --------------------------------------------------------

        supplier_result = await db.execute(
            select(Supplier).where(
                Supplier.id == data.supplier_id
            )
        )

        supplier = supplier_result.scalars().first()

        if not supplier:
            raise HTTPException(
                status_code=400,
                detail="Supplier not found",
            )

        if supplier.status == SupplierStatus.SUSPENDED:
            raise HTTPException(
                status_code=400,
                detail="Supplier is suspended",
            )

        # --------------------------------------------------------
        # Check warehouse
        # --------------------------------------------------------

        warehouse_result = await db.execute(
            select(Warehouse).where(
                Warehouse.id == data.warehouse_id
            )
        )

        warehouse = warehouse_result.scalars().first()

        if not warehouse:
            raise HTTPException(
                status_code=400,
                detail="Warehouse not found",
            )

        # --------------------------------------------------------
        # Validate items
        # --------------------------------------------------------

        if not data.items:
            raise HTTPException(
                status_code=400,
                detail="Purchase Order must contain at least one item",
            )

        # --------------------------------------------------------
        # Generate PO number
        # --------------------------------------------------------

        po_number = (
            f"PO-"
            f"{datetime.utcnow().strftime('%Y%m%d')}-"
            f"{uuid.uuid4().hex[:6].upper()}"
        )

        total_amount = 0.0
        po_items: List[PurchaseOrderItem] = []

        # --------------------------------------------------------
        # Validate every product
        # --------------------------------------------------------

        for item in data.items:

            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Quantity must be greater than 0 "
                        f"for Product ID {item.product_id}"
                    ),
                )

            if item.unit_price < 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Unit price cannot be negative "
                        f"for Product ID {item.product_id}"
                    ),
                )

            product_result = await db.execute(
                select(Product).where(
                    Product.id == item.product_id
                )
            )

            product = product_result.scalars().first()

            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product ID {item.product_id} "
                        f"not found"
                    ),
                )

            if product.is_archived:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product ID {item.product_id} "
                        f"is archived"
                    ),
                )

            line_total = (
                item.quantity * item.unit_price
            )

            total_amount += line_total

            po_items.append(
                PurchaseOrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    received_quantity=0,
                    unit_price=item.unit_price,
                    total_price=line_total,
                )
            )

        # --------------------------------------------------------
        # Create Purchase Order
        # --------------------------------------------------------

        po = PurchaseOrder(
            po_number=po_number,
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            expected_delivery_date=data.expected_delivery_date,
            status=POStatus.DRAFT,
            total_amount=total_amount,
            created_by_id=user_id,
            items=po_items,
        )

        db.add(po)

        try:
            await db.commit()

        except Exception:
            await db.rollback()
            raise

        # --------------------------------------------------------
        # Reload PO with ALL required relationships
        # --------------------------------------------------------

        created_po = await POService._get_po(
            db=db,
            po_id=po.id,
        )

        if created_po is None:
            raise HTTPException(
                status_code=500,
                detail="Purchase Order was created but could not be loaded",
            )

        return created_po

    # ============================================================
    # APPROVE PURCHASE ORDER
    # ============================================================

    @staticmethod
    async def approve_po(
        db: AsyncSession,
        po_id: int,
        user_id: int,
    ) -> PurchaseOrder:

        # --------------------------------------------------------
        # Load PO + items + product + supplier + warehouse
        # --------------------------------------------------------

        po = await POService._get_po(
            db=db,
            po_id=po_id,
        )

        if not po:
            raise HTTPException(
                status_code=404,
                detail="Purchase Order not found",
            )

        # --------------------------------------------------------
        # Validate current status
        # --------------------------------------------------------

        if po.status not in (
            POStatus.DRAFT,
            POStatus.PENDING_APPROVAL,
        ):
            status_value = getattr(
                po.status,
                "value",
                str(po.status),
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot approve PO in "
                    f"'{status_value}' state"
                ),
            )

        # --------------------------------------------------------
        # Approve
        # --------------------------------------------------------

        po.status = POStatus.APPROVED
        po.approved_by_id = user_id
        po.updated_at = datetime.utcnow()

        try:
            await db.commit()

        except Exception:
            await db.rollback()
            raise

        # --------------------------------------------------------
        # IMPORTANT:
        # Reload after commit so relationships remain safely
        # available for FastAPI response serialization.
        # --------------------------------------------------------

        approved_po = await POService._get_po(
            db=db,
            po_id=po_id,
        )

        if approved_po is None:
            raise HTTPException(
                status_code=500,
                detail="Purchase Order approved but could not be reloaded",
            )

        # --------------------------------------------------------
        # WebSocket notification
        # --------------------------------------------------------

        await ws_manager.broadcast(
            "alerts",
            {
                "event": "PO_APPROVED",
                "po_id": approved_po.id,
                "po_number": approved_po.po_number,
                "total_amount": approved_po.total_amount,
            },
        )

        # --------------------------------------------------------
        # Email notification
        # --------------------------------------------------------

        supplier_email = (
            approved_po.supplier.email
            if approved_po.supplier
            else "manager@warehouse.com"
        )

        EmailNotifier.send_email(
            to_email=supplier_email,
            subject=(
                f"Purchase Order Approved: "
                f"{approved_po.po_number}"
            ),
            body=(
                f"Purchase Order "
                f"{approved_po.po_number} "
                f"has been approved for total amount "
                f"${approved_po.total_amount:.2f}"
            ),
        )

        return approved_po

    # ============================================================
    # RECEIVE GOODS
    # ============================================================

    @staticmethod
    async def receive_goods(
        db: AsyncSession,
        po_id: int,
        data: POReceiveRequest,
        user_id: int,
    ) -> PurchaseOrder:

        # --------------------------------------------------------
        # Load PO + items + product + supplier + warehouse
        # --------------------------------------------------------

        po = await POService._get_po(
            db=db,
            po_id=po_id,
        )

        if not po:
            raise HTTPException(
                status_code=404,
                detail="Purchase Order not found",
            )

        # --------------------------------------------------------
        # Validate PO status
        # --------------------------------------------------------

        allowed_statuses = (
            POStatus.APPROVED,
            POStatus.ORDERED,
            POStatus.PARTIALLY_RECEIVED,
        )

        if po.status not in allowed_statuses:

            status_value = getattr(
                po.status,
                "value",
                str(po.status),
            )

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot receive goods for PO in "
                    f"'{status_value}' state"
                ),
            )

        # --------------------------------------------------------
        # Validate receive request
        # --------------------------------------------------------

        if not data.items:
            raise HTTPException(
                status_code=400,
                detail="At least one item is required",
            )

        # --------------------------------------------------------
        # Map PO items by product ID
        # --------------------------------------------------------

        item_map = {
            item.product_id: item
            for item in po.items
        }

        # --------------------------------------------------------
        # Receive each item
        # --------------------------------------------------------

        for recv_item in data.items:

            if recv_item.product_id not in item_map:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Product {recv_item.product_id} "
                        f"is not part of this PO"
                    ),
                )

            po_item = item_map[
                recv_item.product_id
            ]

            qty_to_add = recv_item.received_quantity

            if qty_to_add <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Received quantity must be "
                        f"greater than 0 for Product "
                        f"{recv_item.product_id}"
                    ),
                )

            current_received = (
                po_item.received_quantity or 0
            )

            ordered_quantity = (
                po_item.quantity or 0
            )

            if (
                current_received + qty_to_add
                > ordered_quantity
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Received quantity exceeds "
                        f"ordered quantity for Product "
                        f"{recv_item.product_id}"
                    ),
                )

            # ----------------------------------------------------
            # Update received quantity
            # ----------------------------------------------------

            po_item.received_quantity = (
                current_received + qty_to_add
            )

            # ----------------------------------------------------
            # Update inventory
            # ----------------------------------------------------

            await InventoryService.stock_in(
                db=db,
                product_id=recv_item.product_id,
                warehouse_id=po.warehouse_id,
                quantity=qty_to_add,
                reference_id=(
                    f"PO-RECEIPT-{po.po_number}"
                ),
                user_id=user_id,
            )

        # --------------------------------------------------------
        # Recalculate PO status
        # --------------------------------------------------------

        all_completed = all(
            (item.received_quantity or 0)
            >= (item.quantity or 0)
            for item in po.items
        )

        any_received = any(
            (item.received_quantity or 0) > 0
            for item in po.items
        )

        if all_completed:
            po.status = POStatus.COMPLETED

        elif any_received:
            po.status = POStatus.PARTIALLY_RECEIVED

        po.updated_at = datetime.utcnow()

        # --------------------------------------------------------
        # Commit
        # --------------------------------------------------------

        try:
            await db.commit()

        except Exception:
            await db.rollback()
            raise

        # --------------------------------------------------------
        # Reload everything before returning
        # This is important for async SQLAlchemy + Pydantic.
        # --------------------------------------------------------

        updated_po = await POService._get_po(
            db=db,
            po_id=po_id,
        )

        if updated_po is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Goods received successfully but "
                    "Purchase Order could not be reloaded"
                ),
            )

        # --------------------------------------------------------
        # WebSocket notification
        # --------------------------------------------------------

        status_value = getattr(
            updated_po.status,
            "value",
            str(updated_po.status),
        )

        await ws_manager.broadcast(
            "alerts",
            {
                "event": "STOCK_RECEIVED",
                "po_id": updated_po.id,
                "po_number": updated_po.po_number,
                "status": status_value,
            },
        )

        return updated_po