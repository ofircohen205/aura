---
title: "Modules and Namespaces"
language: typescript
difficulty: intermediate
prerequisites: ["Modules", "Interfaces", "Classes"]
keywords:
  [modules, namespaces, module resolution, barrel exports, module organization, code splitting]
---

# Learning Objectives

- Organize code using modules effectively
- Understand module resolution
- Use namespaces for code organization
- Create barrel exports
- Understand module vs namespace
- Organize large codebases

# Prerequisites

- Modules
- Interfaces
- Classes

# Introduction

As applications grow, organizing code becomes critical. TypeScript provides modules and namespaces for code organization. Understanding when and how to use them helps you build maintainable, scalable applications. This lesson covers advanced module patterns and organization strategies.

# Core Concepts

## Module Organization

Organize related code in modules:

```typescript
// math/arithmetic.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

// math/geometry.ts
export function area(radius: number): number {
  return Math.PI * radius ** 2;
}
```

## Barrel Exports

Create index files that re-export from multiple modules:

```typescript
// math/index.ts
export * from "./arithmetic";
export * from "./geometry";

// Usage
import { add, area } from "./math";
```

## Namespaces

Alternative to modules for organization:

```typescript
namespace MathUtils {
  export function add(a: number, b: number): number {
    return a + b;
  }

  export namespace Geometry {
    export function area(radius: number): number {
      return Math.PI * radius ** 2;
    }
  }
}

// Usage
const result = MathUtils.add(5, 3);
const circleArea = MathUtils.Geometry.area(5);
```

## Module vs Namespace

- **Modules**: Preferred for modern code, better tree-shaking
- **Namespaces**: Legacy pattern, still useful in some cases

```typescript
// Module approach (preferred)
// math.ts
export function add(a: number, b: number): number {
  return a + b;
}

// Namespace approach (legacy)
namespace Math {
  export function add(a: number, b: number): number {
    return a + b;
  }
}
```

## Module Resolution

TypeScript resolves modules based on configuration:

```json
// tsconfig.json
{
  "compilerOptions": {
    "moduleResolution": "node", // or "classic"
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@utils/*": ["utils/*"]
    }
  }
}
```

## Path Aliases

Use path aliases for cleaner imports:

```typescript
// Instead of
import { util } from "../../../utils/helper";

// Use alias
import { util } from "@utils/helper";
```

## Dynamic Imports

Load modules dynamically:

```typescript
async function loadModule() {
  const module = await import("./heavy-module");
  module.doSomething();
}
```

# Common Mistakes

- **Mixing modules and namespaces**: Choose one approach
- **Circular dependencies**: Module A imports B, B imports A
- **Not using barrel exports**: Makes imports cleaner
- **Deep import paths**: Use path aliases
- **Not organizing logically**: Group related code together

# Practice Exercises

1. Organize related functions into a module with barrel exports.
2. Create a namespace for utility functions.
3. Set up path aliases in tsconfig.json.
4. Create a module structure for a feature (e.g., user management).
5. Use dynamic imports to load a module conditionally.

Example solution for exercise 1:

```typescript
// utils/string.ts
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// utils/number.ts
export function round(num: number, decimals: number): number {
  return Number(num.toFixed(decimals));
}

// utils/index.ts
export * from "./string";
export * from "./number";

// Usage
import { capitalize, round } from "./utils";
```

# Key Takeaways

- Modules are the preferred way to organize code
- Barrel exports (index.ts) simplify imports
- Namespaces are legacy but still useful in some cases
- Use path aliases for cleaner import paths
- Organize code logically by feature or functionality
- Avoid circular dependencies
- Dynamic imports enable code splitting

# Related Topics

- Modules (TypeScript Beginner #9)
- Classes (TypeScript Intermediate #2)
- Interfaces (TypeScript Intermediate #1)
