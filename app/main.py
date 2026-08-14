import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.database import async_engine, Base
from app.api.v1 import api_v1_router
from app.websockets.router import ws_router
from app.utils.redis_client import redis_client


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("app.main")


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Initializing Database tables & Redis connections..."
    )

    # Initialize database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize Redis
    await redis_client.init()

    logger.info(
        "Database and Redis initialized successfully."
    )

    yield

    # Application shutdown
    logger.info("Closing Redis connection...")

    await redis_client.close()

    logger.info("Redis connection closed.")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Scalable enterprise backend platform for managing "
        "warehouses, inventory, suppliers, purchase orders, "
        "stock transfers, and procurement workflows."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ============================================================
# CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL ERROR HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        f"Global exception caught on path "
        f"{request.url.path}: {exc}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "An internal server error occurred. "
                "Please contact administrator."
            )
        },
    )


# ============================================================
# REST API ROUTERS
# ============================================================

app.include_router(api_v1_router)


# ============================================================
# WEBSOCKET ROUTER
# ============================================================

app.include_router(ws_router)


# ============================================================
# CUSTOM OPENAPI / SWAGGER DOCUMENTATION
# ============================================================

def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description=(
            "Scalable enterprise backend platform for managing "
            "warehouses, inventory, suppliers, purchase orders, "
            "stock transfers, and procurement workflows."
        ),
        routes=app.routes,
    )

    # --------------------------------------------------------
    # WebSocket Swagger Tag
    # --------------------------------------------------------

    openapi_schema.setdefault("tags", [])

    if not any(
        tag.get("name") == "WebSockets"
        for tag in openapi_schema["tags"]
    ):
        openapi_schema["tags"].append(
            {
                "name": "WebSockets",
                "description": (
                    "Real-time WebSocket communication endpoints."
                ),
            }
        )

    # --------------------------------------------------------
    # WebSocket Documentation
    # --------------------------------------------------------

    websocket_endpoints = {
        "/ws/inventory": {
            "summary": "WebSocket - Inventory",
            "description": (
                "Real-time WebSocket connection for inventory updates.\n\n"
                "Connect using:\n"
                "ws://localhost:8000/ws/inventory"
            ),
        },
        "/ws/alerts": {
            "summary": "WebSocket - Alerts",
            "description": (
                "Real-time WebSocket connection for alerts.\n\n"
                "Connect using:\n"
                "ws://localhost:8000/ws/alerts"
            ),
        },
        "/ws/transfers": {
            "summary": "WebSocket - Stock Transfers",
            "description": (
                "Real-time WebSocket connection for stock transfer updates.\n\n"
                "Connect using:\n"
                "ws://localhost:8000/ws/transfers"
            ),
        },
    }

    # --------------------------------------------------------
    # Add WebSocket Routes to Swagger
    # --------------------------------------------------------

    for path, details in websocket_endpoints.items():

        openapi_schema["paths"][path] = {
            "get": {
                "tags": ["WebSockets"],
                "summary": details["summary"],
                "description": details["description"],
                "operationId": (
                    path.strip("/")
                    .replace("/", "_")
                    .replace("-", "_")
                    + "_websocket"
                ),
                "responses": {
                    "200": {
                        "description": (
                            "WebSocket endpoint documentation. "
                            "Use a WebSocket client to connect."
                        )
                    }
                },
                "x-websocket": True,
                "x-websocket-url": (
                    f"ws://localhost:8000{path}"
                ),
            }
        }

    # --------------------------------------------------------
    # Save OpenAPI Schema
    # --------------------------------------------------------

    app.openapi_schema = openapi_schema

    return app.openapi_schema


# Tell FastAPI to use the custom OpenAPI generator
app.openapi = custom_openapi


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


# ============================================================
# LOCAL DEVELOPMENT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )