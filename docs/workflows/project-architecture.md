## Backend Architecture

### Layer Structure

1. **Core Layer** (`src/core/`)
   - Configuration management (config.py): fetches values from .env.local/staging/production and creates a global configuration object
   - Security utilities (security.py): JWT, password hashing
   - Timezone utilities (timezone.py): instead of datetime.now(), we use Asia/Jerusalem timezone

2. **Database Layer** (`src/db/`)
   - SQLModel/ORM models (each DB table will have its own python file under `models` directory)
   - Database connection management (database.py)
   - Session handling for dependency injection in API (database.py -> SessionDep)

3. **DAO Layer** (`src/dao/`)
   - The only place that talks with the DB.
   - Database operations abstraction (BaseDAO in base.py)
   - Each DB table has its own class (inherits BaseDAO), must implement base queries, can add specific queries.

4. **Service Layer** (`src/services/`)
   - Business logic
   - Integration with external services (for example OpenAI client)
   - Orchestration of multiple operations
   - DAO Layer wrapper - for each DB table there will be a dedicated folder and under it 3 files:
     ```text
     ├── services/                
     │   ├── users/
     │   │   ├── __init__.py
     │   │   ├── exceptions.py
     │   │   ├── service.py
     .
     .
     .
     ```

5. **API Layer** (`src/api/`)
   - FastAPI endpoints (with versioning)
   - Request/response validation (Pydantic schemas)
   - Authentication & authorization
   - Current user handling for dependency injection in API (dependencies.py -> CurrentUser)
   - Exceptions from Service Layer are translated into HTTP Exceptions
   - Folder structure for example):
     ```text
     ├── v1/                
     │   ├── users/
     │   │   ├── __init__.py
     │   │   ├── endpoints.py
     │   │   ├── exceptions.py
     │   │   ├── schemas.py
     .
     .
     .
     ```

6. **Jobs Layer** (`src/jobs/`)
   - For example: Data Pipeline (ETL) job, Clean-up data job, etc.
   - README.md for explaining the logic of the job.

## Frontend Architecture

### Feature-Based Structure

1. **Core** (`src/core/`): This folder contains the foundational infrastructure and setup code that runs the application (the "engine").
   - api/: Configures the base HTTP client (like an Axios instance) with interceptors, base URLs, and global error handling used by all services.
   - config/: Centralizes environment variables, global constants, and third-party library settings to prevent hardcoded values throughout the app.
   - routing/: Defines the top-level application router, including the main route list, navigation guards (middleware), and layout wrappers.
   - types/: Holds global utility types and generic interfaces (like Nullable<T> or AsyncState) that are agnostic to specific business logic.
2. **Shared** (`src/shared/`): This folder acts as an internal library of reusable code that can be imported by any feature.
   - components/: Contains generic, "dumb" UI elements (like Buttons, Inputs, or Modals) that form your design system and rely only on props.
   - hooks/: Encapsulates reusable, non-business logic (like useOnClickOutside or useMediaQuery) that solves common UI problems.
   - services/: Provides general-purpose utilities that interact with the browser or external tools, such as LocalStorage wrappers, Logging, or Analytics.
   - stores/: Manages global UI state that is not specific to one feature, such as theme settings (dark mode), global toast notifications, or loading spinners.
   - types/: Defines domain interfaces that are used across multiple features (e.g., a User or Pagination interface) to ensure data consistency.
   - utils/: Contains pure helper functions for common tasks like date formatting, currency conversion, or string manipulation that have no side effects.
3. **Features** (`src/features/`): Self-contained feature modules
   - Folder structure for an example feature:
    ```text              
    ├── example/
    │   ├── components/
    │   ├── hooks/
    │   ├── pages/
    │   ├── services/
    │   ├── stores/
    │   ├── types/
    │   ├── index.ts
    .
    .
    .
    ```
   - components: Contains the reusable, presentational UI elements (like buttons or forms) specific to this feature that receive data and render views.
   - hooks: Encapsulates reusable logic and complex behavior to separate calculations from the visual UI components.
   - pages: Serves as the main route entry points (screens) that compose the smaller components together and connect them to data.
   - services: Handles all external communication, such as HTTP requests and API calls to fetch or send data to the backend.
   - stores: Manages the feature's shared state and business logic, ensuring data remains consistent across different components.
   - types: Defines the TypeScript interfaces and data models (contracts) to ensure type safety throughout the feature.
   - index.ts: Acts as the public "gatekeeper" that exports only the necessary parts of the feature to the rest of the app, keeping internal details private.
4. **layouts** (`src/layouts`): Defines the structural templates (such as Sidebars, Headers, or AuthWrappers) that wrap around page content to maintain a consistent UI across the application.
4. **assets** (`src/assets`): Stores static resources such as images, icons, fonts, and global stylesheets that are imported into components or compiled with the build.

### State Management

- **React Query**: Manages asynchronous server state by handling data fetching, caching, synchronization, and background updates to keep the UI in sync with the backend.
- **Zustand**: Handles global client state for volatile UI data like active filters, sidebar visibility, or complex multi-step form data without complex boilerplate.
- **React Context**: Provides a native way to pass foundational, low-frequency data like current theme, localization settings, or user authentication status deep into the component tree without prop drilling.

### Technology Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **Forms**: React Hook Form + Zod validation
- **Routing**: React Router v7.

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
   - Interfaces with shared core libraries (`libs/core-py`)

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