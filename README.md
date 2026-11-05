# ErrorLog Management API

An asynchronous, role-based backend system for reporting, assigning, tracking, reviewing, and resolving application or network-related errors through a structured ticket workflow.

## 1. Project Abstract

ErrorLog Management is a REST API designed to centralise the process of reporting and handling technical issues within an organisation. Employees can create tickets, select an issue category, add remarks, and attach supporting images. Administrators can manage users, categories, ticket assignments, and ticket progress, while managers can review approval requests and record approval or rejection decisions.

The system applies category-based rules such as default SLA hours and approval requirements. It maintains a separate status history and remarks for traceability, supports overdue-ticket tracking, and sends email notifications for selected workflow events. JWT-based authentication and role-based authorisation protect the endpoints. The application is built with FastAPI, asynchronous SQLAlchemy, and PostgreSQL, following a layered architecture that separates API routes, schemas, services, repository interfaces, and database operations. Automated tests are included for API routes and service-layer logic.

## 2. Main Features

- JWT authentication with access-token and refresh-token endpoints.
- Role-based access for **ADMIN**, **MANAGER**, and **EMPLOYEE** users.
- User and error-category management.
- Ticket creation, assignment, retrieval, status updates, closure, and overdue-ticket listing.
- Category-driven SLA and approval rules.
- Manager approval and rejection workflow with decision reasons.
- Ticket remarks and chronological status history.
- JPEG and PNG ticket-image uploads and deletion.
- Email notifications through the Mailjet API.
- Request logging, application logging, health check, and custom exception handling.

## 3. Technology Stack and Concepts

| Technology / Concept | Purpose |
|---|---|
| Python | Main backend programming language. |
| FastAPI | Builds asynchronous REST endpoints and provides dependency injection and OpenAPI documentation. |
| Pydantic | Validates request data and defines response schemas. |
| Pydantic Settings | Loads application configuration from environment variables and `.env`. |
| PostgreSQL | Stores application data in relational tables. |
| SQLAlchemy 2.x Async ORM | Maps Python classes to tables and performs asynchronous database operations using `AsyncSession`. |
| asyncpg | Asynchronous PostgreSQL driver. |
| Alembic | Tracks and applies database schema changes through migrations. |
| JWT (PyJWT) | Creates and verifies signed access and refresh tokens. |
| Argon2 (`pwdlib`) | Hashes passwords before storing them. |
| RBAC | Restricts operations according to the logged-in user's role. |
| Repository Pattern | Separates database access from business logic. |
| Repository Interfaces | Define contracts for repository implementations. |
| Service Layer | Holds business rules and coordinates repository operations. |
| Dependency Injection | Supplies database sessions and services to route handlers. |
| SQLAlchemy Relationships and Foreign Keys | Connect related records and maintain referential integrity. |
| Pytest / pytest-asyncio | Runs unit tests and API tests, including asynchronous test setup. |
| AsyncMock | Mocks asynchronous repository or service dependencies in unit tests. |
| Ruff | Checks Python code quality, imports, and formatting. |
| HTTPX | Makes asynchronous HTTP requests to the Mailjet API and supports HTTP testing dependencies. |
| aiofiles | Reads and writes uploaded image files asynchronously. |
| python-multipart | Handles multipart form data for file uploads and form-based login. |

## 4. Database Design

The application uses PostgreSQL with seven main tables. Each table has a separate responsibility to keep ticket data, workflow records, and user activity organised.

| Table | Purpose |
|---|---|
| `users` | Stores login details, password hashes, user roles, department, active status, and the optional manager relationship. |
| `error_categories` | Stores issue categories, issue types, descriptions, default SLA hours, and whether tickets in the category require approval by default. |
| `error_tickets` | Stores the main ticket details, ticket number, creator, category, assigned administrator, priority, status, approval requirement, and due date. |
| `ticket_approvals` | Stores manager approval requests, their status, decision reason, and decision timestamp for a ticket. |
| `ticket_remarks` | Stores comments added to a ticket, the user who added each remark, and its creation time. |
| `ticket_status_history` | Records each ticket status transition, including the previous status, new status, user who changed it, and timestamp. |
| `ticket_images` | Stores metadata for images attached to tickets, including original filename, stored file path, content type, file size, uploader, and upload time. |

### Main relationships

- One user can create many tickets; each ticket has one creator.
- One error category can be associated with many tickets; each ticket belongs to one category.
- A user can be assigned as the administrator for multiple tickets.
- A ticket can have multiple approval records, remarks, status-history entries, and image records.
- A manager can review multiple approval records.
- A user can add multiple remarks, change multiple ticket statuses, and upload multiple ticket images.
- A user can optionally reference another user as their manager through `users.manager_id`.

Foreign keys connect related tables. The models also define constraints and indexes for selected status, role, category, ticket, and timestamp fields.

## 5. Project Folder Structure

```text
ErrorLog Management/
│
├── alembic/                         # Database migration environment and revision files
│   └── versions/                    # Versioned database schema changes
│
├── app/
│   ├── api/
│   │   ├── dependency/              # Shared FastAPI dependencies and service providers
│   │   └── routers/                 # API endpoints grouped by feature
│   │
│   ├── core/                        # Application settings and security utilities
│   ├── database/                    # SQLAlchemy base, engine, and session configuration
│   ├── exceptions/                  # Custom exceptions and exception handlers
│   ├── middleware/                   # HTTP request logging middleware
│   ├── models/                       # SQLAlchemy database models
│   ├── repositories/
│   │   ├── interfaces/              # Abstract repository contracts
│   │   └── implementations/         # Database access implementations
│   ├── schemas/                      # Pydantic request and response schemas
│   ├── scripts/                      # Seed-user, ticket-number, and file-handling helpers
│   ├── services/                     # Business logic for each application feature
│   ├── utils/                        # Logging configuration and shared utilities
│   └── main.py                       # FastAPI application entry point
│
├── tests/
│   ├── routers/                     # API endpoint tests
│   ├── unit_testing/                # Service-layer unit tests
│   └── conftest.py                  # Shared fixtures and test database configuration
│
├── uploads/                          # Stored ticket image files
├── logs/                             # Application log output
├── .env.example                      # Example environment configuration
├── alembic.ini                       # Alembic configuration
├── pyproject.toml                    # Ruff and pytest configuration
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

## 6. Environment Configuration

Create a local `.env` file in the project root using `.env.example` as the reference. Replace all example values with your own configuration. Do not commit `.env` or share real credentials.

| Variable | Description |
|---|---|
| `APP_NAME`, `APP_VERSION` | Application name and version. |
| `API_PREFIX` | Common API prefix; the current example uses `/api/v1`. |
| `DATABASE_NAME` | PostgreSQL application database name. |
| `DATABASE_USER` | PostgreSQL username. |
| `DATABASE_PASSWORD` | PostgreSQL password. |
| `DATABASE_HOST`, `DATABASE_PORT` | PostgreSQL host and port. |
| `DATABASE_DRIVER` | SQLAlchemy driver; use `postgresql+asyncpg`. |
| `TEST_DATABASE_NAME` | Separate PostgreSQL database used by pytest. |
| `TEST_DATABASE_USER`, `TEST_DATABASE_PASSWORD` | Test database credentials. |
| `TEST_DATABASE_HOST`, `TEST_DATABASE_PORT` | Test database host and port. |
| `TEST_DATABASE_DRIVER` | Test database driver; use `postgresql+asyncpg`. |
| `JWT_SECRET_KEY` | Random secret used to sign JWTs; provide at least 32 characters. |
| `JWT_ALGORITHM` | JWT signing algorithm; configured as `HS256` in the example. |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime in minutes. |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token lifetime in days. |
| `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Optional initial administrator account details. |
| `MANAGER_USERNAME`, `MANAGER_EMAIL`, `MANAGER_PASSWORD` | Optional initial manager account details. |
| `MAILJET_API_KEY`, `MAILJET_API_SECRET` | Mailjet API credentials. |
| `MAILJET_FROM`, `MAILJET_APPROVAL_FROM` | Verified sender addresses for application and approval emails. |
| `MAIL_FROM`, `MAIL_FROM_NAME` | Default sender address and display name. |

Create a separate test database before running the test suite. The test configuration is designed to reject using the application database as the test database.

## 7. Installation and Running the Application

Commands below are intended to be run from the project root directory.

### 7.1 Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```



### 7.2 Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 7.3 Configure environment

```bash
copy .env.example .env
```


Edit `.env` and provide valid application database, test database, JWT, seed-user, and Mailjet settings. Create the PostgreSQL application database before applying migrations.

### 7.4 Apply database migrations

```bash
alembic upgrade head
```

### 7.5 Start the API

```bash
uvicorn app.main:app --reload
```

The API will normally be available at `http://127.0.0.1:8000`.

## 8. API Documentation

FastAPI generates interactive API documentation automatically.

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`
- **Health check:** `GET /api/v1/health`

The configured API prefix is `/api/v1`. The main endpoint groups are:

| Feature | Method and endpoint | Purpose |
|---|---|---|
| Authentication | `POST /api/v1/auth/login` | Log in and obtain tokens. |
| Authentication | `POST /api/v1/auth/refresh` | Obtain a refreshed access token. |
| Authentication | `GET /api/v1/auth/me` | Retrieve the authenticated user's details. |
| Users | `/api/v1/users` | Create and list users. |
| Users | `/api/v1/users/{user_id}` | Retrieve, update, or deactivate a user. |
| Categories | `/api/v1/categories` | Create and list error categories. |
| Categories | `/api/v1/categories/{category_id}` | Retrieve or update a category. |
| Tickets | `POST /api/v1/tickets` | Create a ticket. |
| Tickets | `GET /api/v1/tickets/my-tickets` | List tickets visible to the current employee. |
| Tickets | `GET /api/v1/tickets/all-tickets` | List tickets available to authorised users. |
| Tickets | `GET /api/v1/tickets/overdue` | List overdue tickets. |
| Tickets | `GET /api/v1/tickets/{ticket_id}` | Retrieve a ticket. |
| Tickets | `PATCH /api/v1/tickets/{ticket_id}/status` | Update ticket status. |
| Tickets | `PATCH /api/v1/tickets/{ticket_id}/close` | Close a ticket. |
| Remarks | `POST /api/v1/tickets/{ticket_id}/remarks` | Add a ticket remark. |
| Remarks | `GET /api/v1/tickets/{ticket_id}/remarks` | Retrieve ticket remarks. |
| History | `GET /api/v1/tickets/{ticket_id}/history` | Retrieve ticket status history. |
| Approvals | `GET /api/v1/approvals/pending-approvals` | List pending approval requests. |
| Approvals | `GET /api/v1/approvals/{approval_id}` | Retrieve an approval request. |
| Approvals | `PATCH /api/v1/approvals/{approval_id}/approve` | Approve a request. |
| Approvals | `PATCH /api/v1/approvals/{approval_id}/reject` | Reject a request. |
| Ticket images | `POST /api/v1/tickets/{ticket_id}/images` | Upload an image to a ticket. |
| Ticket images | `DELETE /api/v1/tickets/{ticket_id}/images/{image_id}` | Delete a ticket image. |

Use Swagger UI to inspect request schemas, response schemas, required authentication, and the full set of endpoint details.

## 9. Running Tests with Pytest

The test suite is organised into router/API tests and service unit tests. The shared `tests/conftest.py` configures a separate asynchronous PostgreSQL test engine, creates and drops test tables, clears data between tests, overrides the application database dependency, and mocks email delivery.

Make sure the test database variables in `.env` point to a dedicated database before running tests.

### Run all tests

```bash
pytest
```

### Run with detailed output

```bash
pytest -v
```

### Run only router/API tests

```bash
pytest tests/api_testing -v
```

### Run only service unit tests

```bash
pytest tests/unit_testing -v
```

### Run a specific test file

```bash
pytest tests/unit_testing/test_ticket_service.py -v
```

### Run a specific test function

```bash
pytest tests/unit_testing/test_ticket_service.py::test_function_name -v
```

### Run with short summary for failures

```bash
pytest -ra
```

## 10. Database Migrations with Alembic

Alembic is configured to use the asynchronous SQLAlchemy database URL and the model metadata in `app/database/base.py`.

### Apply all migrations

```bash
alembic upgrade head
```

### Create a new migration after changing SQLAlchemy models

```bash
alembic revision --autogenerate -m "describe_your_change"
```

Review the generated migration before applying it. Autogeneration may not identify every database change correctly.

### Apply the latest migration

```bash
alembic upgrade head
```

### Check the current database revision

```bash
alembic current
```

### View migration history

```bash
alembic history
```

### Move back by one migration

```bash
alembic downgrade -1
```

### Move to the base revision

```bash
alembic downgrade base
```

### View the SQL without applying it

```bash
alembic upgrade head --sql
```

Use downgrade commands carefully, especially on databases containing important data. Always inspect migration files and back up important data before schema changes.

## 11. Code Quality with Ruff

Ruff is configured in `pyproject.toml` with a line length of 88 characters and the `E`, `F`, `I`, `UP`, and `B` rule groups.

### Check the project for lint issues

```bash
ruff check .
```

### Automatically fix supported lint issues

```bash
ruff check . --fix
```

### Format the project

```bash
ruff format .
```

### Check formatting without changing files

```bash
ruff format . --check
```

### Check a specific folder

```bash
ruff check app tests
```

## 12. File Upload Notes

Ticket images are stored in the local `uploads/` directory, while their metadata is stored in the `ticket_images` table. The current file handler accepts JPEG and PNG images and enforces a maximum size of 10 MB. The stored filename is generated uniquely rather than using the original filename as the storage name.

## 13. Logging and Error Handling

- HTTP request logging is implemented through middleware.
- Application logging configuration is maintained in `app/utils/logging_config.py`.
- Log output is written under the `logs/` directory.
- Application-specific exceptions are defined in `app/exceptions/custom_exceptions.py`.
- Centralised exception handlers convert known application errors into appropriate HTTP responses.

## 14. Important Notes

- Keep `.env` and all real credentials out of version control.
- Use a dedicated PostgreSQL database for automated tests.
- Apply Alembic migrations before starting the application against a newly created database.
- Review autogenerated migration scripts before applying them.
- Ensure the configured Mailjet sender addresses are verified with Mailjet if email notifications are required.
- The `uploads/` directory must be writable by the application process.
