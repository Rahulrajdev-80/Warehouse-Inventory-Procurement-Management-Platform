from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models.inventory import Inventory, InventoryHistory
from app.models.user import User, UserRole
from app.schemas.inventory import (
    StockInRequest, StockOutRequest, AdjustInventoryRequest,
    InventoryResponse, InventoryHistoryResponse, ForecastResponse
)
from app.security import get_current_user, RequireRoles
from app.services.inventory_service import InventoryService
from app.services.forecasting_service import ForecastingService
from app.services.csv_service import CSVService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryResponse])
async def list_inventory(
    warehouse_id: Optional[int] = None,
    product_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """View Inventory across warehouses with optional filters"""
    stmt = select(Inventory).options(selectinload(Inventory.product), selectinload(Inventory.warehouse))
    if warehouse_id:
        stmt = stmt.where(Inventory.warehouse_id == warehouse_id)
    if product_id:
        stmt = stmt.where(Inventory.product_id == product_id)

    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/stock-in", response_model=InventoryResponse)
async def stock_in(
    data: StockInRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER, UserRole.INVENTORY_STAFF]))
):
    """Stock In (Add Quantity)"""
    inv = await InventoryService.stock_in(
        db, data.product_id, data.warehouse_id, data.quantity, data.reference_id, user.id
    )
    res = await db.execute(
        select(Inventory).options(selectinload(Inventory.product), selectinload(Inventory.warehouse)).where(Inventory.id == inv.id)
    )
    return res.scalars().first()

@router.post("/stock-out", response_model=InventoryResponse)
async def stock_out(
    data: StockOutRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER, UserRole.INVENTORY_STAFF]))
):
    """Stock Out (Deduct Quantity)"""
    inv = await InventoryService.stock_out(
        db, data.product_id, data.warehouse_id, data.quantity, data.reference_id, user.id
    )
    res = await db.execute(
        select(Inventory).options(selectinload(Inventory.product), selectinload(Inventory.warehouse)).where(Inventory.id == inv.id)
    )
    return res.scalars().first()

@router.post("/adjust", response_model=InventoryResponse)
async def adjust_inventory(
    data: AdjustInventoryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER, UserRole.INVENTORY_STAFF]))
):
    """Adjust Inventory (Count discrepancy / Damage)"""
    inv = await InventoryService.adjust_inventory(
        db, data.product_id, data.warehouse_id, data.available_quantity, data.damaged_quantity, data.reserved_quantity, data.reason, user.id
    )
    res = await db.execute(
        select(Inventory).options(selectinload(Inventory.product), selectinload(Inventory.warehouse)).where(Inventory.id == inv.id)
    )
    return res.scalars().first()

@router.get("/history", response_model=List[InventoryHistoryResponse])
async def get_inventory_history(
    warehouse_id: Optional[int] = None,
    product_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """View Inventory Transaction Logs"""
    stmt = select(InventoryHistory)
    if warehouse_id:
        stmt = stmt.where(InventoryHistory.warehouse_id == warehouse_id)
    if product_id:
        stmt = stmt.where(InventoryHistory.product_id == product_id)
    stmt = stmt.order_by(InventoryHistory.timestamp.desc())

    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/forecast/{product_id}", response_model=ForecastResponse)
async def get_inventory_forecast(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Predict future inventory requirements using moving average forecasting"""
    return await ForecastingService.get_product_forecast(db, product_id)

@router.post("/import-csv")
async def import_inventory_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Bulk import stock in inventory via CSV file"""
    return await CSVService.import_inventory_csv(db, file, user.id)
