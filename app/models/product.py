from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False)
    unit = Column(String, nullable=False, default="pcs")
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    reorder_level = Column(Integer, nullable=False, default=10)
    barcode = Column(String, unique=True, index=True, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventories = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
