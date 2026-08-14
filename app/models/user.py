import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER"
    INVENTORY_STAFF = "INVENTORY_STAFF"
    PROCUREMENT_OFFICER = "PROCUREMENT_OFFICER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.INVENTORY_STAFF, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_warehouse = relationship("Warehouse", back_populates="staff_members", foreign_keys=[warehouse_id])
