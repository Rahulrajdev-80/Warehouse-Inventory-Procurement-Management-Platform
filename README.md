Warehouse Inventory & Procurement Management Platform
A production-oriented backend system for managing warehouse operations, inventory, procurement, stock transfers, goods receipts, suppliers, products, users, authentication, alerts, and analytics.

The application is built using FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT Authentication, Redis caching, and a layered architecture separating APIs, services, repositories, models, and schemas.

🚀 Project Overview
The Warehouse Inventory & Procurement Management Platform provides a centralized backend for managing inventory across warehouses and handling the complete procurement lifecycle.

The platform supports:

User authentication and authorization
Role-based access control
Warehouse management
Product and category management
Supplier management
Inventory management
Stock-in and stock-out operations
Inventory reservations and releases
Damaged stock management
Inventory reconciliation
Purchase order lifecycle
Goods receipt processing
Inter-warehouse stock transfers
Inventory alerts
Analytics and dashboards
Redis-based inventory caching
WebSocket-based alerts
Background task support
Database migrations using Alembic
Automated testing with Pytest
🏗️ Architecture
The project follows a layered architecture:

Client
   │
   ▼
FastAPI API Layer
   │
   ▼
Service Layer
   │
   ▼
Repository Layer
   │
   ▼
SQLAlchemy Models
   │
   ▼
PostgreSQL Database

                 ┌───────────────┐
                 │    FastAPI    │
                 └───────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     PostgreSQL        Redis        WebSocket
          │              │              │
          ▼              ▼              ▼
      Database        Caching        Real-time
                                    Notifications

🛠️ Technology Stack Backend Python FastAPI SQLAlchemy Pydantic PostgreSQL Alembic Authentication & Security JWT Authentication Access Tokens Refresh Tokens Password hashing Role-Based Access Control (RBAC) Protected API endpoints Caching Redis Inventory cache Cache invalidation after inventory changes Real-Time Communication WebSockets Inventory alert notifications Background Processing Celery Background scheduler/tasks Testing Pytest FastAPI TestClient unittest.mock MagicMock Service-layer unit testing Development Git Docker Docker Compose Uvicorn ``

📁 Project Structure
warehouse-management/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── alerts.py
│   │   ├── analytics.py
│   │   ├── auth.py
│   │   ├── categories.py
│   │   ├── goods_receipts.py
│   │   ├── inventory.py
│   │   ├── products.py
│   │   ├── purchase_orders.py
│   │   ├── stock_transfers.py
│   │   ├── suppliers.py
│   │   ├── users.py
│   │   ├── warehouses.py
│   │   └── websocket.py
│   │
│   ├── background/
│   │   ├── scheduler.py
│   │   └── tasks.py
│   │
│   ├── core/
│   │   ├── celery_app.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logger.py
│   │   ├── redis.py
│   │   ├── security.py
│   │   ├── websocket.py
│   │   └── websocket_manager.py
│   │
│   ├── dependencies/
│   │   └── auth.py
│   │
│   ├── exceptions/
│   │   ├── custom_exceptions.py
│   │   └── handlers.py
│   │
│   ├── models/
│   │   ├── alert.py
│   │   ├── category.py
│   │   ├── goods_receipt.py
│   │   ├── inventory.py
│   │   ├── inventory_transaction.py
│   │   ├── password_reset.py
│   │   ├── product.py
│   │   ├── purchase_order.py
│   │   ├── refresh_token.py
│   │   ├── role.py
│   │   ├── stock_transfer.py
│   │   ├── supplier.py
│   │   ├── user.py
│   │   └── warehouse.py
│   │
│   ├── repositories/
│   │   ├── alert_repository.py
│   │   ├── analytics_repository.py
│   │   ├── auth_repository.py
│   │   ├── category_repository.py
│   │   ├── goods_receipt_repository.py
│   │   ├── inventory_repository.py
│   │   ├── password_reset_repository.py
│   │   ├── product_repository.py
│   │   ├── purchase_order_repository.py
│   │   ├── role_repository.py
│   │   ├── stock_transfer_repository.py
│   │   ├── supplier_repository.py
│   │   ├── user_repository.py
│   │   └── warehouse_repository.py
│   │
│   ├── schemas/
│   │   ├── alert.py
│   │   ├── analytics.py
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── goods_receipt.py
│   │   ├── inventory.py
│   │   ├── product.py
│   │   ├── purchase_order.py
│   │   ├── stock_transfer.py
│   │   ├── supplier.py
│   │   ├── user.py
│   │   └── warehouse.py
│   │
│   └── services/
│       ├── alert_service.py
│       ├── analytics_service.py
│       ├── auth_service.py
│       ├── category_service.py
│       ├── goods_receipt_service.py
│       ├── inventory_cache_service.py
│       ├── inventory_service.py
│       ├── product_service.py
│       ├── purchase_order_service.py
│       ├── stock_transfer_service.py
│       ├── supplier_service.py
│       ├── user_service.py
│       └── warehouse_service.py
│
├── migrations/
├── tests/
│   ├── conftest.py
│   ├── test_analytics.py
│   ├── test_auth.py
│   ├── test_goods_receipt_service.py
│   ├── test_health.py
│   ├── test_inventory.py
│   ├── test_inventory_service.py
│   ├── test_purchase_order_service.py
│   ├── test_stock_transfer_service.py
│   └── test_websocket.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── test_db.py
└── README.md

🔐 Authentication
The platform uses JWT-based authentication.

Authentication functionality includes:

User registration User login Access token generation Refresh token generation Token refresh Logout Current-user endpoint Invalid token handling Password validation Role-based authorization

Protected endpoints require a valid JWT access token.

Example:

Authorization: Bearer <access_token>

👥 Role-Based Access Control
The application supports role-based access control to restrict operations based on user permissions.

Roles can be used to control access to:

Users Warehouses Products Suppliers Inventory Procurement Stock transfers Analytics Administrative operations

📦 Inventory Management
The inventory module manages stock at warehouse level.

Supported operations:

Stock In

Adds inventory to a warehouse.

Stock In
   │
   ├── Validate Product
   ├── Validate Warehouse
   ├── Increase Available Quantity
   ├── Create Inventory Transaction
   ├── Invalidate Cache
   └── Check Inventory Alert
Stock Out
Removes inventory from a warehouse while validating available stock.

Reserve

Moves stock from available quantity to reserved quantity.

Release

Moves reserved stock back to available stock.

Damage

Moves available inventory into damaged inventory.

Adjust

Updates physical inventory quantities.

Reconcile

Compares physical stock with system inventory and adjusts the available quantity accordingly.

🏭 Warehouse Management
Warehouse functionality includes:

Warehouse creation Warehouse retrieval Warehouse updates Warehouse status management Active/inactive warehouse validation Warehouse-based inventory management

Inventory is maintained separately for each warehouse.

📦 Product & Category Management
The product module provides product lifecycle management.

Supported functionality includes:

Product creation Product retrieval Product updates Product status Category association Product validation

Categories provide logical grouping for warehouse products.

🚚 Supplier Management
Supplier management provides functionality for maintaining supplier information used during procurement.

Suppliers are associated with purchase orders and procurement operations.

🧾 Purchase Order Management
The Purchase Order module manages the procurement lifecycle.

The purchase order lifecycle includes:

DRAFT
  │
  ▼
PENDING_APPROVAL
  │
  ├──────────────► REJECTED
  │
  ▼
APPROVED
  │
  ▼
ORDERED
  │
  ├──────────────► PARTIALLY_RECEIVED
  │                         │
  │                         ▼
  └────────────────────► RECEIVED
Supported operations:

Generate purchase order number Create purchase orders Submit purchase orders Approve purchase orders Reject purchase orders Cancel purchase orders Mark orders as ordered Receive purchase orders Partial receiving Quantity validation Product validation Status validation

📥 Goods Receipt Management
Goods receipts are used to record products physically received against purchase orders.

The system validates:

Purchase order existence Purchase order status Duplicate products Products belonging to the purchase order Remaining quantities Received quantities

The system supports:

Full goods receipt Partial goods receipt Inventory updates Purchase order status updates Goods receipt records Atomic database rollback

Example:

Purchase Order
      │
      ▼
   ORDERED
      │
      ▼
Goods Receipt
      │
      ├── Update PO received quantity
      ├── Increase warehouse inventory
      ├── Create receipt
      └── Update PO status
             │
             ├── PARTIALLY_RECEIVED
             │
             └── RECEIVED
🔄 Stock Transfer Management
Stock transfers allow inventory to move between warehouses.

Transfer lifecycle:

REQUESTED
    │
    ├────────────► REJECTED
    │
    ▼
 APPROVED
    │
    ▼
IN_TRANSIT
    │
    ▼
 RECEIVED
Supported operations:

Create transfer Validate source warehouse Validate destination warehouse Prevent same-warehouse transfers Validate products Prevent duplicate products Approve transfers Validate source inventory Reject transfers Dispatch transfers Deduct stock from source warehouse Receive transfers Add stock to destination warehouse

🚨 Inventory Alerts
The system includes inventory alert functionality.

Alerts can be triggered when inventory reaches configured conditions such as low-stock situations.

Alert functionality is integrated with inventory operations.

📊 Analytics
The analytics module provides warehouse and inventory insights.

Supported analytics areas include:

Dashboard analytics Inventory analytics Supplier analytics Warehouse analytics

Analytics endpoints require authentication.

⚡ Redis Inventory Caching
Inventory lookup operations support Redis caching.

The flow is:

Request
   │
   ▼
Check Redis Cache
   │
   ├── Cache Hit ──► Return Cached Inventory
   │
   └── Cache Miss
           │
           ▼
      PostgreSQL
           │
           ▼
      Store in Cache
           │
           ▼
        Return
Inventory cache is invalidated whenever inventory changes.

This reduces unnecessary database queries for frequently accessed inventory information.

🔌 WebSocket Alerts
The application includes WebSocket support for real-time alert communication.

WebSockets can be used to push inventory-related alerts to connected clients without requiring continuous polling.

⏱️ Background Processing
The project contains background processing infrastructure for scheduled and asynchronous tasks.

Components include:

Celery application Background tasks Scheduler

🗄️ Database
The project uses:

PostgreSQL
     │
     ▼
SQLAlchemy ORM
     │
     ▼
Alembic Migrations
Database migrations are managed using Alembic.

🔄 Database Migrations
Initialize migrations:

alembic upgrade head

Create a migration:

alembic revision --autogenerate -m "migration message"

Apply migrations:

alembic upgrade head

Rollback the latest migration:

alembic downgrade -1

⚙️ Environment Configuration
Create a .env file based on .env.example.

Example:

DATABASE_URL=postgresql://postgres:password@localhost:5432/warehouse_db

SECRET_KEY=your-secret-key

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://localhost:6379/0

Do not commit your actual .env file or production secrets to GitHub.

🐍 Local Setup
Clone the repository git clone https://github.com/mdshareef786/Warehouse-Inventory-Procurement-Management-Platform.git cd Warehouse-Inventory-Procurement-Management-Platform
Create a virtual environment
Windows:

python -m venv venv

Activate:

venv\Scripts\activate

Linux/macOS:

python3 -m venv venv source venv/bin/activate 3. Install dependencies pip install -r requirements.txt 4. Configure environment variables

Create:

.env

using:

.env.example

and configure the PostgreSQL and Redis connection details.

Run database migrations alembic upgrade head
Start the FastAPI server uvicorn app.main:app --reload
The API will be available at:

http://127.0.0.1:8000

📚 API Documentation
FastAPI automatically provides interactive API documentation.

Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

The Swagger UI can be used to:

View endpoints Inspect request schemas Test APIs Authenticate using JWT Inspect responses

🧪 Testing
The project contains unit and API authentication tests using Pytest.

Run the complete test suite:

pytest -v

Current test result:

92 passed 1 warning

Test coverage includes:

Authentication Protected endpoints Invalid tokens Invalid credentials Registration validation Refresh token validation Logout validation Inventory Stock in Stock out Insufficient stock Reserve Release Damaged inventory Adjustments Reconciliation Quantity validation Cache hit Cache miss Purchase Orders PO number generation Submission Approval Rejection Cancellation Ordering Full receiving Partial receiving Quantity validation Status validation Goods Receipts Receipt number generation Receipt creation Partial receiving Duplicate product validation Product validation Excess quantity validation Transaction rollback Stock Transfers Transfer number generation Transfer creation Warehouse validation Duplicate product validation Approval Rejection Dispatch Receiving Insufficient stock validation Status validation Other Health endpoint Analytics authentication WebSocket functionality

🧪 Test Command Examples
Run all tests:

pytest -v

Run inventory tests:

pytest -v tests/test_inventory_service.py

Run purchase order tests:

pytest -v tests/test_purchase_order_service.py

Run goods receipt tests:

pytest -v tests/test_goods_receipt_service.py

Run stock transfer tests:

pytest -v tests/test_stock_transfer_service.py

Run API authentication tests:

pytest -v tests/test_inventory.py

🐳 Docker
The project includes Docker configuration.

Build and start the services:

docker-compose up --build

Run in detached mode:

docker-compose up -d

Stop the services:

docker-compose down

🔒 Security Considerations
The application includes several security practices:

JWT authentication Refresh token mechanism Password hashing Protected API routes Role-based authorization Environment-based configuration Secret management through environment variables Input validation using Pydantic Database-level ORM abstraction Custom exception handling

Production deployments should additionally use:

HTTPS Strong production secrets Secure database credentials Restricted CORS configuration Secure Redis configuration Proper logging and monitoring

🔁 Inventory Transaction Flow
Every inventory movement follows a controlled service-layer process.

API Request
    │
    ▼
Authentication
    │
    ▼
Pydantic Validation
    │
    ▼
Inventory Service
    │
    ├── Validate Product
    ├── Validate Warehouse
    ├── Validate Quantity
    │
    ▼
Inventory Repository
    │
    ├── Update Inventory
    └── Create Transaction
    │
    ▼
Cache Invalidation
    │
    ▼
Inventory Alert Check
    │
    ▼
Response
🧱 Design Principles
The application follows several backend engineering principles:

Separation of Concerns

Business logic is kept inside service classes instead of API routes.

Repository Pattern

Database operations are isolated inside repository classes.

Service Layer

Business rules such as inventory validation, procurement workflows, and stock transfers are handled by dedicated services.

Schema Validation

Pydantic schemas validate incoming and outgoing API data.

Centralized Exception Handling

Custom exceptions provide consistent business error handling.

Transaction Safety

Critical operations use database transactions and rollback handling to prevent inconsistent inventory states.

Cache Consistency

Inventory cache is invalidated after stock-changing operations.

# Test Summary
Latest full test execution:

============================= test session starts =============================

collected 92 items

92 passed, 1 warning

============================== 92 passed ==============================

#Future Improvements
Possible future enhancements include:

Advanced reporting Export analytics to CSV/Excel/PDF Advanced inventory forecasting Barcode/QR code integration Audit log dashboard More granular permissions Automated email notifications Advanced Redis caching strategies Production monitoring CI/CD pipeline Cloud deployment Frontend dashboard if required in a future phase

👨‍💻 Author
Rahul raj k
Python Developer
