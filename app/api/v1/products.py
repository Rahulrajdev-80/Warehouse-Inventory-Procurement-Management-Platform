from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.security import get_current_user, RequireRoles
from app.services.barcode_service import BarcodeService
from app.services.csv_service import CSVService

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Add Product"""
    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Product with this SKU already exists")

    prod_data = data.model_dump() if hasattr(data, 'model_dump') else data.dict()
    product = Product(**prod_data)
    if not product.barcode:
        product.barcode = data.sku
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.get("", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List & Filter Products by Category, SKU, or Name"""
    stmt = select(Product).where(Product.is_archived == False)
    if category:
        stmt = stmt.where(Product.category == category)
    if search:
        stmt = stmt.where(
            (Product.name.ilike(f"%{search}%")) | (Product.sku.ilike(f"%{search}%"))
        )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{id}", response_model=ProductResponse)
async def get_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get product details"""
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=ProductResponse)
async def update_product(
    id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Update product details"""
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_product(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN]))
):
    """Archive product (Soft delete)"""
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_archived = True
    await db.commit()
    return None

@router.get("/{id}/barcode")
async def get_product_barcode(
    id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate and return SVG Barcode for product SKU"""
    res = await db.execute(select(Product).where(Product.id == id))
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    svg_content = BarcodeService.generate_sku_barcode_svg(product.sku)
    return Response(content=svg_content, media_type="image/svg+xml")

@router.post("/import-csv")
async def import_products_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(RequireRoles([UserRole.SUPER_ADMIN, UserRole.WAREHOUSE_MANAGER]))
):
    """Bulk import products via CSV file"""
    return await CSVService.import_products_csv(db, file)
