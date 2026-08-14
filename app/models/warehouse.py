import enum
from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class WarehouseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=False)
    capacity = Column(Float, nullable=False, default=1000.0)
    current_utilization = Column(Float, nullable=False, default=0.0)
    status = Column(SQLEnum(WarehouseStatus), default=WarehouseStatus.ACTIVE, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manager = relationship("User", foreign_keys=[manager_id])
    staff_members = relationship("User", back_populates="assigned_warehouse", foreign_keys="User.warehouse_id")
    inventories = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")
