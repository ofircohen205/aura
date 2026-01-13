# Common Development Tasks

## Creating a New Feature

### Backend: Adding a New API Endpoint

The backend follows a layered architecture. You must add files in the specific order of dependencies: **Model -> DAO -> Service -> API**.

1. **Define Database Model** (`src/db/models/example.py`)

   *Create the SQLAlchemy/SQLModel definition.*

```python
# src/db/models/example.py

from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from datetime import datetime

class Example(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

2. **Create DAO** (`src/dao/example.py`)

   *Inherit from `BaseDAO` to get standard CRUD operations automatically.*

```python
# src/dao/example.py

from src.dao.base import BaseDAO
from src.db.models.example import Example

class ExampleDAO(BaseDAO[Example, ExampleCreate, ExampleUpdate]):
    # Add specific queries here if needed, otherwise pass
    pass

example_dao = ExampleDAO(Example)
```

3. **Create Service & Business Exceptions** (`src/services/example/`)

   *Define pure Python exceptions for business logic, then implement the service.*

   **A. Define Exceptions** (`src/services/example/exceptions.py`)

```python
# src/services/example/exceptions.py

class ExampleAlreadyExistsError(Exception):
    def __init__(self, name: str):
        self.message = f"Example with name '{name}' already exists."
        super().__init__(self.message)

class ExampleNotFoundError(Exception):
    pass

class ExampleValidationError(Exception):
    def __init__(self, message: str, operation: str = ""):
        self.message = message
        self.operation = operation
        super().__init__(self.message)

class ExampleServiceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
```

**B. Implement Service** (`src/services/example/service.py`)

```python
# src/services/example/service.py

from src.dao.example import example_dao
from src.services.example.exceptions import ExampleAlreadyExistsError, ExampleNotFoundError

class ExampleService:
    async def create_example(self, session, data: dict):
        # Business Logic: Check for duplicates before creation
        existing = await example_dao.get_by_name(session, data.name)
        if existing:
            raise ExampleAlreadyExistsError(data.name)
            
        return await example_dao.create(session, data)
    
    async def get_example(self, session, example_id: str):
        example = await example_dao.get_by_id(session, example_id)
        if not example:
            raise ExampleNotFoundError(f"Example with id '{example_id}' not found")
        return example

service = ExampleService()
```

4. **Create API Layer** (`src/api/v1/example/`)

   *Create a folder `src/api/v1/example/` containing schemas, HTTP exceptions, and endpoints. Each API module uses a FastAPI sub-application pattern.*

   **A. Schemas** (`src/api/v1/example/schemas.py`)

   *Define Pydantic models for request/response validation.*

```python
# src/api/v1/example/schemas.py

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class ExampleBase(BaseModel):
    """Shared example fields."""
    name: str
    description: str

class ExampleCreate(ExampleBase):
    """Example creation schema."""
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Example Name",
                    "description": "Example description"
                }
            ]
        }
    )

class ExampleUpdate(BaseModel):
    """Example update schema."""
    name: str | None = None
    description: str | None = None

class ExampleResponse(ExampleBase):
    """Example response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_example(cls, example: "Example") -> "ExampleResponse":
        """Create ExampleResponse from Example model."""
        return cls(
            id=example.id,
            name=example.name,
            description=example.description,
            created_at=example.created_at,
            updated_at=example.updated_at,
        )
```

**B. Exception Handlers** (`src/api/v1/example/exceptions.py`)

*Define a function to register exception handlers for the sub-application. This converts service exceptions to HTTP responses.*

```python
# src/api/v1/example/exceptions.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from src.services.example.exceptions import (
    ExampleAlreadyExistsError,
    ExampleNotFoundError,
    ExampleValidationError,
    ExampleServiceError,
)

def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the example service."""

    @app.exception_handler(ExampleNotFoundError)
    async def example_not_found_handler(request: Request, exc: ExampleNotFoundError):
        """Handle ExampleNotFoundError exceptions."""
        logger.warning(f"Example not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ExampleAlreadyExistsError)
    async def example_already_exists_handler(
        request: Request, exc: ExampleAlreadyExistsError
    ):
        """Handle ExampleAlreadyExistsError exceptions."""
        logger.warning(f"Example already exists: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ExampleValidationError)
    async def example_validation_handler(request: Request, exc: ExampleValidationError):
        """Handle ExampleValidationError exceptions."""
        logger.warning(f"Example validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ExampleServiceError)
    async def example_service_error_handler(
        request: Request, exc: ExampleServiceError
    ):
        """Handle ExampleServiceError exceptions."""
        logger.error(f"Example service error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )
```

**C. Endpoints** (`src/api/v1/example/endpoints.py`)

*Create the router and sub-application factory function. Each API module is a separate FastAPI sub-application.*

```python
# src/api/v1/example/endpoints.py

from fastapi import APIRouter, FastAPI

from src.api.v1.example.exceptions import register_exception_handlers
from src.api.v1.example.schemas import ExampleCreate, ExampleResponse, ExampleUpdate
from src.db.database import SessionDep
from src.services.example.service import service
from src.services.example.exceptions import ExampleValidationError

router = APIRouter(tags=["examples"])


def create_example_app() -> FastAPI:
    """Create and configure the example service FastAPI sub-application."""
    example_app = FastAPI(title="Example Service")
    register_exception_handlers(example_app)
    example_app.include_router(router)
    return example_app


@router.post(
    "/",
    summary="Create example",
    description="Create a new example item",
    response_model=ExampleResponse,
    responses={
        200: {"description": "Example created successfully"},
        400: {"description": "Validation error"},
        409: {"description": "Example already exists"},
        500: {"description": "Internal server error"},
    },
)
async def create_example(
    data: ExampleCreate,
    session: SessionDep
) -> ExampleResponse:
    """
    Create a new example item.
    
    Note: No try/except block needed here. The exception handlers
    registered in register_exception_handlers() will catch service
    exceptions and convert them to appropriate HTTP responses.
    """
    return await service.create_example(session, data)


@router.get(
    "/",
    summary="List examples",
    description="Get all examples",
    response_model=list[ExampleResponse],
)
async def list_examples(
    session: SessionDep
) -> list[ExampleResponse]:
    """Get all examples."""
    return await service.list_examples(session)


@router.get(
    "/{example_id}/",
    summary="Get example",
    description="Get example by ID",
    response_model=ExampleResponse,
)
async def get_example(
    example_id: str,
    session: SessionDep
) -> ExampleResponse:
    """Get example by ID."""
    return await service.get_example(session, example_id)


@router.put(
    "/{example_id}/",
    summary="Update example",
    description="Update example by ID",
    response_model=ExampleResponse,
)
async def update_example(
    example_id: str,
    data: ExampleUpdate,
    session: SessionDep
) -> ExampleResponse:
    """Update example by ID."""
    return await service.update_example(session, example_id, data)
```

5. **Register Sub-Application** (`src/main.py`)

   *Mount the sub-application in the main FastAPI app. Each module is mounted as a separate sub-application at a specific path.*

```python
# src/main.py

from fastapi import FastAPI
from src.api.v1.example.endpoints import create_example_app

app = FastAPI()

# Create the sub-application
example_app = create_example_app()

# Mount the sub-application
# The path prefix determines the URL: /api/v1/examples/*
app.mount("/api/v1/examples", example_app)
```

**Key Points:**
- Each API module is a **separate FastAPI sub-application**, not just a router
- Exception handlers are registered per sub-application via `register_exception_handlers()`
- Sub-applications are **mounted** (not included) in the main app using `app.mount()`
- The mount path determines the URL prefix for all endpoints in that module
- Service exceptions are automatically converted to HTTP responses by the registered handlers

### Frontend: Adding a New Feature

The frontend uses a **Screaming Architecture**. All logic related to a feature stays within `src/features/`.

1. **Create Feature Structure**

   Create the directory: `src/features/example/` with subfolders: `components`, `hooks`, `pages`, `services`, `types`.

2. **Create Types** (`src/features/example/types/index.ts`)

```typescript
// src/features/example/types/index.ts

export interface ExampleItem {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}
```

3. **Create Service** (`src/features/example/services/api.ts`)

```typescript
// src/features/example/services/api.ts

import { apiClient } from "@/core/api/client";
import { ExampleItem } from "../types";

export const createExample = async (data: Omit<ExampleItem, 'id' | 'created_at' | 'updated_at'>) => {
  const response = await apiClient.post<ExampleItem>("/examples/", data);
  return response.data;
};

export const getExamples = async (): Promise<ExampleItem[]> => {
  const response = await apiClient.get<ExampleItem[]>("/examples/");
  return response.data;
};

export const getExample = async (id: string): Promise<ExampleItem> => {
  const response = await apiClient.get<ExampleItem>(`/examples/${id}/`);
  return response.data;
};

export const updateExample = async (id: string, data: Partial<ExampleItem>): Promise<ExampleItem> => {
  const response = await apiClient.put<ExampleItem>(`/examples/${id}/`, data);
  return response.data;
};
```

4. **Create Component** (`src/features/example/components/ExampleCard.tsx`)

```typescript
// src/features/example/components/ExampleCard.tsx

import { Button } from "@/shared/components/ui/button";
import { ExampleItem } from "../types";

interface Props {
  item: ExampleItem;
}

export const ExampleCard = ({ item }: Props) => {
  return (
    <div className="border p-4 rounded">
      <h3>{item.name}</h3>
      <p>{item.description}</p>
      <Button variant="outline">View Details</Button>
    </div>
  );
};
```

5. **Create Page** (`src/features/example/pages/ExamplePage.tsx`)

```typescript
// src/features/example/pages/ExamplePage.tsx

import { useQuery } from "@tanstack/react-query";
import { ExampleCard } from "../components/ExampleCard";
import { getExamples } from "../services/api";

export const ExamplePage = () => {
  const { data: examples, isLoading } = useQuery({
    queryKey: ["examples"],
    queryFn: getExamples,
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1>Example Feature</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {examples?.map((example) => (
          <ExampleCard key={example.id} item={example} />
        ))}
      </div>
    </div>
  );
};
```

6. **Export Feature** (`src/features/example/index.ts`)

   *Act as the "Public API" for this feature.*

```typescript
// src/features/example/index.ts

// Only export what is needed by the router or other modules
export { ExamplePage } from "./pages/ExamplePage";
```

7. **Add Route** (`src/core/routing/router.tsx`)

```typescript
// src/core/routing/router.tsx

import { ExamplePage } from "@/features/example";

// Inside your route definition array
{
  path: "example",
  element: <ExamplePage />,
}
```

### CLI: Adding a New Command

1. **Create Command Module** (`clients/cli/src/commands/example.py`)

```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def hello(name: str):
    """
    Say hello to the user.
    """
    console.print(f"Hello, [bold blue]{name}[/bold blue]!")
```

2. **Register in Main** (`clients/cli/src/main.py`)

```python
from clients.cli.src.commands import example

app.add_typer(example.app, name="example")
```

### VSCode: Adding a New Command

1. **Define in package.json**

```json
"contributes": {
  "commands": [
    {
      "command": "aura.example",
      "title": "Aura: Example Command"
    }
  ]
}
```

2. **Implement Logic** (`clients/vscode/src/commands/example.ts`)

```typescript
import * as vscode from 'vscode';

export const exampleCommand = () => {
  vscode.window.showInformationMessage('Hello from Aura!');
};
```

3. **Register in Extension** (`clients/vscode/src/extension.ts`)

```typescript
import { exampleCommand } from './commands/example';

export function activate(context: vscode.ExtensionContext) {
  let disposable = vscode.commands.registerCommand('aura.example', exampleCommand);
  context.subscriptions.push(disposable);
}
```

## Database Migrations

Use the migration scripts located in the deployment folder to manage schema changes.

```bash
# Location: deployment/migration

# Naming Convention: V{version}__{description}.sql

# 1. Create a new SQL file
touch deployment/migration/V21__add_example_table.sql

# 2. Add SQL content
# CREATE TABLE example (
#     id UUID PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     description TEXT,
#     created_at TIMESTAMP DEFAULT NOW()
# );

# 3. Apply migrations (via Makefile shortcut)
make run-db-migrations
```

## Running Tests

### Backend Testing

The backend has distinct folders for unit and integration tests.

```bash
# Run all tests
cd backend && uv run pytest

# Run specific test file
uv run pytest tests/unit/services/test_example_service.py -v

uv run pytest tests/integration/api/test_example_endpoints.py -v
```

### Frontend Testing

Frontend tests are located alongside components or in `__tests__` directories using Vitest/Jest.

```bash
# Run all tests
cd frontend && npm test

# Run specific test file
npm test ExampleCard.test.tsx
```

## Debugging Tips

### Backend Debugging (FastAPI)

```bash
# 1. Run with Debugger
# Ensure your IDE (VS Code/PyCharm) is attached to port 5678
uv run python -m debugpy --listen 0.0.0.0:5678 src/main.py

# 2. Check Application Logs
tail -f backend/logs/app.log

# 3. Direct Database Access
# Access the Postgres container defined in docker-compose.dev.yml
docker exec -it [project_name]-postgres psql -U [user] -d [database]
```

### Frontend Debugging (React 19)

1. **React DevTools**: Use the "Components" tab to inspect the component tree and the "Profiler" for performance.

2. **TanStack Query DevTools**: Click the floating flower icon in development to inspect cached server state, loading states, and API refetch intervals.

3. **Network Tab**: Filter by `Fetch/XHR` to ensure payloads match the Zod schemas defined in the backend.
