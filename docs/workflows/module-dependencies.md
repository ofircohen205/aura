# Module Dependencies

This document outlines the dependency relationships between modules in the Aura backend.

## Dependency Graph

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

## Layer Dependencies

### API Layer Dependencies

- **Depends on**: Service Layer, Core Layer (exceptions, config)
- **Provides**: HTTP endpoints, request/response validation
- **Modules**:
  - `api/v1/auth/` → `services/auth/`, `api/dependencies/`
  - `api/middlewares/` → `core/config/`
  - `api/dependencies/` → `core/security/`, `dao/user/`, `services/auth/`

### Service Layer Dependencies

- **Depends on**: DAO Layer, Core Layer, External Services (Redis)
- **Provides**: Business logic, orchestration
- **Modules**:
  - `services/auth/` → `dao/user/`, `core/security/`, `services/redis/`
  - `services/redis/` → External Redis service

### DAO Layer Dependencies

- **Depends on**: Database Layer
- **Provides**: Data access abstraction
- **Modules**:
  - `dao/user/` → `db/models/user/`, `db/database/`

### Core Layer Dependencies

- **Depends on**: External libraries only
- **Provides**: Foundation utilities
- **Modules**:
  - `core/security/` → External (bcrypt, python-jose)
  - `core/config/` → External (pydantic-settings)
  - `core/exceptions/` → External (fastapi)

### Database Layer Dependencies

- **Depends on**: External libraries (SQLModel, SQLAlchemy)
- **Provides**: Data models, connection management
- **Modules**:
  - `db/models/` → External (SQLModel)
  - `db/database/` → External (SQLAlchemy, SQLModel)

## Authentication Module Dependencies

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

## Circular Dependency Prevention

- **API Layer** never directly imports from **Database Layer**
- **Service Layer** never directly imports from **API Layer**
- **Core Layer** has no dependencies on other application layers
- All cross-layer communication goes through defined interfaces

## Import Guidelines

1. **Always import from the layer directly below** (when possible)
2. **Use dependency injection** for cross-layer dependencies
3. **Avoid circular imports** by using TYPE_CHECKING for type hints
4. **Keep Core Layer independent** - no application-specific imports

## Example: Adding a New Feature

When adding a new feature (e.g., "notifications"):

1. **Database Layer**: Create `db/models/notification.py`
2. **DAO Layer**: Create `dao/notification.py` (depends on model)
3. **Service Layer**: Create `services/notification/service.py` (depends on DAO)
4. **API Layer**: Create `api/v1/notifications/` (depends on service)

This maintains the layered architecture and prevents circular dependencies.
