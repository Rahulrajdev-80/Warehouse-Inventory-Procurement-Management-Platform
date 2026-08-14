from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.supplier import Supplier, SupplierStatus
from app.models.purchase_order import PurchaseOrder
from app.models.user import User, UserRole
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.schemas.purchase_order import POResponse
from app.security import get_current_user, RequireRoles

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.PROCUREMENT_OFFICER]))
):
    """Add new supplier"""
    existing = await db.execute(select(Supplier).where(Supplier.email == data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Supplier email already exists")

    supplier_data = data.model_dump() if hasattr(data, 'model_dump') else data.dict()
    supplier = Supplier(**supplier_data)
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier

@router.get("", response_model=List[SupplierResponse])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all suppliers"""
    res = await db.execute(select(Supplier))
    return res.scalars().all()

@router.get("/{id}", response_model=SupplierResponse)
async def get_supplier(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get supplier by ID"""
    res = await db.execute(select(Supplier).where(Supplier.id == id))
    sup = res.scalars().first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return sup

@router.put("/{id}", response_model=SupplierResponse)
async def update_supplier(
    id: int,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.PROCUREMENT_OFFICER]))
):
    """Update supplier details"""
    res = await db.execute(select(Supplier).where(Supplier.id == id))
    sup = res.scalars().first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sup, key, value)

    await db.commit()
    await db.refresh(sup)
    return sup

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def suspend_supplier(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.PROCUREMENT_OFFICER]))
):
    """Suspend supplier"""
    res = await db.execute(select(Supplier).where(Supplier.id == id))
    sup = res.scalars().first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")
    sup.status = SupplierStatus.SUSPENDED
    await db.commit()
    return None

@router.get("/{id}/history")
async def get_supplier_purchase_history(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """View purchase order history for a supplier"""
    res = await db.execute(select(PurchaseOrder).where(PurchaseOrder.supplier_id == id))
    pos = res.scalars().all()
    return pos
