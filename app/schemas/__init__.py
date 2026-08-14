from app.schemas.auth import (
    UserRegister, UserLogin, Token, TokenRefresh, PasswordResetRequest, PasswordResetConfirm, UserResponse
)
from app.schemas.warehouse import (
    WarehouseCreate, WarehouseUpdate, WarehouseAssignManager, WarehouseResponse
)
from app.schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierResponse
)
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse
)
from app.schemas.inventory import (
    StockInRequest, StockOutRequest, AdjustInventoryRequest, InventoryResponse, InventoryHistoryResponse, ForecastResponse
)
from app.schemas.purchase_order import (
    POCreate, POUpdate, POReceiveRequest, POResponse, POItemResponse
)
from app.schemas.stock_transfer import (
    TransferCreate, TransferUpdate, TransferResponse
)
from app.schemas.alert import AlertResponse
from app.schemas.analytics import AnalyticsDashboardResponse

__all__ = [
    "UserRegister", "UserLogin", "Token", "TokenRefresh", "PasswordResetRequest", "PasswordResetConfirm", "UserResponse",
    "WarehouseCreate", "WarehouseUpdate", "WarehouseAssignManager", "WarehouseResponse",
    "SupplierCreate", "SupplierUpdate", "SupplierResponse",
    "ProductCreate", "ProductUpdate", "ProductResponse",
    "StockInRequest", "StockOutRequest", "AdjustInventoryRequest", "InventoryResponse", "InventoryHistoryResponse", "ForecastResponse",
    "POCreate", "POUpdate", "POReceiveRequest", "POResponse", "POItemResponse",
    "TransferCreate", "TransferUpdate", "TransferResponse",
    "AlertResponse", "AnalyticsDashboardResponse"
]
