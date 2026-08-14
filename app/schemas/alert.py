from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.alert import AlertType
from app.schemas.product import ProductResponse
from app.schemas.warehouse import WarehouseResponse

class AlertResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    alert_type: AlertType
    current_quantity: int
    threshold_quantity: Optional[int] = None
    message: str
    is_acknowledged: bool
    timestamp: datetime
    product: Optional[ProductResponse] = None
    warehouse: Optional[WarehouseResponse] = None

    class Config:
        from_attributes = True
