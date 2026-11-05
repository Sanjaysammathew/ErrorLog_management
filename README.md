# ErrorLog Management API

An asynchronous backend application for managing employee-reported
errors and support tickets through a structured workflow. The system
provides role-based access for employees, administrators, and managers,
allowing tickets to be created, categorised, assigned, tracked,
reviewed, and closed. It also maintains ticket remarks and status
history, supports approval decisions, stores ticket image attachments,
and sends email notifications for important events.

The application is built with **FastAPI**, **Python**, **SQLAlchemy 2.x
(async ORM)**, and **PostgreSQL**. It follows a layered architecture
that separates HTTP routing, request validation, business rules, data
access, and database models. This separation improves maintainability,
testability, and the ability to extend individual modules without
placing the entire application in route handlers.

------------------------------------------------------------------------

## 1. Project Objectives

The project aims to provide a centralised system for recording and
managing application errors and support requests.

Key objectives:

-   Provide authenticated access for different user roles.
-   Allow employees to create tickets and view tickets they are
    permitted to access.
-   Organise tickets using configurable error categories and issue
    types.
-   Apply category-driven ticket rules, including default SLA hours and
    approval requirements where configured.
-   Allow administrators to manage users, categories, ticket status, and
    ticket closure.
-   Allow managers to review pending approval requests and approve or
    reject them with a decision reason.
-   Preserve ticket remarks and a chronological status history for
    traceability.
-   Support JPEG and PNG ticket image uploads with file validation and
    size limits.
-   Notify relevant users about selected ticket and approval events
    through email.
-   Provide automated tests for API routes and service-layer business
    logic.

## 2. Main Features

### Authentication and authorisation

-   User login using username and password.
-   JWT access and refresh tokens.
-   Access-token validation on protected endpoints.
-   Role-based access control for `ADMIN`, `MANAGER`, and `EMPLOYEE`.
-   Active-user checks for authenticated operations.
-   Password hashing using Argon2 through `pwdlib`.

### User management

-   Administrator-controlled user creation and maintenance.
-   User listing with pagination.
-   User deactivation rather than permanently removing the account.
-   Manager-to-employee association where applicable.

### Category management

-   Create, retrieve, update, and deactivate error categories.
-   Store category-specific issue information and ticket-handling rules.
-   Use category configuration when processing newly created tickets.

### Ticket management

-   Create tickets for the authenticated employee.
-   Generate ticket numbers through a dedicated helper.
-   Retrieve an employee's own tickets or all tickets according to role
    permissions.
-   Retrieve individual tickets and overdue tickets.
-   Update ticket status and close tickets through authorised
    operations.
-   Apply ticket workflow rules in the service layer.

### Approval workflow

-   Retrieve approval requests assigned to a manager.
-   View an individual approval request.
-   Approve or reject a request.
-   Store the decision and optional reason.
-   Notify the relevant administrator about the decision.

### Remarks and status history

-   Add remarks to tickets.
-   Retrieve ticket remarks subject to access rules.
-   Record and retrieve ticket status transitions.
-   Keep ticket discussion and status auditing separate from the main
    ticket record.

### Ticket image attachments

-   Upload JPEG and PNG images to a ticket.
-   Validate the filename, extension, content type, and maximum file
    size.
-   Generate unique stored filenames to avoid collisions.
-   Store attachment metadata in the database.
-   Delete an attachment through an authorised endpoint.

### Notifications, logging, and health checks

-   Send configured email notifications through the Mailjet API.
-   Log application activity to a rotating log file.
-   Log HTTP request information through middleware.
-   Check application/database connectivity through the health endpoint.

------------------------------------------------------------------------

## 3. Technology Stack and Concepts

  -----------------------------------------------------------------------
  Technology / Concept                Purpose in this project
  ----------------------------------- -----------------------------------
  Python                              Main programming language for
                                      backend implementation.

  FastAPI                             Builds asynchronous REST API
                                      endpoints and integrates dependency
                                      injection and OpenAPI
                                      documentation.

  Pydantic                            Validates incoming request data and
                                      defines structured API response
                                      schemas.

  Pydantic Settings                   Loads and validates application
                                      configuration from environment
                                      variables and `.env`.

  PostgreSQL                          Relational database used to persist
                                      users, categories, tickets,
                                      approvals, remarks, history, and
                                      attachment metadata.

  SQLAlchemy 2.x                      ORM used to map Python model
                                      classes to database tables and
                                      execute database operations.

  Async SQLAlchemy                    Uses `AsyncEngine`, `AsyncSession`,
                                      and asynchronous database
                                      operations with the `asyncpg`
                                      driver.

  Alembic                             Maintains version-controlled
                                      database schema migrations.

  JWT                                 Provides signed access and refresh
                                      tokens for authentication.

  Argon2                              Hashes passwords before they are
                                      stored in the database.

  Role-based access control (RBAC)    Restricts operations according to
                                      the authenticated user's role.

  Dependency Injection                Supplies database sessions and
                                      service instances to route handlers
                                      using FastAPI dependencies.

  Repository Pattern                  Separates database access
                                      operations from business logic.

  Service Layer                       Contains application rules and
                                      coordinates repositories and
                                      supporting services.

  Repository Interfaces               Define repository contracts so
                                      services can depend on abstractions
                                      rather than concrete data-access
                                      implementations.

  pytest                              Runs automated unit and API tests.

  pytest-asyncio                      Supports asynchronous test
                                      functions and fixtures.

  FastAPI TestClient / HTTPX          Sends requests to the application
                                      during API tests.

  `unittest.mock.AsyncMock`           Replaces asynchronous dependencies
                                      when testing services in isolation.

  Ruff                                Checks Python code quality, common
                                      errors, import ordering, and
                                      formatting.

  aiofiles                            Writes uploaded files
                                      asynchronously.

  python-multipart                    Parses multipart form data used by
                                      file-upload endpoints.

  HTTPX                               Makes asynchronous HTTP requests to
                                      the Mailjet email API.

  RotatingFileHandler                 Writes application logs to files
                                      with size-based rotation.
  -----------------------------------------------------------------------

### Architecture and engineering concepts applied

1.  **Layered architecture:** The API, service, repository, model, and
    schema layers have distinct responsibilities.
2.  **Separation of concerns:** Route handlers handle HTTP concerns,
    services handle business rules, and repositories handle persistence.
3.  **Dependency inversion:** Services can use repository interfaces
    instead of being tightly coupled to concrete repository classes.
4.  **Dependency injection:** FastAPI dependencies provide the current
    user, database session, and service dependencies.
5.  **Asynchronous programming:** Database operations, file operations,
    and email HTTP requests use asynchronous APIs.
6.  **Data validation:** Pydantic schemas validate request payloads
    before business logic processes them.
7.  **ORM mapping and relationships:** SQLAlchemy models represent
    relational tables, keys, constraints, and associations.
8.  **Database normalisation:** Related ticket information is stored in
    separate tables rather than being duplicated in one large record.
9.  **Schema migration management:** Alembic records database changes as
    ordered revision scripts.
10. **Automated testing:** Unit tests isolate service behaviour with
    mocks; router tests exercise HTTP endpoints against a dedicated test
    database.
11. **Security practices:** Password hashing, signed JWTs, role checks,
    input validation, and a separate test database are used.
12. **Error handling:** Custom exceptions and registered exception
    handlers provide consistent API error responses.

------------------------------------------------------------------------

## 4. Project Structure

The following is the application source structure. Cache directories,
the local virtual environment, generated logs, and Git internals are
intentionally excluded.

``` text
ErrorLog Management/
│
├── app/
│   ├── api/
│   │   ├── dependency/
│   │   │   └── dependencies.py
│   │   └── routers/
│   │       ├── approval.py
│   │       ├── auth.py
│   │       ├── base.py
│   │       ├── categories.py
│   │       ├── health.py
│   │       ├── history.py
│   │       ├── remarks.py
│   │       ├── tickets.py
│   │       ├── ticket_image_router.py
│   │       └── users.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── connection.py
│   │   └── session.py
│   │
│   ├── exceptions/
│   │   ├── custom_exceptions.py
│   │   ├── handlers.py
│   │   └── register_handlers.py
│   │
│   ├── middleware/
│   │   └── request_logging.py
│   │
│   ├── models/
│   │   ├── ErrorCategory.py
│   │   ├── error_ticket.py
│   │   ├── ticket_approval.py
│   │   ├── ticket_image.py
│   │   ├── ticket_remark.py
│   │   ├── ticket_status_history.py
│   │   └── user.py
│   │
│   ├── repositories/
│   │   ├── implementations/
│   │   │   ├── approval_repository.py
│   │   │   ├── category_repository.py
│   │   │   ├── ticket_image_repository.py
│   │   │   ├── ticket_repository.py
│   │   │   └── user_repository.py
│   │   └── interfaces/
│   │       ├── approval_interface.py
│   │       ├── category_interface.py
│   │       ├── ticket_image_interface.py
│   │       ├── ticket_interface.py
│   │       └── user_interface.py
│   │
│   ├── schemas/
│   │   ├── authSchema.py
│   │   ├── error_categorySchema.py
│   │   ├── error_ticketSchema.py
│   │   ├── ticket_approvalSchema.py
│   │   ├── ticket_image.py
│   │   ├── ticket_remarkSchema.py
│   │   ├── ticket_status_historySchema.py
│   │   └── userSchema.py
│   │
│   ├── scripts/
│   │   ├── create_admin.py
│   │   ├── create_manager.py
│   │   ├── file_handler.py
│   │   └── ticket_number.py
│   │
│   ├── services/
│   │   ├── approval_service.py
│   │   ├── auth_service.py
│   │   ├── category_service.py
│   │   ├── email_service.py
│   │   ├── history_service.py
│   │   ├── remark_service.py
│   │   ├── ticket_image_service.py
│   │   ├── ticket_service.py
│   │   └── user_service.py
│   │
│   ├── utils/
│   │   └── logging_config.py
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   │   └── [database migration revision files]
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── routers/
│   │   ├── test_approvals.py
│   │   ├── test_categories.py
│   │   ├── test_history.py
│   │   ├── test_remarks.py
│   │   ├── test_tickets.py
│   │   └── test_users.py
│   │
│   ├── unit_testing/
│   │   ├── test_approval_service.py
│   │   ├── test_category_service.py
│   │   ├── test_history_service.py
│   │   ├── test_remark_service.py
│   │   ├── test_ticket_service.py
│   │   └── test_user_service.py
│   │
│   └── conftest.py
│
├── uploads/              # Runtime storage for uploaded ticket images
├── logs/                 # Runtime application log output
├── .env.example          # Environment-variable template
├── .env                  # Local secrets; do not commit
├── alembic.ini           # Alembic configuration
├── pyproject.toml        # Ruff and pytest configuration
├── requirements.txt      # Python dependencies
└── README.md
```

### Folder and file responsibilities

  -------------------------------------------------------------------------
  Path                                  Responsibility
  ------------------------------------- -----------------------------------
  `app/api/routers/`                    Defines HTTP endpoints, URL paths,
                                        request parameters, response
                                        models, and route-level
                                        dependencies.

  `app/api/routers/base.py`             Collects and registers all feature
                                        routers in one API router.

  `app/api/dependency/`                 Provides reusable dependencies such
                                        as database-backed services, the
                                        current user, and role checks.

  `app/core/`                           Holds application settings and
                                        security utilities such as password
                                        hashing and JWT operations.

  `app/database/`                       Defines the SQLAlchemy declarative
                                        base, asynchronous engine, and
                                        database-session dependency.

  `app/exceptions/`                     Defines application-specific
                                        exceptions and maps them to
                                        consistent HTTP responses.

  `app/middleware/`                     Contains middleware for
                                        cross-cutting HTTP request logging.

  `app/models/`                         Defines SQLAlchemy ORM models,
                                        table columns, relationships,
                                        constraints, and enumerations.

  `app/repositories/interfaces/`        Defines contracts for repository
                                        operations used by service classes.

  `app/repositories/implementations/`   Implements database queries and
                                        persistence operations using
                                        SQLAlchemy.

  `app/schemas/`                        Defines Pydantic request, update,
                                        token, and response schemas.

  `app/scripts/`                        Contains supporting operations for
                                        seed users, ticket-number
                                        generation, and file handling.

  `app/services/`                       Implements business rules and
                                        coordinates repositories, approval
                                        workflows, history, and
                                        notifications.

  `app/utils/`                          Contains shared utilities such as
                                        logging configuration.

  `app/main.py`                         Creates the FastAPI application,
                                        configures lifespan behaviour,
                                        middleware, exception handlers, and
                                        router registration.

  `alembic/versions/`                   Stores revision scripts that
                                        upgrade or downgrade the database
                                        schema.

  `alembic/env.py`                      Connects Alembic to the
                                        application's async database
                                        configuration and model metadata.

  `tests/routers/`                      Contains endpoint-level tests for
                                        API behaviour and HTTP responses.

  `tests/unit_testing/`                 Contains isolated service tests
                                        using mocked dependencies.

  `tests/conftest.py`                   Defines shared fixtures, test
                                        database setup, dependency
                                        overrides, and test authentication
                                        headers.

  `uploads/`                            Stores ticket image files at
                                        runtime; this directory should be
                                        persisted and backed up where
                                        required.

  `logs/`                               Receives the rotating application
                                        log file.

  `pyproject.toml`                      Configures Ruff lint rules,
                                        formatting preferences, and pytest
                                        defaults.
  -------------------------------------------------------------------------

------------------------------------------------------------------------

## 5. Environment Configuration

The application reads configuration from a `.env` file through Pydantic
Settings.

### Step 1: Create the environment file

Copy the provided template:

**Windows PowerShell**

``` powershell
Copy-Item .env.example .env
```

**Linux / macOS**

``` bash
cp .env.example .env
```

### Step 2: Configure the variables

Update the values in `.env`. Do not commit this file or share real
credentials.

  -----------------------------------------------------------------------------------
  Variable                            Required / Optional     Description
  ----------------------------------- ----------------------- -----------------------
  `APP_NAME`                          Required by template    Application name
                                                              displayed in API
                                                              documentation.

  `APP_VERSION`                       Required by template    Application version.

  `API_PREFIX`                        Required by template    Common API route
                                                              prefix; the supplied
                                                              project uses `/api/v1`.

  `DATABASE_NAME`                     Required                Name of the development
                                                              PostgreSQL database.

  `DATABASE_USER`                     Required                PostgreSQL username.

  `DATABASE_PASSWORD`                 Required                PostgreSQL password.

  `DATABASE_HOST`                     Required                Database server host,
                                                              usually `localhost` for
                                                              local development.

  `DATABASE_PORT`                     Required                PostgreSQL port,
                                                              normally `5432`.

  `DATABASE_DRIVER`                   Required by template    Async SQLAlchemy
                                                              driver, normally
                                                              `postgresql+asyncpg`.

  `TEST_DATABASE_NAME`                Required for tests      Dedicated PostgreSQL
                                                              database for automated
                                                              tests.

  `TEST_DATABASE_USER`                Required for tests      Test database username.

  `TEST_DATABASE_PASSWORD`            Required for tests      Test database password.

  `TEST_DATABASE_HOST`                Required for tests      Test database host.

  `TEST_DATABASE_PORT`                Required for tests      Test database port.

  `TEST_DATABASE_DRIVER`              Required for tests      Test driver, normally
                                                              `postgresql+asyncpg`.

  `JWT_SECRET_KEY`                    Required                Random secret of at
                                                              least 32 characters
                                                              used to sign JWTs.

  `JWT_ALGORITHM`                     Required by template    JWT signing algorithm;
                                                              supplied configuration
                                                              uses `HS256`.

  `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`   Required by template    Access-token lifetime
                                                              in minutes.

  `JWT_REFRESH_TOKEN_EXPIRE_DAYS`     Required by template    Refresh-token lifetime
                                                              in days.

  `ADMIN_USERNAME`                    Optional                Username for the
                                                              administrator account
                                                              created at application
                                                              startup.

  `ADMIN_EMAIL`                       Optional                Email address for the
                                                              seed administrator.

  `ADMIN_PASSWORD`                    Optional                Initial password for
                                                              the seed administrator.

  `MANAGER_USERNAME`                  Optional                Username for the
                                                              manager account created
                                                              at application startup.

  `MANAGER_EMAIL`                     Optional                Email address for the
                                                              seed manager.

  `MANAGER_PASSWORD`                  Optional                Initial password for
                                                              the seed manager.

  `MAILJET_API_KEY`                   Optional for startup;   Mailjet API key.
                                      needed for email        

  `MAILJET_API_SECRET`                Optional for startup;   Mailjet API secret.
                                      needed for email        

  `MAILJET_FROM`                      Optional for startup;   Verified default sender
                                      needed for email        email address.

  `MAILJET_APPROVAL_FROM`             Optional for approval   Verified sender address
                                      notifications           used for
                                                              approval-decision
                                                              notifications.

  `MAIL_FROM`                         Optional fallback       Fallback sender email
                                                              address.

  `MAIL_FROM_NAME`                    Optional                Display name used for
                                                              outgoing email.
  -----------------------------------------------------------------------------------

**Important configuration notes**

-   Create the development database and test database in PostgreSQL
    before starting the application or running tests.
-   Keep the test database separate from the development database. The
    test fixture explicitly checks that it is not pointing to the
    application database.
-   Use a unique, randomly generated JWT secret. Never use the example
    placeholder in a real environment.
-   Configure valid seed administrator and manager credentials if you
    want the application startup process to create those accounts. If
    the variables are absent, the seed operation is skipped.
-   Mailjet credentials and verified sender addresses are needed for
    actual email delivery. Without them, email delivery operations
    cannot send messages.
-   The `.env.example` file is a template; `.env` contains local values
    and must remain private.

------------------------------------------------------------------------

## 6. Installation and Running the Application

### Prerequisites

-   Python 3.12 or a compatible Python version.
-   PostgreSQL.
-   Git (if cloning the repository).
-   A terminal or command prompt.

### Step 1: Open the project directory

``` bash
cd "ErrorLog Management"
```

### Step 2: Create a virtual environment

**Windows**

``` powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

``` bat
venv\Scripts\activate
```

**Linux / macOS**

``` bash
python3.12 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Ruff as a development tool because it is configured in
`pyproject.toml` but is not currently listed in `requirements.txt`:

``` bash
pip install ruff
```

### Step 4: Configure PostgreSQL and `.env`

1.  Start the PostgreSQL service.
2.  Create the development database named in `DATABASE_NAME`.
3.  Create a separate test database named in `TEST_DATABASE_NAME`.
4.  Fill in the database credentials and remaining settings in `.env`.

Example database creation commands (run in `psql` using an account with
database-creation privileges):

``` sql
CREATE DATABASE errorlog_db;
CREATE DATABASE errorlog_test_db;
```

If you use these example names, set the corresponding database-name
variables in `.env`.

### Step 5: Apply database migrations

Run the Alembic upgrade command from the project root:

``` bash
alembic upgrade head
```

This applies all migration revisions up to the latest revision and
creates or updates the schema.

### Step 6: Start the FastAPI server

``` bash
uvicorn app.main:app --reload
```

The API will normally be available at:

-   API base path: `http://127.0.0.1:8000/api/v1`
-   Swagger UI: `http://127.0.0.1:8000/docs`
-   ReDoc: `http://127.0.0.1:8000/redoc`
-   Health check: `http://127.0.0.1:8000/api/v1/health`

The application lifespan configures logging and attempts to create the
configured administrator and manager seed accounts if they do not
already exist.

------------------------------------------------------------------------

## 7. API Modules

The API routes are grouped by feature and registered under the
configured `API_PREFIX`.

  --------------------------------------------------------------------------------
  Module                  Main endpoint paths              Purpose
  ----------------------- -------------------------------- -----------------------
  Health                  `GET /health`                    Checks
                                                           application/database
                                                           availability.

  Authentication          `/auth/login`, `/auth/refresh`,  Login, refresh tokens,
                          `/auth/me`                       and retrieve the
                                                           authenticated user's
                                                           profile.

  Users                   `/users`                         Create, list, retrieve,
                                                           update, and deactivate
                                                           users.

  Categories              `/categories`                    Create, list, retrieve,
                                                           update, and deactivate
                                                           ticket categories.

  Tickets                 `/tickets`                       Create and retrieve
                                                           tickets, list
                                                           personal/all/overdue
                                                           tickets, update status,
                                                           and close tickets.

  Remarks                 `/tickets/{ticket_id}/remarks`   Add and retrieve ticket
                                                           remarks.

  History                 `/tickets/{ticket_id}/history`   Retrieve the status
                                                           history of a ticket.

  Approvals               `/approvals`                     List pending approvals,
                                                           retrieve an approval,
                                                           and approve or reject
                                                           it.

  Ticket images           `/tickets/{ticket_id}/images`    Upload and delete
                                                           ticket image
                                                           attachments.
  --------------------------------------------------------------------------------

All paths above are relative to the configured API prefix. For example,
with `API_PREFIX=/api/v1`, the login endpoint is
`POST /api/v1/auth/login`.

For the complete request and response definitions, open Swagger UI at
`/docs` while the application is running.

------------------------------------------------------------------------

## 8. Running Automated Tests with pytest

The project includes two test groups:

-   **Unit tests:** Test service-layer business logic independently by
    mocking repository or other asynchronous dependencies.
-   **Router tests:** Test API endpoint behaviour using FastAPI's
    `TestClient` and a dedicated PostgreSQL test database.

### Step 1: Verify the test database configuration

Ensure that the following variables are configured in `.env`:

``` env
TEST_DATABASE_NAME=errorlog_test_db
TEST_DATABASE_USER=your_test_database_username
TEST_DATABASE_PASSWORD=your_test_database_password
TEST_DATABASE_HOST=localhost
TEST_DATABASE_PORT=5432
TEST_DATABASE_DRIVER=postgresql+asyncpg
```

Create the test database in PostgreSQL before running tests.

**Warning:** The test fixtures create and drop tables and truncate test
data. Never configure the test database variables to point to a
production or development database.

### Step 2: Run the complete test suite

From the project root:

``` bash
pytest
```

### Run only unit tests

``` bash
pytest tests/unit_testing/ -v
```

### Run only router/API tests

``` bash
pytest tests/routers/ -v
```

### Run one test file

``` bash
pytest tests/unit_testing/test_ticket_service.py -v
```

Or:

``` bash
pytest tests/routers/test_tickets.py -v
```

### Run a specific test function

``` bash
pytest tests/unit_testing/test_ticket_service.py::test_function_name -v
```

Replace `test_function_name` with the actual test function name in the
file.

### Useful pytest options

``` bash
pytest -v
```

Displays each test name and its result.

``` bash
pytest -q
```

Displays a shorter test summary.

``` bash
pytest -vv
```

Displays more detailed test information.

``` bash
pytest -x
```

Stops after the first failure.

``` bash
pytest --tb=short
```

Displays shorter tracebacks.

### Test fixture behaviour

The shared `tests/conftest.py` file:

1.  Builds a separate async SQLAlchemy engine using the test database
    settings.
2.  Verifies that the test database is not the configured application
    database.
3.  Creates the schema before the test session.
4.  Clears test data between tests and inserts test users for the
    supported roles.
5.  Overrides the application's database dependency so API tests use the
    test database.
6.  Mocks the email service so tests do not send real emails.
7.  Provides authenticated headers for administrator, manager, and
    employee test users.
8.  Drops the test schema and disposes of the test engine after the test
    session.

------------------------------------------------------------------------

## 9. Database Migrations with Alembic

Alembic is used to manage database schema changes over time. Migration
scripts are stored in `alembic/versions/`, and each revision describes
how to upgrade or downgrade the schema.

The project uses an asynchronous SQLAlchemy database URL in its Alembic
environment configuration.

Run all commands from the project root, where `alembic.ini` is located.

### Apply all migrations

``` bash
alembic upgrade head
```

Applies all available revisions up to the latest revision.

### Check the current database revision

``` bash
alembic current
```

Displays the revision currently applied to the configured database.

### View migration history

``` bash
alembic history
```

Displays the available migration revision history.

### Generate a new migration automatically

After changing SQLAlchemy models:

``` bash
alembic revision --autogenerate -m "describe_schema_change"
```

For example:

``` bash
alembic revision --autogenerate -m "add_ticket_reference_column"
```

Review the generated file in `alembic/versions/` before applying it.
Autogeneration is a starting point; it does not guarantee that every
database change has been detected or that the generated migration is
correct.

### Apply the new migration

``` bash
alembic upgrade head
```

### Downgrade one revision

``` bash
alembic downgrade -1
```

Reverts the most recently applied migration.

### Downgrade to a specific revision

``` bash
alembic downgrade <revision_id>
```

Replace `<revision_id>` with the target revision identifier.

### Display the latest revision

``` bash
alembic heads
```

### Important migration practices

-   Update the SQLAlchemy model first, then generate the migration.
-   Review both `upgrade()` and `downgrade()` functions before applying
    a revision.
-   Check constraints, indexes, foreign keys, defaults, and nullable
    settings carefully.
-   Apply migrations to the intended database only.
-   Do not edit an already-shared/applied migration casually; create a
    new revision for subsequent schema changes.
-   Back up important data before running destructive migrations.
-   Use `alembic upgrade head` when setting up a fresh development
    database.

------------------------------------------------------------------------

## 10. Code Quality and Formatting with Ruff

Ruff is configured in `pyproject.toml`.

Current configuration:

-   Maximum line length: 88 characters.
-   Target Python version: Python 3.12.
-   Enabled lint rule groups: `E`, `F`, `I`, `UP`, and `B`.
-   Formatter uses double quotes and four-space indentation.

### Check the complete project

``` bash
ruff check .
```

### Automatically fix supported lint issues

``` bash
ruff check . --fix
```

Review the changes after running automatic fixes.

### Check formatting without changing files

``` bash
ruff format --check .
```

### Format the project

``` bash
ruff format .
```

### Check a specific folder

``` bash
ruff check app/
```

### Check a specific file

``` bash
ruff check app/services/ticket_service.py
```

### Recommended quality-check sequence

Run these commands from the project root before submitting the project:

``` bash
ruff check .
ruff format --check .
pytest
```

If Ruff reports fixable lint issues, run `ruff check . --fix`, review
the result, and then run the checks again.

------------------------------------------------------------------------

## 11. File Upload Behaviour

Ticket images are uploaded through the ticket image API. The
file-handling utility:

-   Accepts JPEG and PNG image formats.
-   Checks the supplied filename and content type.
-   Enforces a maximum image size of 10 MB.
-   Reads and writes the uploaded file in chunks.
-   Generates a unique filename for storage.
-   Saves files under the `uploads/` directory.
-   Removes a partially written file if validation or storage fails.

The database stores attachment metadata, while the image file itself is
stored in the upload directory. Therefore, deployments must persist the
`uploads/` directory and include it in the application's backup
strategy. Do not assume that a local folder is durable when deploying to
an ephemeral hosting platform.

------------------------------------------------------------------------

## 12. Logging and Error Handling

### Logging

Application logging is configured through `app/utils/logging_config.py`.
Logs are written to:

``` text
logs/app.log
```

A rotating file handler limits an individual log file to 5 MB and
retains up to five backup files. HTTP request logging is handled by
middleware.

### Error handling

Custom application exceptions are defined in
`app/exceptions/custom_exceptions.py`. Their HTTP response mappings are
maintained in the exception handler modules and registered during
application creation.

This keeps error responses consistent and avoids duplicating
exception-to-response logic in every route.

------------------------------------------------------------------------

## 13. Development Workflow

A recommended workflow when adding a feature:

1.  Define or update the SQLAlchemy model if the database structure
    changes.
2.  Define the Pydantic request and response schemas.
3.  Update the repository interface with the required data-access
    contract.
4.  Implement the database operation in the repository implementation.
5.  Implement validation and business rules in the service layer.
6.  Add the API endpoint in the appropriate router and inject its
    dependencies.
7.  Register new routers or dependencies if required.
8.  Generate and review an Alembic migration when the schema changes.
9.  Add unit tests for service behaviour.
10. Add router tests for endpoint behaviour and access control.
11. Run Ruff linting, formatting checks, and the complete pytest suite.

------------------------------------------------------------------------

## 14. Security and Configuration Practices

-   Never commit `.env`, database passwords, JWT secrets, or Mailjet
    credentials.
-   Use a strong, unique JWT signing secret outside local development.
-   Store password hashes, not plain-text passwords.
-   Use role checks for restricted operations.
-   Keep test and non-test databases separate.
-   Validate uploaded file type, filename, and size.
-   Restrict access to uploaded files and protect the upload directory
    in deployment.
-   Use HTTPS when deploying the API outside local development.
-   Use least-privilege PostgreSQL credentials for application and test
    environments.
-   Review migration scripts before applying them to important
    databases.

------------------------------------------------------------------------

## 15. Conclusion

ErrorLog Management is a modular, asynchronous REST API designed to
manage the complete lifecycle of error and support tickets. It combines
authentication, role-based permissions, category-based ticket handling,
approval workflows, remarks, status auditing, image attachments, email
notifications, database migrations, and automated testing.

The project demonstrates practical backend engineering concepts
including FastAPI dependency injection, asynchronous SQLAlchemy,
repository and service layers, interface-based design, Pydantic
validation, JWT authentication, PostgreSQL schema management,
pytest-based testing, and Ruff code-quality checks.

The separation of responsibilities across modules makes the application
easier to understand, test, maintain, and extend.
