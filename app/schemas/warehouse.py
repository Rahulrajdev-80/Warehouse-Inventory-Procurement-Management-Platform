from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.warehouse import WarehouseStatus

class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: str
    capacity: float = 1000.0
    manager_id: Optional[int] = None

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[float] = None
    status: Optional[WarehouseStatus] = None
    manager_id: Optional[int] = None

class WarehouseAssignManager(BaseModel):
    manager_id: int

class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    address: str
    capacity: float
    current_utilization: float
    status: WarehouseStatus
    manager_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
