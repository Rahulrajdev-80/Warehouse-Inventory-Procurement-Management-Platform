from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.purchase_order import POStatus
from app.schemas.product import ProductResponse
from app.schemas.supplier import SupplierResponse
from app.schemas.warehouse import WarehouseResponse

class POItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class POCreate(BaseModel):
    supplier_id: int
    warehouse_id: int
    expected_delivery_date: Optional[datetime] = None
    items: List[POItemCreate]

class POUpdate(BaseModel):
    supplier_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    expected_delivery_date: Optional[datetime] = None
    status: Optional[POStatus] = None

class POReceiveItem(BaseModel):
    product_id: int
    received_quantity: int

class POReceiveRequest(BaseModel):
    items: List[POReceiveItem]

class POItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    received_quantity: int
    unit_price: float
    total_price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class POResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    warehouse_id: int
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    status: POStatus
    total_amount: float
    created_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    supplier: Optional[SupplierResponse] = None
    warehouse: Optional[WarehouseResponse] = None
    items: List[POItemResponse] = []

    class Config:
        from_attributes = True
