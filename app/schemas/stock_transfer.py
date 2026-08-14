from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.stock_transfer import TransferStatus
from app.schemas.product import ProductResponse
from app.schemas.warehouse import WarehouseResponse

class TransferItemCreate(BaseModel):
    product_id: int
    quantity: int

class TransferCreate(BaseModel):
    source_warehouse_id: int
    destination_warehouse_id: int
    items: List[TransferItemCreate]

class TransferUpdate(BaseModel):
    source_warehouse_id: Optional[int] = None
    destination_warehouse_id: Optional[int] = None
    status: Optional[TransferStatus] = None

class TransferItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class TransferResponse(BaseModel):
    id: int
    transfer_number: str
    source_warehouse_id: int
    destination_warehouse_id: int
    status: TransferStatus
    requested_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    source_warehouse: Optional[WarehouseResponse] = None
    destination_warehouse: Optional[WarehouseResponse] = None
    items: List[TransferItemResponse] = []

    class Config:
        from_attributes = True
