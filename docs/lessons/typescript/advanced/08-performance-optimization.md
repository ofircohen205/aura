---
title: "Performance Optimization"
language: typescript
difficulty: advanced
prerequisites: ["All previous TypeScript lessons"]
keywords: [performance, optimization, bundle size, tree shaking, code splitting, type erasure]
---

# Learning Objectives

- Understand TypeScript's impact on performance
- Optimize bundle sizes
- Use tree shaking effectively
- Understand type erasure
- Optimize type checking performance
- Use code splitting strategies

# Prerequisites

- All previous TypeScript lessons

# Introduction

TypeScript adds type safety but doesn't affect runtime performance (types are erased). However, compilation time, bundle size, and type checking performance matter. Understanding optimization techniques helps you build faster, smaller applications.

# Core Concepts

## Type Erasure

TypeScript types are removed at compile time:

```typescript
// TypeScript
function add(a: number, b: number): number {
  return a + b;
}

// Compiled JavaScript (types removed)
function add(a, b) {
  return a + b;
}
```

## Tree Shaking

Remove unused code:

```typescript
// utils.ts
export function used() {
  return "used";
}

export function unused() {
  return "unused";
}

// main.ts
import { used } from "./utils";
// unused is not included in bundle
```

## Code Splitting

Split code into smaller chunks:

```typescript
// Dynamic import for code splitting
async function loadFeature() {
  const module = await import("./heavy-feature");
  module.initialize();
}
```

## Type-Only Imports

Import only types (removed at compile time):

```typescript
import type { User } from "./types";
// User type is not included in JavaScript output

// vs regular import
import { User } from "./types";
// Might include runtime code
```

## Const Assertions

Help with tree shaking:

```typescript
// Use const assertions
const config = {
  apiUrl: "https://api.example.com",
} as const;

// Better for tree shaking than
const config = {
  apiUrl: "https://api.example.com",
};
```

## Avoid Complex Types in Hot Paths

```typescript
// Complex types can slow compilation
type ComplexType = /* very complex type */;

// Simplify when possible
type SimpleType = string | number;
```

## Use const Enums

```typescript
// Regular enum (creates object)
enum Direction {
  Up,
  Down,
}

// Const enum (inlined, no object)
const enum Direction {
  Up,
  Down,
}

const dir = Direction.Up; // Inlined as 0
```

# Common Mistakes

- **Not using type-only imports**: Can include unnecessary code
- **Complex types everywhere**: Can slow compilation
- **Not enabling tree shaking**: Configure bundler properly
- **Ignoring bundle size**: Monitor and optimize
- **Not using const enums**: Regular enums create runtime objects

# Practice Exercises

1. Convert regular imports to type-only imports where appropriate.
2. Use const enums instead of regular enums.
3. Implement code splitting for a large feature.
4. Optimize a module for better tree shaking.
5. Review and simplify complex types that slow compilation.

Example solution for exercise 1:

```typescript
// Before
import { User, createUser } from "./user";
const user: User = createUser("Alice");

// After (if User is only used as type)
import type { User } from "./user";
import { createUser } from "./user";
const user: User = createUser("Alice");
```

# Key Takeaways

- TypeScript types don't affect runtime (erased)
- Use type-only imports to reduce bundle size
- Enable tree shaking in bundler
- Use code splitting for large applications
- Const enums are inlined (no runtime cost)
- Complex types can slow compilation
- Monitor bundle size and compilation time

# Related Topics

- Modules (TypeScript Beginner #9)
- All previous TypeScript lessons
