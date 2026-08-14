from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db

from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
    POStatus,
)

from app.models.user import User, UserRole

from app.schemas.purchase_order import (
    POCreate,
    POUpdate,
    POReceiveRequest,
    POResponse,
)

from app.security import (
    get_current_user,
    RequireRoles,
)

from app.services.po_service import POService


router = APIRouter(
    prefix="/purchase-orders",
    tags=["Purchase Orders"],
)


# ============================================================
# COMMON PURCHASE ORDER LOAD
# ============================================================
#
# IMPORTANT:
# PurchaseOrder -> items -> product
# must be eagerly loaded.
#
# Otherwise FastAPI/Pydantic response serialization can cause:
#
# MissingGreenlet:
# greenlet_spawn has not been called
#
# ============================================================

def purchase_order_load_options():
    return (
        selectinload(PurchaseOrder.items)
        .selectinload(PurchaseOrderItem.product),

        selectinload(PurchaseOrder.supplier),

        selectinload(PurchaseOrder.warehouse),
    )


# ============================================================
# LOAD ONE PURCHASE ORDER
# ============================================================

async def load_purchase_order(
    db: AsyncSession,
    po_id: int,
) -> Optional[PurchaseOrder]:

    result = await db.execute(
        select(PurchaseOrder)
        .options(*purchase_order_load_options())
        .where(PurchaseOrder.id == po_id)
    )

    return result.scalar_one_or_none()


# ============================================================
# CREATE PURCHASE ORDER
# ============================================================

@router.post(
    "",
    response_model=POResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_purchase_order(
    data: POCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(
        RequireRoles(
            [
                UserRole.SUPER_ADMIN,
                UserRole.WAREHOUSE_MANAGER,
                UserRole.PROCUREMENT_OFFICER,
            ]
        )
    ),
):
    """
    Create Purchase Order.
    """

    po = await POService.create_po(
        db=db,
        data=data,
        user_id=user.id,
    )

    # Reload with ALL response relationships.
    # This guarantees product/supplier/warehouse
    # are already available before Pydantic serialization.

    loaded_po = await load_purchase_order(
        db=db,
        po_id=po.id,
    )

    if loaded_po is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Purchase Order was created but could not be loaded",
        )

    return loaded_po


# ============================================================
# LIST PURCHASE ORDERS
# ============================================================

@router.get(
    "",
    response_model=List[POResponse],
)
async def list_purchase_orders(
    supplier_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    status_filter: Optional[POStatus] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    List Purchase Orders.
    """

    stmt = (
        select(PurchaseOrder)
        .options(*purchase_order_load_options())
    )

    # --------------------------------------------------------
    # Optional supplier filter
    # --------------------------------------------------------

    if supplier_id is not None:
        stmt = stmt.where(
            PurchaseOrder.supplier_id == supplier_id
        )

    # --------------------------------------------------------
    # Optional warehouse filter
    # --------------------------------------------------------

    if warehouse_id is not None:
        stmt = stmt.where(
            PurchaseOrder.warehouse_id == warehouse_id
        )

    # --------------------------------------------------------
    # Optional status filter
    # --------------------------------------------------------

    if status_filter is not None:
        stmt = stmt.where(
            PurchaseOrder.status == status_filter
        )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    result = await db.execute(stmt)

    return result.scalars().unique().all()


# ============================================================
# GET PURCHASE ORDER BY ID
# ============================================================

@router.get(
    "/{id}",
    response_model=POResponse,
)
async def get_purchase_order(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get Purchase Order Details.
    """

    po = await load_purchase_order(
        db=db,
        po_id=id,
    )

    if po is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase Order not found",
        )

    return po


# ============================================================
# UPDATE PURCHASE ORDER
# ============================================================

@router.put(
    "/{id}",
    response_model=POResponse,
)
async def update_purchase_order(
    id: int,
    data: POUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(
        RequireRoles(
            [
                UserRole.SUPER_ADMIN,
                UserRole.WAREHOUSE_MANAGER,
                UserRole.PROCUREMENT_OFFICER,
            ]
        )
    ),
):
    """
    Update Purchase Order.
    """

    po = await load_purchase_order(
        db=db,
        po_id=id,
    )

    if po is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase Order not found",
        )

    # --------------------------------------------------------
    # Extract only fields actually supplied by the client
    # --------------------------------------------------------

    if hasattr(data, "model_dump"):
        update_data = data.model_dump(
            exclude_unset=True
        )
    else:
        update_data = data.dict(
            exclude_unset=True
        )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    for key, value in update_data.items():

        # Don't accidentally modify primary key.
        if key == "id":
            continue

        setattr(po, key, value)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    await db.commit()

    # IMPORTANT:
    # Do NOT use db.refresh(po) here for the response.
    #
    # Re-query with selectinload so product/supplier/warehouse
    # are loaded before FastAPI serializes the response.
    # --------------------------------------------------------

    updated_po = await load_purchase_order(
        db=db,
        po_id=id,
    )

    if updated_po is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Purchase Order was updated but could not be loaded",
        )

    return updated_po


# ============================================================
# CANCEL PURCHASE ORDER
# ============================================================

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_purchase_order(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(
        RequireRoles(
            [
                UserRole.SUPER_ADMIN,
                UserRole.PROCUREMENT_OFFICER,
            ]
        )
    ),
):
    """
    Cancel Purchase Order.
    """

    po = await load_purchase_order(
        db=db,
        po_id=id,
    )

    if po is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase Order not found",
        )

    # --------------------------------------------------------
    # Cancel PO
    # --------------------------------------------------------

    po.status = POStatus.CANCELLED

    await db.commit()

    return None


# ============================================================
# APPROVE PURCHASE ORDER
# ============================================================

@router.post(
    "/{id}/approve",
    response_model=POResponse,
)
async def approve_purchase_order(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(
        RequireRoles(
            [
                UserRole.SUPER_ADMIN,
                UserRole.PROCUREMENT_OFFICER,
            ]
        )
    ),
):
    """
    Approve Purchase Order.
    """

    await POService.approve_po(
        db=db,
        po_id=id,
        user_id=user.id,
    )

    # Reload completely so the response does not trigger
    # lazy loading of product.
    approved_po = await load_purchase_order(
        db=db,
        po_id=id,
    )

    if approved_po is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase Order not found after approval",
        )

    return approved_po


# ============================================================
# RECEIVE PURCHASE ORDER GOODS
# ============================================================

@router.post(
    "/{id}/receive",
    response_model=POResponse,
)
async def receive_purchase_order_goods(
    id: int,
    data: POReceiveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(
        RequireRoles(
            [
                UserRole.SUPER_ADMIN,
                UserRole.WAREHOUSE_MANAGER,
            ]
        )
    ),
):
    """
    Receive Goods for Purchase Order.

    Receiving goods also updates warehouse inventory.
    """

    await POService.receive_goods(
        db=db,
        po_id=id,
        data=data,
        user_id=user.id,
    )

    # Reload complete PO with product relationship.
    received_po = await load_purchase_order(
        db=db,
        po_id=id,
    )

    if received_po is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase Order not found after receiving goods",
        )

    return received_po