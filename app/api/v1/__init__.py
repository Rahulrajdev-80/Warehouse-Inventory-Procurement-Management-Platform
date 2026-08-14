from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.warehouses import router as warehouses_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.products import router as products_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.purchase_orders import router as po_router
from app.api.v1.transfers import router as transfers_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.analytics import router as analytics_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(warehouses_router)
api_v1_router.include_router(suppliers_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(po_router)
api_v1_router.include_router(transfers_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(analytics_router)
