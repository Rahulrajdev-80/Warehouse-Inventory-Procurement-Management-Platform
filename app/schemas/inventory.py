from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.inventory import TransactionType
from app.schemas.product import ProductResponse
from app.schemas.warehouse import WarehouseResponse

class StockInRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    reference_id: Optional[str] = None

class StockOutRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    reference_id: Optional[str] = None

class AdjustInventoryRequest(BaseModel):
    product_id: int
    warehouse_id: int
    available_quantity: Optional[int] = None
    damaged_quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
    reason: Optional[str] = "Manual Inventory Adjustment"

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    available_quantity: int
    reserved_quantity: int
    damaged_quantity: int
    last_updated: datetime
    product: Optional[ProductResponse] = None
    warehouse: Optional[WarehouseResponse] = None

    class Config:
        from_attributes = True

class InventoryHistoryResponse(BaseModel):
    id: int
    inventory_id: int
    product_id: int
    warehouse_id: int
    change_quantity: int
    transaction_type: TransactionType
    reference_id: Optional[str] = None
    created_by_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ForecastResponse(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    current_total_stock: int
    average_daily_demand: float
    predicted_demand_30_days: float
    recommended_reorder_quantity: int
    days_of_supply_remaining: float
