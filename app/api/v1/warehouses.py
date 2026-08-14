from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.warehouse import Warehouse, WarehouseStatus
from app.models.user import User, UserRole
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseAssignManager, WarehouseResponse
from app.security import get_current_user, RequireRoles

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN]))
):
    """Create new warehouse (Super Admin only)"""
    existing = await db.execute(select(Warehouse).where(Warehouse.code == data.code))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Warehouse code already exists")

    wh = Warehouse(
        name=data.name,
        code=data.code,
        address=data.address,
        capacity=data.capacity,
        manager_id=data.manager_id
    )
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh

@router.get("", response_model=List[WarehouseResponse])
async def list_warehouses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all warehouses"""
    res = await db.execute(select(Warehouse))
    return res.scalars().all()

@router.get("/{id}", response_model=WarehouseResponse)
async def get_warehouse(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get warehouse details by ID"""
    res = await db.execute(select(Warehouse).where(Warehouse.id == id))
    wh = res.scalars().first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return wh

@router.put("/{id}", response_model=WarehouseResponse)
async def update_warehouse(
    id: int,
    data: WarehouseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Update warehouse details"""
    res = await db.execute(select(Warehouse).where(Warehouse.id == id))
    wh = res.scalars().first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wh, key, value)

    await db.commit()
    await db.refresh(wh)
    return wh

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_warehouse(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN]))
):
    """Disable warehouse (Soft delete / status change)"""
    res = await db.execute(select(Warehouse).where(Warehouse.id == id))
    wh = res.scalars().first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    wh.status = WarehouseStatus.DISABLED
    await db.commit()
    return None
