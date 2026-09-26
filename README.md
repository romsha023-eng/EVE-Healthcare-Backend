# EVE Healthcare Diagnostic Test Booking & Payment Backend Service

Production-quality backend engineering assignment built for an SDE Intern role at **EVE Healthcare**.

This service provides robust RESTful APIs for user authentication, diagnostic centre and test management, diagnostic booking scheduling, simulated payment processing, and idempotent payment webhooks.

---

## 1. Project Overview

The **EVE Healthcare Diagnostic Booking Service** enables healthcare users to search diagnostic centres and tests, schedule test appointments, process simulated payments, and handle real-time payment gateway webhooks safely.

Key highlights include:
- **Clean Architecture**: Decoupled routes, schemas, services, ORM models, and database access.
- **Strict Financial & State Guarantees**: Derived monetary pricing, `Numeric(10, 2)` precision, transactional state updates, and idempotent webhook handling.
- **Role-Based Access Control (RBAC)**: Fine-grained access control differentiating standard `USER`s from `ADMIN` administrators.
- **Automated Test Coverage**: 100% passing test suite built using `pytest` and `httpx`.

---

## 2. Features

- **Authentication & Security**:
  - User signup and login with bcrypt password hashing.
  - JWT token generation and verification with expiration.
  - Role-based authorization (`USER` and `ADMIN`).
- **Diagnostic Centres & Tests**:
  - Centre and Test management with Many-to-Many associations.
  - Admin-only creation, modification, and test assignment endpoints.
- **Booking Workflows**:
  - Appointment scheduling with future date validation.
  - Test availability checking at selected centres.
  - User booking isolation (users only access their own bookings; admins view all).
  - Explicit booking state machine (`PENDING`, `CONFIRMED`, `FAILED`, `CANCELLED`).
- **Simulated Payment Gateway**:
  - Transactional payment execution matching exact booking amounts.
  - Duplicate payment prevention.
  - Automatic booking status transitions.
- **Idempotent Payment Webhook**:
  - Processing webhook events from simulated payment gateways.
  - Idempotency key tracking via `WebhookEvent.event_id` and database UNIQUE constraints.
  - Concurrent duplicate payload protection.

---

## 3. Tech Stack

- **Language**: Python 3.12+ (Tested on Python 3.13)
- **Framework**: FastAPI (ASGI server: Uvicorn)
- **Database**: PostgreSQL
- **ORM & Migrations**: SQLAlchemy 2.x, Alembic
- **Data Validation & Settings**: Pydantic v2, Pydantic Settings
- **Authentication**: PyJWT, bcrypt
- **Testing**: Pytest, HTTPX, FastAPI TestClient
- **Containerization**: Docker, Docker Compose
- **API Documentation**: OpenAPI / Swagger UI (`/docs`)

---

## 4. Architecture

The application adopts a **Layered Service Architecture**:

```
           +-----------------------------------------+
           |         HTTP Request (FastAPI)          |
           +-----------------------------------------+
                                |
                                v
           +-----------------------------------------+
           |           API Routers (app/api)         |
           |     Validation & HTTP Status Codes      |
           +-----------------------------------------+
                                |
                                v
           +-----------------------------------------+
           |        Service Layer (app/services)     |
           |  Business Logic & State Transitions     |
           +-----------------------------------------+
                                |
                                v
           +-----------------------------------------+
           |         Data Layer (app/db/models)      |
           |    SQLAlchemy ORM & Database Session    |
           +-----------------------------------------+
```

---

## 5. Folder Structure

```
d:\EVE/
│
├── app/
│   ├── main.py                # FastAPI application entry point & error handlers
│   ├── core/
│   │   ├── config.py          # App settings via pydantic-settings
│   │   └── security.py        # Bcrypt hashing & JWT utilities
│   ├── db/
│   │   ├── database.py        # SQLAlchemy engine & session maker
│   │   ├── base.py            # Base declarative model import for Alembic
│   │   └── models/            # SQLAlchemy ORM models
│   │       ├── user.py
│   │       ├── centre.py
│   │       ├── test.py
│   │       ├── booking.py
│   │       ├── payment.py
│   │       └── webhook.py
│   ├── schemas/               # Pydantic v2 schemas for request/response validation
│   │   ├── auth.py
│   │   ├── centre.py
│   │   ├── test.py
│   │   ├── booking.py
│   │   ├── payment.py
│   │   └── webhook.py
│   ├── api/                   # FastAPI route controllers
│   │   ├── auth.py
│   │   ├── centres.py
│   │   ├── tests.py
│   │   ├── bookings.py
│   │   └── payments.py
│   ├── services/              # Pure business logic layer
│   │   ├── auth_service.py
│   │   ├── booking_service.py
│   │   ├── payment_service.py
│   │   └── webhook_service.py
│   └── dependencies/          # Dependency injection (Auth & DB session)
│       ├── auth.py
│       └── db.py
│
├── alembic/                   # Database migration files
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_migration.py
│
├── tests/                     # Pytest suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_centres.py
│   ├── test_bookings.py
│   ├── test_payments.py
│   └── test_webhooks.py
│
├── .env.example               # Environment template
├── alembic.ini                # Alembic configuration
├── Dockerfile                 # Multi-stage Docker image script
├── docker-compose.yml         # Container orchestration (API + PostgreSQL)
├── pytest.ini                 # Pytest runner configuration
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## 6. Database / Schema Design

```mermaid
erDiagram
    users ||--o{ bookings : places
    diagnostic_centres ||--o{ centre_tests : offers
    diagnostic_tests ||--o{ centre_tests : available_at
    diagnostic_centres ||--o{ bookings : hosts
    diagnostic_tests ||--o{ bookings : includes
    bookings ||--o{ payments : has

    users {
        int id PK
        string name
        string email UNIQUE
        string password_hash
        enum role "USER | ADMIN"
        datetime created_at
    }

    diagnostic_centres {
        int id PK
        string name
        string location
        datetime created_at
    }

    diagnostic_tests {
        int id PK
        string name
        string description
        numeric price
        datetime created_at
    }

    centre_tests {
        int centre_id PK, FK
        int test_id PK, FK
    }

    bookings {
        int id PK
        int user_id FK
        int test_id FK
        int centre_id FK
        datetime appointment_datetime
        numeric amount
        enum status "PENDING | CONFIRMED | FAILED | CANCELLED"
        datetime created_at
        datetime updated_at
    }

    payments {
        int id PK
        int booking_id FK
        numeric amount
        enum status "SUCCESS | FAILED"
        string provider_transaction_id
        datetime created_at
        datetime updated_at
    }

    webhook_events {
        int id PK
        string event_id UNIQUE
        string event_type
        text payload
        datetime processed_at
        datetime created_at
    }
```

---

## 7. Setup Instructions

### Prerequisites
- Python 3.12+ installed
- PostgreSQL database server OR Docker Desktop

---

## 8. Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

`.env` content:
```env
DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5432/eve_db
JWT_SECRET=super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 9. Docker Setup

To launch the complete stack (API + PostgreSQL database):

```bash
docker compose up --build
```

The API will automatically execute Alembic migrations on startup and be available at `http://localhost:8000`.

To stop the containers:
```bash
docker compose down
```

---

## 10. Running Locally Without Docker

1. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Local PostgreSQL Database** (or use local SQLite for testing by setting `DATABASE_URL=sqlite:///./eve_test.db` in `.env`).

4. **Run Alembic Migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start FastAPI Application**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 11. Running Migrations

- Apply all pending migrations:
  ```bash
  alembic upgrade head
  ```
- Rollback last migration:
  ```bash
  alembic downgrade -1
  ```
- Generate new migration after model changes:
  ```bash
  alembic revision --autogenerate -m "describe changes"
  ```

---

## 12. Running Tests

Run the full automated test suite using `pytest`:

```bash
pytest -v
```

All 39 automated tests run in an isolated in-memory SQLite database environment.

> **Verification Status**:
> - Unit & Integration Test Suite (Pytest): **VERIFIED** (39/39 Passed)
> - Live PostgreSQL Runtime: **UNVERIFIED AT RUNTIME** (Requires Docker daemon on host environment)
> - Live Docker Container Execution: **UNVERIFIED AT RUNTIME** (Requires Docker daemon on host environment)

---

## 13. Swagger Documentation

Interactive OpenAPI Swagger UI is available at:

```
http://localhost:8000/docs
```

ReDoc is available at:
```
http://localhost:8000/redoc
```

---

## 14. API Endpoints

| Method | Endpoint | Access Level | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Public | Register new user (`USER` or `ADMIN`) |
| `POST` | `/auth/login` | Public | Login with credentials and receive JWT |
| `GET` | `/centres/` | Public / Auth | List all diagnostic centres |
| `GET` | `/centres/{id}` | Public / Auth | Get centre details with assigned tests |
| `POST` | `/centres/` | ADMIN | Create diagnostic centre |
| `POST` | `/centres/{c_id}/tests/{t_id}` | ADMIN | Assign test to centre |
| `DELETE` | `/centres/{c_id}/tests/{t_id}` | ADMIN | Remove test from centre |
| `GET` | `/tests/` | Public / Auth | List all diagnostic tests |
| `GET` | `/tests/{id}` | Public / Auth | Get test details |
| `POST` | `/tests/` | ADMIN | Create diagnostic test |
| `POST` | `/bookings/` | Authenticated | Book a diagnostic test at a centre |
| `GET` | `/bookings/` | Authenticated | List bookings (User sees own; Admin sees all) |
| `GET` | `/bookings/{id}` | Authenticated | Get booking details (User sees own; Admin sees all) |
| `PATCH` | `/bookings/{id}/cancel` | Authenticated | Cancel a pending booking |
| `POST` | `/payments/` | Authenticated | Simulate payment for a booking |
| `POST` | `/payments/webhook/` | Public | Provider webhook callback (Idempotent) |

---

## 15. Example Requests and Responses

### 1. User Signup (`POST /auth/signup`)
**Request**:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword123",
  "role": "USER"
}
```
**Response (201 Created)**:
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "USER",
  "created_at": "2026-09-26T02:00:00Z"
}
```

### 2. User Login (`POST /auth/login`)
**Request**:
```json
{
  "email": "jane@example.com",
  "password": "securepassword123"
}
```
**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "USER",
    "created_at": "2026-09-26T02:00:00Z"
  }
}
```

### 3. Create Booking (`POST /bookings/`)
**Headers**: `Authorization: Bearer <token>`
**Request**:
```json
{
  "centre_id": 1,
  "test_id": 2,
  "appointment_datetime": "2026-10-15T10:30:00Z"
}
```
**Response (201 Created)**:
```json
{
  "id": 10,
  "user_id": 1,
  "centre_id": 1,
  "test_id": 2,
  "appointment_datetime": "2026-10-15T10:30:00Z",
  "amount": "150.00",
  "status": "PENDING",
  "created_at": "2026-09-26T02:05:00Z",
  "updated_at": "2026-09-26T02:05:00Z"
}
```

### 4. Payment Webhook (`POST /payments/webhook/`)
**Request**:
```json
{
  "event_id": "evt_998877",
  "payment_id": "pay_554433",
  "booking_id": 10,
  "status": "SUCCESS"
}
```
**Response (200 OK - First Processing)**:
```json
{
  "message": "Webhook event processed successfully",
  "event_id": "evt_998877",
  "processed": true
}
```
**Response (200 OK - Repeated Duplicate Delivery)**:
```json
{
  "message": "Event already processed",
  "event_id": "evt_998877",
  "processed": false
}
```

---

## 16. Booking Lifecycle

```
                     +---------------+
                     |  POST /booking|
                     +---------------+
                             |
                             v
                     +---------------+
                     |    PENDING    |
                     +---------------+
                       /     |     \
         Payment SUCCESS     |      Payment FAILED
             /               |              \
            v         PATCH /cancel          v
    +---------------+        |        +---------------+
    |   CONFIRMED   |        v        |    FAILED     |
    +---------------+ +---------------+ +---------------+
                      |   CANCELLED   |
                      +---------------+
```

---

## 17. Payment Flow

1. Booking creation sets status to `PENDING` and records amount derived from test price.
2. User or payment provider calls `POST /payments/` or sends webhook event to `POST /payments/webhook/`.
3. System verifies booking existence and checks that status is `PENDING`.
4. Payment amount is strictly checked against `booking.amount`.
5. In a single atomic database transaction:
   - Payment record is inserted.
   - On `SUCCESS`: `booking.status` becomes `CONFIRMED`.
   - On `FAILED`: `booking.status` becomes `FAILED`.

---

## 18. Webhook Idempotency Explanation

Payment providers frequently retry webhook events due to network delays or timeouts. To guarantee **Idempotency**:

1. **Unique Idempotency Key**: Each webhook request carries a unique `event_id`.
2. **Database Constraint**: `WebhookEvent.event_id` is defined as `UNIQUE` with a dedicated index in PostgreSQL.
3. **Atomic Processing & Deduplication**:
   - Before applying state changes, the service checks if `event_id` exists in `webhook_events`.
   - If found, it returns `200 OK` with `processed: false` immediately.
   - If new, it records `WebhookEvent` and updates `Payment` & `Booking` status in a single database transaction.
   - If two concurrent requests arrive simultaneously, the database `UNIQUE` constraint raises an `IntegrityError`, causing one transaction to roll back safely while returning a successful response without corrupting data or creating duplicate payments.

---

## 19. Important Assumptions

1. **Simulated Payments**: Payment processing does not connect to external gateways like Stripe or Razorpay; payment status is passed directly in requests or webhooks.
2. **Appointment Validation**: Appointment scheduling validates that date/time is in the future. External capacity management / doctor availability is outside scope.
3. **Derived Pricing**: Booking amounts are untrusted from the request and always calculated from the official `DiagnosticTest.price`.
4. **Test-Centre Relationship**: A diagnostic test must be assigned to a diagnostic centre (`centre_tests`) before a booking can be placed.
5. **Monetary Precision**: All currency amounts use `Numeric(10, 2)` / Python `Decimal` to avoid floating-point inaccuracies.
6. **Role Model**: Users possess either `USER` or `ADMIN` roles. Standard operations require authentication; centre/test modifications require `ADMIN`.

---

## 20. Edge Cases Handled

1. Duplicate signup email handled with `400 Bad Request`.
2. Invalid login credentials handled with `401 Unauthorized`.
3. Expired, missing, or malformed JWT token handled with `401 Unauthorized`.
4. Invalid centre ID or test ID handled with `404 Not Found`.
5. Attempting to book a test not assigned to the selected centre handled with `400 Bad Request`.
6. Past appointment date/time handled with `400 Bad Request`.
7. Non-admin users attempting to modify centres or tests handled with `403 Forbidden`.
8. Users attempting to access or view another user's booking handled with `403 Forbidden`.
9. Attempting to cancel an already cancelled or confirmed booking handled with `400 Bad Request`.
10. Attempting payment for a cancelled booking handled with `400 Bad Request`.
11. Duplicate payments for an already confirmed booking handled with `400 Bad Request`.
12. Payment amount mismatch handled with `400 Bad Request`.
13. Duplicate webhook events handled idempotently returning `200 OK`.
14. Concurrent duplicate webhooks safely handled via DB transactions and unique constraints.
15. Invalid payment or webhook request payloads handled with `422 Unprocessable Entity`.

---

## 21. What I Would Improve With More Time

1. **Redis Caching & Lock Manager**: Implement distributed locking (`Redlock`) for high-concurrency booking slots and webhook idempotency.
2. **Celery / Background Tasks**: Asynchronously dispatch email / SMS notifications for booking confirmations.
3. **RefreshToken Support**: Add JWT refresh tokens and token blacklisting on logout.
4. **Time-Slot Capacity Management**: Define operating hours and maximum concurrent bookings per slot for centres.
5. **Audit Logging & Telemetry**: Integrate Structured Logging (`structlog`) and Prometheus metrics for monitoring API performance.
