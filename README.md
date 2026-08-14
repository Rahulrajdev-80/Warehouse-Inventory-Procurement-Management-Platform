# Warehouse Inventory & Procurement Management Platform

A production-grade, highly scalable backend platform built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, **Celery**, **Redis**, **WebSockets**, and **Docker**.

---

## 🌟 Key Features & Capabilities

- 🔐 **Authentication & Role-Based Authorization (RBAC)**
  - JWT Access Tokens, Refresh Tokens, and Password Reset.
  - 4 Role Tiers: `SUPER_ADMIN`, `WAREHOUSE_MANAGER`, `INVENTORY_STAFF`, `PROCUREMENT_OFFICER`.

- 🏢 **Warehouse Management**
  - CRUD operations, manager assignment, capacity monitoring, and occupancy utilization metrics.

- 🏭 **Supplier Management**
  - Vendor lifecycle, rating algorithm, suspension, and complete purchase history.

- 📦 **Product & Barcode Management**
  - Product catalog, archival, SVG/PNG barcode generation for SKUs, and bulk CSV import.

- 📊 **Inventory & Forecasting**
  - Atomic Stock-In, Stock-Out, and Adjustments.
  - Audit logging of all transactions.
  - **Inventory Forecasting**: Moving-average statistical demand prediction & replenishment advisor.
  - Bulk CSV import for inventory stock.

- 🛒 **Purchase Orders & Goods Receipt**
  - PO workflow: `DRAFT` → `PENDING_APPROVAL` → `APPROVED` → `ORDERED` → `PARTIALLY_RECEIVED` / `COMPLETED` / `CANCELLED`.
  - Quality check & automatic inventory increments on receipt.

- 🚚 **Stock Transfers**
  - 2-Phase Transfer: Reserve/deduct from source on approval, increment destination on receipt.

- 🚨 **Low Stock Alerts & Notifications**
  - Automatic triggers for `LOW_STOCK`, `OUT_OF_STOCK`, `OVERSTOCK`, and `EXPIRED_PRODUCT`.
  - Real-time WebSocket broadcasting and email notifications.

- ⚡ **Real-Time WebSockets**
  - Live pub/sub channels: `/ws/inventory`, `/ws/alerts`, `/ws/transfers`.

- ⏰ **Background Processing (Celery & Redis)**
  - Automated inventory reconciliation.
  - Daily low-stock and expiry background scanner.
  - Supplier performance score calculator.
  - Daily inventory summary report generator.

- 📈 **Analytics Dashboard**
  - Financial inventory valuation, turnover rate, supplier performance, top moved products, and warehouse utilization cached in Redis.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.11+ |
| **Framework** | FastAPI |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0 (Async `asyncpg` + Sync `psycopg2`) |
| **Migrations** | Alembic |
| **Caching & PubSub** | Redis 7 |
| **Task Queue** | Celery + Celery Beat |
| **Real-Time** | WebSockets |
| **Barcode Engine** | `python-barcode` |
| **Data Parsing** | Pandas & CSV |
| **Testing** | Pytest + pytest-asyncio + HTTPX |
| **Containerization**| Docker & Docker Compose |

---

## 📁 Directory Structure

```text
c:\Users\rahul\Downloads\warehouse inventory\
├── app/
│   ├── api/                     # REST Router Endpoints (v1)
│   ├── models/                  # SQLAlchemy ORM Models
│   ├── schemas/                 # Pydantic Request/Response DTOs
│   ├── services/                # Domain Business Logic
│   ├── tasks/                   # Celery Worker Tasks & Beat Schedule
│   ├── utils/                   # Redis Client & Email Notifier
│   ├── websockets/              # WebSocket Router & Manager
│   ├── config.py                # Pydantic Settings
│   ├── database.py              # Async/Sync DB Session Factory
│   ├── main.py                  # FastAPI Application Entrypoint
│   └── security.py              # JWT Authentication & RBAC Guards
├── alembic/                     # Database Migrations
├── docs/                        # Architectural Diagrams & Flowcharts
├── tests/                       # Automated Pytest Test Suite
├── postman_collection.json      # Postman API Collection
├── Dockerfile                   # Production Multi-Stage Dockerfile
├── docker-compose.yml           # Compose Config (App, Postgres, Redis, Celery)
├── requirements.txt             # Python Dependencies
└── README.md                    # System Documentation
```

---

## 🚀 Quick Start Guide (VS Code Terminal / Local)

### Option 1: Run with Docker Compose (Recommended)

1. Clone or extract project directory into VS Code.
2. Build and start all 5 containers (Backend, Postgres, Redis, Celery Worker, Celery Beat):
   ```bash
   docker-compose up --build -d
   ```
3. Check container logs:
   ```bash
   docker-compose logs -f backend
   ```
4. Access interactive API Documentation at:
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option 2: Run Locally in Terminal

1. **Create and Activate Python Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell / Command Prompt):
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and verify database credentials:
   ```bash
   cp .env.example .env
   ```

4. **Start PostgreSQL & Redis** (or start local instances):
   ```bash
   docker-compose up postgres redis -d
   ```

5. **Run Alembic Migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start FastAPI Application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Celery Worker (In a separate terminal)**:
   ```bash
   celery -A app.tasks.celery_app.celery worker --loglevel=info
   ```

8. **Start Celery Beat Scheduler (In a separate terminal)**:
   ```bash
   celery -A app.tasks.celery_app.celery beat --loglevel=info
   ```

---

## 🧪 Running Automated Unit & Integration Tests

Run the full pytest suite (uses SQLite in-memory engine, no running Postgres required):

```bash
pytest tests/ -v
```

### Test Coverage Summary:
- `tests/test_auth.py`: User registration, login, token verification.
- `tests/test_inventory.py`: Stock in, stock out, inventory adjustment, history logging.
- `tests/test_purchase_orders.py`: PO creation, approval, goods receipt, auto stock increment.
- `tests/test_transfers.py`: Two-phase transfer creation, approval, and destination receipt.
- `tests/test_alerts.py`: Automatic low stock trigger & alert acknowledgment.

---

## 📡 API Endpoints Reference

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` - User Registration
- `POST /api/v1/auth/login` - User Login (returns JWT access & refresh tokens)
- `POST /api/v1/auth/refresh` - Refresh Access Token
- `POST /api/v1/auth/reset-password` - Password Reset Request

### Warehouses (`/api/v1/warehouses`)
- `POST /api/v1/warehouses` - Create Warehouse (`SUPER_ADMIN`)
- `GET /api/v1/warehouses` - List Warehouses
- `GET /api/v1/warehouses/{id}` - Get Warehouse Details
- `PUT /api/v1/warehouses/{id}` - Update Warehouse
- `DELETE /api/v1/warehouses/{id}` - Disable Warehouse

### Suppliers (`/api/v1/suppliers`)
- `POST /api/v1/suppliers` - Add Supplier
- `GET /api/v1/suppliers` - List Suppliers
- `GET /api/v1/suppliers/{id}` - Get Supplier
- `PUT /api/v1/suppliers/{id}` - Update Supplier
- `DELETE /api/v1/suppliers/{id}` - Suspend Supplier
- `GET /api/v1/suppliers/{id}/history` - Supplier Purchase History

### Products (`/api/v1/products`)
- `POST /api/v1/products` - Add Product
- `GET /api/v1/products` - List Products
- `GET /api/v1/products/{id}` - Get Product
- `PUT /api/v1/products/{id}` - Update Product
- `DELETE /api/v1/products/{id}` - Archive Product
- `GET /api/v1/products/{id}/barcode` - Generate SVG Barcode
- `POST /api/v1/products/import-csv` - CSV Bulk Upload

### Inventory (`/api/v1/inventory`)
- `GET /api/v1/inventory` - View Inventory Levels
- `POST /api/v1/inventory/stock-in` - Stock In
- `POST /api/v1/inventory/stock-out` - Stock Out
- `POST /api/v1/inventory/adjust` - Adjust Stock
- `GET /api/v1/inventory/history` - Audit Transaction Log
- `GET /api/v1/inventory/forecast/{product_id}` - Inventory Forecasting
- `POST /api/v1/inventory/import-csv` - CSV Bulk Import

### Purchase Orders (`/api/v1/purchase-orders`)
- `POST /api/v1/purchase-orders` - Create PO
- `GET /api/v1/purchase-orders` - List POs
- `GET /api/v1/purchase-orders/{id}` - Get PO
- `PUT /api/v1/purchase-orders/{id}` - Update PO
- `DELETE /api/v1/purchase-orders/{id}` - Cancel PO
- `POST /api/v1/purchase-orders/{id}/approve` - Approve PO
- `POST /api/v1/purchase-orders/{id}/receive` - Receive Goods (Auto Stock Increase)

### Stock Transfers (`/api/v1/transfers`)
- `POST /api/v1/transfers` - Create Transfer
- `GET /api/v1/transfers` - List Transfers
- `PUT /api/v1/transfers/{id}` - Update Transfer
- `POST /api/v1/transfers/{id}/approve` - Approve Transfer (Deduct Source Stock)
- `POST /api/v1/transfers/{id}/receive` - Receive Transfer (Add Destination Stock)

### Alerts (`/api/v1/alerts`)
- `GET /api/v1/alerts` - List Alerts
- `PUT /api/v1/alerts/{id}/acknowledge` - Acknowledge Alert

### Analytics (`/api/v1/analytics`)
- `GET /api/v1/analytics/dashboard` - Complete KPI Dashboard (Cached in Redis)

### WebSockets (`/ws/...`)
- `/ws/inventory` - Real-time inventory update notifications
- `/ws/alerts` - Real-time alert notifications
- `/ws/transfers` - Real-time stock transfer status updates
