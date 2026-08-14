# 📦 Warehouse Inventory & Procurement Management Platform

A production-oriented backend platform for warehouse operations, inventory control, procurement workflows, stock transfers, real-time alerts, analytics, and automated background processing.**

Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **JWT authentication**, **Redis**, **Celery**, **WebSockets**, **Docker**, and **Pytest**.

---

## 🚀 Overview

The **Warehouse Inventory & Procurement Management Platform** is a backend system designed to centralize warehouse and inventory operations while supporting the complete procurement lifecycle.

The platform provides APIs for:

* 🔐 User registration and authentication
* 👥 Role-based access control
* 🏭 Warehouse management
* 📦 Product management
* 🚚 Supplier management
* 📊 Inventory management
* 📥 Stock-in operations
* 📤 Stock-out operations
* 🔄 Inventory adjustments
* 📈 Inventory history and forecasting
* 🧾 Purchase order management
* 📦 Purchase order receiving
* 🔁 Inter-warehouse stock transfers
* 🚨 Inventory alerts
* 📊 Warehouse and supplier analytics
* ⚡ Redis-based caching
* 🔌 Real-time WebSocket communication
* ⏱️ Celery background tasks
* 📅 Celery Beat scheduled jobs
* 🏷️ SKU barcode generation
* 📄 CSV import support
* 🗄️ PostgreSQL persistence
* 🔄 Alembic database migrations
* 🧪 Automated testing
* 🐳 Dockerized development environment

---

# ✨ Key Features

## 🔐 Authentication & Authorization

The API uses **JWT-based authentication** with access and refresh tokens.

### Authentication capabilities

* User registration
* User login
* Access token generation
* Refresh token generation
* Password reset endpoint
* Current authentication context
* Password hashing
* Protected API endpoints
* Role-based authorization

### Supported roles

```text
SUPER_ADMIN
WAREHOUSE_MANAGER
INVENTORY_STAFF
PROCUREMENT_OFFICER
```

Protected operations can be restricted according to the authenticated user's role.

---

# 🏭 Warehouse Management

The warehouse module provides APIs for managing warehouse locations and their operational status.

### Supported operations

* Create warehouse
* List warehouses
* Retrieve warehouse
* Update warehouse
* Disable warehouse
* Warehouse-based inventory tracking

Inventory is maintained at the **product + warehouse** level.

---

# 📦 Product Management

Products are the core inventory entities within the platform.

### Supported operations

* Create product
* List products
* Retrieve product
* Update product
* Archive product
* Generate SKU barcode
* Import products through CSV

Products contain inventory-related information such as:

* SKU
* Product name
* Category
* Brand
* Cost price
* Selling price
* Reorder level

---

# 🚚 Supplier Management

Supplier APIs support supplier lifecycle management and procurement relationships.

### Supported operations

* Create supplier
* List suppliers
* Retrieve supplier
* Update supplier
* Suspend supplier
* View supplier purchase history

Supplier information is linked to purchase order workflows.

---

# 📊 Inventory Management

Inventory is tracked independently for every **product and warehouse combination**.

The system maintains:

```text
Available Quantity
Reserved Quantity
Damaged Quantity
```

### Inventory operations

| Operation     | Description                                |
| ------------- | ------------------------------------------ |
| 📥 Stock In   | Adds inventory to a warehouse              |
| 📤 Stock Out  | Removes available inventory                |
| 🔧 Adjust     | Updates inventory quantities               |
| 📜 History    | Tracks inventory transactions              |
| 📈 Forecast   | Estimates future demand and stock coverage |
| 📄 CSV Import | Imports inventory data                     |

### Inventory flow

```text
                API Request
                     │
                     ▼
              Authentication
                     │
                     ▼
              Request Validation
                     │
                     ▼
             Inventory Service
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Validate Product       Validate Warehouse
          │                     │
          └──────────┬──────────┘
                     ▼
              Update Inventory
                     │
                     ▼
           Record Transaction
                     │
                     ▼
             Cache Invalidation
                     │
                     ▼
               Alert Check
                     │
                     ▼
                  Response
```

---

# 📈 Inventory Forecasting

The platform includes a lightweight inventory forecasting service.

The forecast is calculated using recent inventory movement history.

It considers:

* Current total stock
* Stock-out activity
* Transfer-out activity
* Average daily demand
* Estimated 30-day demand
* Recommended reorder quantity
* Estimated days of supply remaining

Example forecast response concepts:

```text
Current Stock
     │
     ▼
30-Day Historical Demand
     │
     ▼
Average Daily Demand
     │
     ├──► Predicted 30-Day Demand
     │
     ├──► Recommended Reorder Quantity
     │
     └──► Days of Supply Remaining
```

---

# 🧾 Procurement & Purchase Orders

The purchase order module manages the procurement lifecycle between warehouses and suppliers.

### Purchase order capabilities

* Create purchase orders
* List purchase orders
* Retrieve purchase orders
* Update purchase orders
* Approve purchase orders
* Cancel purchase orders
* Receive purchased goods
* Track received quantities
* Support partial receiving
* Update inventory after receiving

### Purchase order lifecycle

```text
DRAFT
  │
  ▼
APPROVED
  │
  ▼
RECEIVING
  │
  ├──────────────► PARTIAL RECEIPT
  │                      │
  │                      ▼
  └──────────────────► COMPLETED
```

Receiving validates ordered quantities before updating warehouse inventory.

---

# 📥 Goods Receiving

Purchase order receiving automatically connects procurement with inventory.

The receiving flow is:

```text
Purchase Order
      │
      ▼
Receive Goods
      │
      ▼
Validate Product
      │
      ▼
Validate Ordered Quantity
      │
      ▼
Update Received Quantity
      │
      ▼
Increase Warehouse Inventory
      │
      ▼
Update Purchase Order Status
```

This allows procurement operations to directly affect warehouse stock.

---

# 🔄 Inter-Warehouse Stock Transfers

Stock can be transferred between warehouses.

### Transfer lifecycle

```text
REQUESTED
    │
    ▼
APPROVED
    │
    ▼
IN_TRANSIT
    │
    ▼
RECEIVED
```

The transfer service validates:

* Source warehouse
* Destination warehouse
* Source and destination are different
* Product availability
* Transfer quantities
* Source inventory

### Transfer flow

```text
Source Warehouse
      │
      │  Stock Out
      ▼
  IN_TRANSIT
      │
      │  Stock In
      ▼
Destination Warehouse
```

---

# 🚨 Inventory Alerts

The platform includes automated inventory alert processing.

Alerts can be generated when inventory reaches configured reorder thresholds.

Supported alert concepts include:

* Low-stock alerts
* Out-of-stock alerts
* Alert acknowledgement
* Automated background scanning

The alert task periodically checks inventory and creates alerts when required.

---

# ⚡ Redis Caching

Redis is used for asynchronous caching and messaging support.

Inventory reads can follow this flow:

```text
Client Request
      │
      ▼
   Redis Cache
      │
 ┌────┴────┐
 │         │
Hit       Miss
 │         │
 ▼         ▼
Return   PostgreSQL
            │
            ▼
        Store in Redis
            │
            ▼
          Return
```

Inventory-changing operations invalidate relevant cached data to reduce stale reads.

---

# 🔌 WebSocket Real-Time Communication

The project provides WebSocket endpoints for real-time communication.

### Available WebSocket channels

```text
/ws/inventory
/ws/alerts
/ws/transfers
```

WebSockets can be used for:

* Inventory events
* Alert notifications
* Transfer events
* Real-time client communication

Example architecture:

```text
                    FastAPI
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Inventory      Alerts      Transfers
          │            │            │
          └────────────┼────────────┘
                       ▼
                WebSocket Manager
                       │
                       ▼
                Connected Clients
```

---

# ⏱️ Background Processing

Background processing is implemented using **Celery** with Redis as the broker/backend.

The project contains separate task modules for:

```text
app/tasks/
├── celery_app.py
├── inventory_tasks.py
├── alert_tasks.py
└── report_tasks.py
```

### Scheduled operations

Celery Beat is configured for tasks including:

* Inventory reconciliation
* Low-stock and expired-product checks
* Supplier performance calculation
* Daily inventory reporting

### Background architecture

```text
              Celery Beat
                   │
                   ▼
             Scheduled Tasks
                   │
                   ▼
              Redis Broker
                   │
                   ▼
             Celery Worker
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
      Inventory  Alerts   Reports
```

---

# 🏷️ Barcode Generation

The platform includes SKU barcode generation using **python-barcode**.

Products can expose a barcode representation through the product API.

The barcode service supports **Code 128** SVG generation.

---

# 📄 CSV Import

CSV-based import functionality is available for:

* Products
* Inventory

This provides a convenient way to load bulk operational data into the platform.

---

# 📊 Analytics

The analytics module provides authenticated endpoints for:

* Dashboard analytics
* Inventory analytics
* Supplier analytics
* Warehouse analytics

These endpoints provide a foundation for operational reporting and future dashboard integrations.

---

# 🏗️ Architecture

The application follows a layered backend architecture.

```text
                         Client
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │  API Layer  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Services  │
                    │ Business    │
                    │   Logic     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ SQLAlchemy  │
                    │    ORM      │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ PostgreSQL  │
                    └─────────────┘


        ┌──────────────────────────────────┐
        │          Supporting Services      │
        ├──────────────────────────────────┤
        │ Redis                             │
        │ Celery Worker                     │
        │ Celery Beat                       │
        │ WebSocket Manager                 │
        └──────────────────────────────────┘
```

---

# 🛠️ Technology Stack

| Area                   | Technology        |
| ---------------------- | ----------------- |
| Language               | Python 3.11       |
| API Framework          | FastAPI           |
| ASGI Server            | Uvicorn           |
| ORM                    | SQLAlchemy 2.x    |
| Database               | PostgreSQL 15     |
| Async Database Driver  | asyncpg           |
| Sync PostgreSQL Driver | psycopg2          |
| Validation             | Pydantic 2        |
| Configuration          | Pydantic Settings |
| Authentication         | JWT / python-jose |
| Password Hashing       | Passlib / bcrypt  |
| Cache & Broker         | Redis 7           |
| Background Tasks       | Celery            |
| Scheduling             | Celery Beat       |
| Migrations             | Alembic           |
| Barcode                | python-barcode    |
| Data Processing        | Pandas            |
| Testing                | Pytest            |
| Async Testing          | pytest-asyncio    |
| HTTP Testing           | HTTPX             |
| Containerization       | Docker            |
| Orchestration          | Docker Compose    |

---

# 📁 Project Structure

```text
warehouse-inventory/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── alerts.py
│   │       ├── analytics.py
│   │       ├── auth.py
│   │       ├── inventory.py
│   │       ├── products.py
│   │       ├── purchase_orders.py
│   │       ├── suppliers.py
│   │       ├── transfers.py
│   │       └── warehouses.py
│   │
│   ├── models/
│   │   ├── alert.py
│   │   ├── inventory.py
│   │   ├── product.py
│   │   ├── purchase_order.py
│   │   ├── stock_transfer.py
│   │   ├── supplier.py
│   │   ├── user.py
│   │   └── warehouse.py
│   │
│   ├── schemas/
│   │   ├── alert.py
│   │   ├── analytics.py
│   │   ├── auth.py
│   │   ├── inventory.py
│   │   ├── product.py
│   │   ├── purchase_order.py
│   │   ├── stock_transfer.py
│   │   ├── supplier.py
│   │   └── warehouse.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── barcode_service.py
│   │   ├── csv_service.py
│   │   ├── forecasting_service.py
│   │   ├── inventory_service.py
│   │   ├── po_service.py
│   │   └── transfer_service.py
│   │
│   ├── tasks/
│   │   ├── celery_app.py
│   │   ├── inventory_tasks.py
│   │   ├── alert_tasks.py
│   │   └── report_tasks.py
│   │
│   ├── utils/
│   │   ├── email_notifier.py
│   │   └── redis_client.py
│   │
│   ├── websockets/
│   │   ├── connection_manager.py
│   │   └── router.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── main.py
│
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
│
├── docs/
│   ├── celery_workflow.md
│   ├── schema_diagram.md
│   ├── system_architecture.md
│   └── websocket_flow.md
│
├── tests/
│   ├── conftest.py
│   ├── test_alerts.py
│   ├── test_auth.py
│   ├── test_inventory.py
│   ├── test_purchase_orders.py
│   └── test_transfers.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── openapi.json
├── postman_collection.json
├── requirements.txt
└── README.md
```

---

# 🐳 Docker Setup

The included Docker Compose configuration provides the main infrastructure required by the application.

### Services

```text
┌───────────────────────┐
│       Backend         │
│       FastAPI         │
│       :8000           │
└───────────┬───────────┘
            │
      ┌─────┴─────┐
      ▼           ▼
 PostgreSQL     Redis
   :5432         :6379
      │           │
      │     ┌─────┴──────┐
      │     ▼            ▼
      │  Celery       Celery
      │  Worker        Beat
      │
      └──────────────────┘
```

### Start the complete stack

```bash
docker-compose up --build
```

### Start in detached mode

```bash
docker-compose up -d
```

### Stop the stack

```bash
docker-compose down
```

### Rebuild after code/dependency changes

```bash
docker-compose up --build
```

---

# 🐍 Local Development Setup

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd warehouse-inventory
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a local `.env` file based on `.env.example`.

```text
.env.example
     │
     ▼
   copy
     │
     ▼
   .env
```

Configure your local:

* PostgreSQL connection
* Redis connection
* JWT secret
* SMTP settings

**Never commit your real `.env` file or production credentials.**

## 5. Run database migrations

```bash
alembic upgrade head
```

## 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### OpenAPI schema

```text
http://127.0.0.1:8000/openapi.json
```

The repository also includes:

```text
openapi.json
postman_collection.json
```

for API exploration and testing.

---

# 🔄 Database Migrations

Create a migration after model changes:

```bash
alembic revision --autogenerate -m "describe migration"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```

---

# 🧪 Testing

The project uses:

* **Pytest**
* **pytest-asyncio**
* **HTTPX**
* FastAPI async test clients

Run the complete test suite:

```bash
pytest -v
```

Run inventory tests:

```bash
pytest -v tests/test_inventory.py
```

Run authentication tests:

```bash
pytest -v tests/test_auth.py
```

Run purchase order tests:

```bash
pytest -v tests/test_purchase_orders.py
```

Run transfer tests:

```bash
pytest -v tests/test_transfers.py
```

The test suite covers important workflows including authentication, inventory operations, purchase orders, transfers, alerts, and API behavior.

---

# 🔐 Security

The application includes several security mechanisms:

* JWT access tokens
* Refresh tokens
* Password hashing
* Protected API endpoints
* Role-based authorization
* Pydantic request validation
* Environment-based configuration
* Centralized exception handling

## Production recommendations

Before deploying to production:

* Replace development secrets
* Use strong randomly generated JWT secrets
* Use secure PostgreSQL credentials
* Restrict CORS origins
* Enable HTTPS
* Secure Redis
* Configure proper SMTP credentials
* Add structured logging
* Add monitoring and alerting
* Keep `.env` and other secrets outside source control

---

# 🧠 Design Principles

The project is structured around several backend engineering principles.

### Separation of Concerns

API routes focus on HTTP-level responsibilities while business logic is handled by dedicated services.

### Service-Oriented Business Logic

Core workflows such as inventory operations, purchase orders, transfers, forecasting, and authentication are implemented in service modules.

### ORM-Based Persistence

SQLAlchemy provides the database abstraction layer over PostgreSQL.

### Schema Validation

Pydantic models provide structured request and response validation.

### Transaction Safety

Critical inventory and procurement operations use database operations designed to maintain consistent state.

### Cache Consistency

Inventory-changing operations trigger cache invalidation to reduce stale inventory data.

### Asynchronous Architecture

FastAPI and SQLAlchemy support asynchronous request/database processing while Celery handles background workloads.

---

# 🔗 API Modules

The REST API is organized under:

```text
/api/v1
```

### Authentication

```text
/api/v1/register
/api/v1/login
/api/v1/refresh
/api/v1/reset-password
```

### Warehouses

```text
/api/v1/warehouses
```

### Suppliers

```text
/api/v1/suppliers
```

### Products

```text
/api/v1/products
```

### Inventory

```text
/api/v1/inventory
```

Includes:

```text
GET  /api/v1/inventory
POST /api/v1/inventory/stock-in
POST /api/v1/inventory/stock-out
POST /api/v1/inventory/adjust
GET  /api/v1/inventory/history
GET  /api/v1/inventory/forecast/{product_id}
POST /api/v1/inventory/import-csv
```

### Purchase Orders

```text
/api/v1/purchase-orders
```

### Stock Transfers

```text
/api/v1/transfers
```

### Alerts

```text
/api/v1/alerts
```

### Analytics

```text
/api/v1/analytics
```

---

# 📡 WebSocket Endpoints

Real-time communication is available through:

```text
ws://127.0.0.1:8000/ws/inventory
ws://127.0.0.1:8000/ws/alerts
ws://127.0.0.1:8000/ws/transfers
```

---

# 📌 Current Scope

This repository currently focuses on the **backend platform and supporting infrastructure**.

It includes:

```text
REST API
Authentication
Authorization
Inventory
Procurement
Warehouses
Products
Suppliers
Transfers
Alerts
Analytics
Caching
WebSockets
Background Processing
Scheduled Tasks
Database Migrations
Testing
Docker Infrastructure
API Documentation
```

---

# 🔮 Future Enhancements

Potential future improvements include:

* 📊 Advanced analytics dashboards
* 📑 Automated PDF/Excel reporting
* 📦 Advanced demand forecasting
* 🔍 Barcode/QR workflow expansion
* 🧾 Audit log dashboard
* 🔔 Production email notification integration
* 🔐 More granular permissions
* 📈 Observability and monitoring
* 🚀 CI/CD automation
* ☁️ Cloud deployment
* 🖥️ Dedicated frontend dashboard
* 📱 Mobile warehouse operations interface

---

# 🤝 Contributing

Contributions are welcome.

A typical development workflow is:

```bash
git checkout -b feature/your-feature
```

Make your changes, run the tests:

```bash
pytest -v
```

Then commit:

```bash
git add .
git commit -m "Describe your changes"
```

Push your branch:

```bash
git push origin feature/your-feature
```

Then open a pull request.

---

# 📄 License

No license file is currently included in the project repository.

If this project is intended to be open source, add an appropriate `LICENSE` file before publishing it for external contributions.

---

# 👨‍💻 AUTHOR

# **RAHUL RAJ**

### **PYTHON BACKEND DEVELOPER**

> Building scalable backend systems with **Python • FastAPI • PostgreSQL • Redis • Celery • Docker**

