from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    brand: str
    unit: str = "pcs"
    cost_price: float
    selling_price: float
    reorder_level: int = 10
    barcode: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    reorder_level: Optional[int] = None
    barcode: Optional[str] = None
    is_archived: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    brand: str
    unit: str
    cost_price: float
    selling_price: float
    reorder_level: int
    barcode: Optional[str] = None
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
