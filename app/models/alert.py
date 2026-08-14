import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AlertType(str, enum.Enum):
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    OVERSTOCK = "OVERSTOCK"
    EXPIRED_PRODUCT = "EXPIRED_PRODUCT"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    current_quantity = Column(Integer, nullable=False)
    threshold_quantity = Column(Integer, nullable=True)
    message = Column(String, nullable=False)
    is_acknowledged = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
    warehouse = relationship("Warehouse")
