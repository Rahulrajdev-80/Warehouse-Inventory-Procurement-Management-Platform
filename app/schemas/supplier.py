from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.supplier import SupplierStatus

class SupplierCreate(BaseModel):
    name: str
    contact_person: str
    email: EmailStr
    phone: str
    gst_number: str
    address: str
    rating: Optional[float] = 5.0

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    status: Optional[SupplierStatus] = None

class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: str
    email: str
    phone: str
    gst_number: str
    address: str
    rating: float
    status: SupplierStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
