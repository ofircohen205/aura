# System Architecture

This document describes the architecture of the Aura system, including backend, frontend, CLI, and VSCode extension components, as well as module dependencies.

## Table of Contents

1. [Backend Architecture](#backend-architecture)
2. [Frontend Architecture](#frontend-architecture)
3. [CLI Architecture](#cli-architecture)
4. [VSCode Extension Architecture](#vscode-extension-architecture)
5. [Module Dependencies](#module-dependencies)
6. [Adding New Features](#adding-new-features)

## Backend Architecture

### Layer Structure

1. **Core Layer** (`src/core/`)
   - Configuration management (config.py): Uses Pydantic Settings to fetch values from .env.local/staging/production and creates a global configuration object
   - Exception handling (exceptions.py): Base exception classes and HTTP exception mapping utilities
   - Logging infrastructure (logging.py): Structured logging with loguru, request/response middleware, and correlation IDs
   - Security utilities (security.py): JWT token creation/verification, password hashing (bcrypt), refresh token generation
   - Metrics (metrics.py): Prometheus metrics for monitoring (optional, fails gracefully if prometheus_client not installed)

2. **Database Layer** (`src/db/`)
   - SQLModel/ORM models (each DB table will have its own python file under `models` directory)
   - Database connection management (database.py)
   - Session handling for dependency injection in API (database.py -> SessionDep)

3. **DAO Layer** (`src/dao/`)
   - The only place that talks with the DB.
   - Database operations abstraction (BaseDAO in base.py)
   - Each DB table has its own class (inherits BaseDAO), must implement base queries, can add specific queries.
   - Current DAO modules:
     ```text
     ├── dao/
     │   ├── __init__.py
     │   ├── base.py (BaseDAO with CRUD operations)
     │   ├── user.py (UserDAO)
     ```

4. **Service Layer** (`src/services/`)
   - Business logic extraction from API endpoints
   - Integration with external services (for example OpenAI client, LangGraph workflows)
   - Orchestration of multiple operations
   - Service-specific exception handling
   - Current service modules:
     ```text
     ├── services/
     │   ├── auth/
     │   │   ├── __init__.py
     │   │   ├── cache.py (Redis caching for auth)
     │   │   ├── exceptions.py
     │   │   ├── service.py
     │   ├── redis/
     │   │   ├── __init__.py
     │   │   ├── client.py
     │   ├── workflows/
     │   │   ├── __init__.py
     │   │   ├── exceptions.py
     │   │   ├── service.py
     │   ├── events/
     │   │   ├── __init__.py
     │   │   ├── exceptions.py
     │   │   ├── service.py
     │   ├── audit/
     │   │   ├── __init__.py
     │   │   ├── exceptions.py
     │   │   ├── service.py
     ```

5. **API Layer** (`src/api/`)
   - FastAPI sub-applications (with versioning)
   - Request/response validation (Pydantic schemas)
   - Exception handlers for each sub-application
   - Service layer integration
   - Current API structure:
     ```text
     ├── v1/
     │   ├── auth/
     │   │   ├── __init__.py
     │   │   ├── endpoints.py
     │   │   ├── exceptions.py
     │   │   ├── schemas.py
     │   ├── workflows/
     │   │   ├── __init__.py
     │   │   ├── endpoints.py
     │   │   ├── exceptions.py
     │   │   ├── schemas.py
     │   ├── events/
     │   │   ├── __init__.py
     │   │   ├── endpoints.py
     │   │   ├── exceptions.py
     │   │   ├── schemas.py
     │   ├── audit/
     │   │   ├── __init__.py
     │   │   ├── endpoints.py
     │   │   ├── exceptions.py
     │   │   ├── schemas.py
     │   ├── common/
     │   │   ├── __init__.py
     │   │   ├── schemas.py (PaginationParams, PaginatedResponse)
     ```
   - Middleware (`src/api/middlewares/`):
     - Security headers middleware
     - CSRF protection middleware
     - Rate limiting middleware
   - Dependencies (`src/api/dependencies.py`):
     - Authentication dependencies
     - Authorization dependencies

6. **Jobs Layer** (`src/jobs/`)
   - For example: Data Pipeline (ETL) job, Clean-up data job, etc.
   - README.md for explaining the logic of the job.
   - **Note**: Currently not implemented, reserved for future background job processing.

## Frontend Architecture

The web dashboard is built with Next.js 16 using the App Router pattern, providing server-side rendering, routing, and layout capabilities.

### Directory Structure

1. **App Directory** (`app/`): Next.js App Router structure
   - `app/`: Root layout and page
   - `app/auth/`: Authentication pages (login, register) with shared layout
   - `app/dashboard/`: Protected dashboard pages with shared layout
     - `workflows/`: Workflow listing and detail pages
     - `audits/`: Audit listing and detail pages
     - `profile/`: User profile page
     - `settings/`: Settings page
   - `app/layout.tsx`: Root layout with providers
   - `app/globals.css`: Global styles

2. **Components** (`components/`): Reusable UI components
   - `auth/`: Authentication-related components (LoginForm, RegisterForm, ProtectedRoute)
   - `dashboard/`: Dashboard-specific components (Sidebar, Header, Breadcrumbs, UserMenu, WorkflowCard)
   - `ui/`: Base UI components (Button, Card, Input, Badge, Toast, etc.) - shadcn/ui style components
   - `ErrorBoundary.tsx`: Error boundary component
   - `ToastProvider.tsx`: Toast notification provider

3. **Library** (`lib/`): Shared utilities and business logic
   - `api/`: API client modules
     - `client.ts`: Axios instance with interceptors and error handling
     - `auth.ts`: Authentication API calls
     - `workflows.ts`: Workflow API calls
     - `audits.ts`: Audit API calls
     - `endpoints.ts`: Centralized endpoint definitions
   - `hooks/`: Custom React hooks
     - `useAuth.ts`: Authentication state management
     - `useFormSubmission.ts`: Form submission handling
     - `useToast.ts`: Toast notification hook
   - `routes.ts`: Centralized route definitions
   - `utils/`: Utility functions
     - `cn.ts`: Class name utility (clsx + tailwind-merge)
     - `env.ts`: Environment variable utilities
     - `error-handler.ts`: Error handling utilities
     - `logger.ts`: Logging utilities
     - `navigation.ts`: Navigation utilities
     - `user.ts`: User-related utilities

4. **Types** (`types/`): TypeScript type definitions
   - `api.ts`: API response types

5. **Middleware** (`middleware.ts`): Next.js middleware for route protection and authentication

### State Management

- **Zustand**: Global client state management for authentication and UI state
- **React Context**: Used for providers (ToastProvider, ErrorBoundary)
- **Local State**: React hooks (useState, useMemo) for component-level state

### Technology Stack

- **Framework**: Next.js 16.1.3 with App Router
- **React**: 19.2.3
- **TypeScript**: 5.9.3
- **Styling**: Tailwind CSS 3.3.0
- **UI Components**: Custom components built with Tailwind (shadcn/ui style)
- **Forms**: React Hook Form 7.48.0 + Zod 3.22.0 validation
- **HTTP Client**: Axios 1.6.0
- **State Management**: Zustand 4.4.0
- **Testing**: Vitest (unit/integration), Playwright (E2E)

## CLI Architecture

### Structure (`clients/cli/`)

1. **Entry Point** (`src/main.py`):
   - Typer application definition
   - Command registration
   - Global error handling

2. **Commands** (`src/commands/`):
   - Focused modules for each command group (e.g., `audit.py`, `config.py`)
   - Argument parsing and validation
   - Calls into the `Services` layer (or shared libs)

3. **Services** (`src/services/`):
   - Business logic specific to the CLI (e.g., `GitService` for hook management)
   - Interfaces with shared core libraries (`libs/agentic-py`)

4. **Config** (`src/config/`):
   - YAML configuration loader (`~/.aura/config.yaml`)
   - Credential management

## VSCode Extension Architecture

### Structure (`clients/vscode/`)

1. **Extension Entry** (`src/extension.ts`):
   - `activate()` and `deactivate()` methods
   - Command registration
   - Context subscriptions

2. **Services** (`src/services/`):
   - `StruggleService`: Analyzes edit patterns
   - `LspService`: Communicates with the Language Server (or backend)

3. **Panels** (`src/panels/`):
   - React/HTML/Sidebar implementations for WebViews (e.g., `LessonPanel`)

4. **State** (`src/state/`):
   - Extension-global state (authenticated user, current session)

## Module Dependencies

### Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  (api/v1/auth/, api/middlewares/, api/dependencies/)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                          │
│  (services/auth/, services/redis/)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│     DAO Layer    │   │   Core Layer     │
│  (dao/user.py)   │   │ (core/security,  │
│                  │   │  core/config)    │
└────────┬─────────┘   └──────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  (db/models/, db/database.py)                               │
└─────────────────────────────────────────────────────────────┘
```

### Layer Dependencies

#### API Layer Dependencies

- **Depends on**: Service Layer, Core Layer (exceptions, config)
- **Provides**: HTTP endpoints, request/response validation
- **Modules**:
  - `api/v1/auth/` → `services/auth/`, `api/dependencies/`
  - `api/middlewares/` → `core/config/`
  - `api/dependencies/` → `core/security/`, `dao/user/`, `services/auth/`

#### Service Layer Dependencies

- **Depends on**: DAO Layer, Core Layer, External Services (Redis)
- **Provides**: Business logic, orchestration
- **Modules**:
  - `services/auth/` → `dao/user/`, `core/security/`, `services/redis/`
  - `services/redis/` → External Redis service

#### DAO Layer Dependencies

- **Depends on**: Database Layer
- **Provides**: Data access abstraction
- **Modules**:
  - `dao/user/` → `db/models/user/`, `db/database/`

#### Core Layer Dependencies

- **Depends on**: External libraries only
- **Provides**: Foundation utilities
- **Modules**:
  - `core/security/` → External (bcrypt, python-jose)
  - `core/config/` → External (pydantic-settings)
  - `core/exceptions/` → External (fastapi)

#### Database Layer Dependencies

- **Depends on**: External libraries (SQLModel, SQLAlchemy)
- **Provides**: Data models, connection management
- **Modules**:
  - `db/models/` → External (SQLModel)
  - `db/database/` → External (SQLAlchemy, SQLModel)

### Authentication Module Dependencies

```
api/v1/auth/endpoints.py
  ├── services/auth/service.py
  │   ├── dao/user/user_dao.py
  │   │   └── db/models/user.py
  │   ├── core/security.py
  │   └── services/redis/client.py
  ├── api/dependencies.py
  │   ├── core/security.py
  │   ├── dao/user/user_dao.py
  │   └── services/auth/service.py
  └── api/v1/auth/schemas.py
      └── db/models/user.py
```

### Circular Dependency Prevention

- **API Layer** never directly imports from **Database Layer**
- **Service Layer** never directly imports from **API Layer**
- **Core Layer** has no dependencies on other application layers
- All cross-layer communication goes through defined interfaces

### Import Guidelines

1. **Always import from the layer directly below** (when possible)
2. **Use dependency injection** for cross-layer dependencies
3. **Avoid circular imports** by using TYPE_CHECKING for type hints
4. **Keep Core Layer independent** - no application-specific imports

## Adding New Features

### Backend: Adding a New Feature

When adding a new feature (e.g., "notifications"):

1. **Database Layer**: Create `db/models/notification.py`
2. **DAO Layer**: Create `dao/notification.py` (depends on model)
3. **Service Layer**: Create `services/notification/service.py` (depends on DAO)
4. **API Layer**: Create `api/v1/notifications/` (depends on service)

This maintains the layered architecture and prevents circular dependencies.

### Frontend: Adding a New Feature

When adding a new feature to the web dashboard (e.g., "notifications"):

1. **Create Page**: Add a new route in `app/dashboard/notifications/page.tsx` (or appropriate location)
2. **Create Components**: Add feature-specific components in `components/dashboard/notifications/`
3. **Create API Client**: Add API functions in `lib/api/notifications.ts` if needed
4. **Add Route**: Update `lib/routes.ts` with new route definitions
5. **Add Navigation**: Update navigation items in `lib/routes.ts` if it should appear in sidebar
6. **Add Types**: Add TypeScript types in `types/api.ts` if needed

For detailed examples of creating new features, see [Common Development Tasks](DEVELOPMENT.md#creating-a-new-feature) in the Development Guide.

## Related Documentation

- [Development Guide](DEVELOPMENT.md) - Development workflow and common tasks
- [Requirements](REQUIREMENTS.md) - Product and technical requirements
