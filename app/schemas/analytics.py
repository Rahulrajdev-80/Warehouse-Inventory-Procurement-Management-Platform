from pydantic import BaseModel
from typing import List, Dict, Any

class TopMovedProduct(BaseModel):
    product_id: int
    sku: str
    product_name: str
    total_quantity_moved: int

class WarehouseUtilizationItem(BaseModel):
    warehouse_id: int
    name: str
    code: str
    capacity: float
    current_utilization: float
    occupancy_percentage: float

class SupplierPerformanceItem(BaseModel):
    supplier_id: int
    name: str
    rating: float
    total_pos: int
    completed_pos: int
    on_time_delivery_rate: float

class AnalyticsDashboardResponse(BaseModel):
    total_products: int
    total_warehouses: int
    total_inventory_value: float
    low_stock_items_count: int
    out_of_stock_items_count: int
    purchase_orders_this_month: int
    inventory_turnover_rate: float
    most_moved_products: List[TopMovedProduct]
    warehouse_utilization: List[WarehouseUtilizationItem]
    supplier_performance: List[SupplierPerformanceItem]
