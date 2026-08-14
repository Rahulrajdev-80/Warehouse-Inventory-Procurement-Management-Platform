from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.stock_transfer import StockTransfer, TransferStatus
from app.models.user import User, UserRole
from app.schemas.stock_transfer import TransferCreate, TransferUpdate, TransferResponse
from app.security import get_current_user, RequireRoles
from app.services.transfer_service import TransferService

router = APIRouter(prefix="/transfers", tags=["Stock Transfers"])

@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_transfer(
    data: TransferCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER, UserRole.INVENTORY_STAFF]))
):
    """Create Stock Transfer Request"""
    return await TransferService.create_transfer(db, data, user.id)

@router.get("", response_model=List[TransferResponse])
async def list_stock_transfers(
    source_warehouse_id: Optional[int] = None,
    destination_warehouse_id: Optional[int] = None,
    status_filter: Optional[TransferStatus] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List Stock Transfer Requests"""
    stmt = select(StockTransfer).options(
        selectinload(StockTransfer.items),
        selectinload(StockTransfer.source_warehouse),
        selectinload(StockTransfer.destination_warehouse)
    )
    if source_warehouse_id:
        stmt = stmt.where(StockTransfer.source_warehouse_id == source_warehouse_id)
    if destination_warehouse_id:
        stmt = stmt.where(StockTransfer.destination_warehouse_id == destination_warehouse_id)
    if status_filter:
        stmt = stmt.where(StockTransfer.status == status_filter)

    res = await db.execute(stmt)
    return res.scalars().all()

@router.put("/{id}", response_model=TransferResponse)
async def update_stock_transfer(
    id: int,
    data: TransferUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Update Transfer Details"""
    stmt = select(StockTransfer).options(
        selectinload(StockTransfer.items),
        selectinload(StockTransfer.source_warehouse),
        selectinload(StockTransfer.destination_warehouse)
    ).where(StockTransfer.id == id)

    res = await db.execute(stmt)
    transfer = res.scalars().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer request not found")

    update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transfer, key, value)

    await db.commit()
    await db.refresh(transfer)
    return transfer

@router.post("/{id}/approve", response_model=TransferResponse)
async def approve_stock_transfer(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Approve Stock Transfer Request (Deducts stock from source)"""
    return await TransferService.approve_transfer(db, id, user.id)

@router.post("/{id}/receive", response_model=TransferResponse)
async def receive_stock_transfer(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Receive Stock Transfer (Adds stock to destination)"""
    return await TransferService.receive_transfer(db, id, user.id)
