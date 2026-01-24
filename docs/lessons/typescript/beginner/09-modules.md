---
title: "Modules"
language: typescript
difficulty: beginner
prerequisites: ["Functions", "Interfaces Introduction"]
keywords: [modules, import, export, ES6 modules, code organization, file structure]
---

# Learning Objectives

- Understand what modules are and why we use them
- Export functions, variables, and types from modules
- Import from other modules
- Understand default vs named exports
- Organize code using modules

# Prerequisites

- Functions
- Interfaces Introduction

# Introduction

Modules allow you to split your code into separate files, making it more organized and reusable. TypeScript uses ES6 module syntax (`import` and `export`) to share code between files. Understanding modules is essential for building larger applications.

# Core Concepts

## Exporting (Making Code Available)

### Named Exports

Export individual items with names:

```typescript
// math.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

export const PI = 3.14159;
```

### Default Export

Export one main item as default:

```typescript
// calculator.ts
export default function calculate(a: number, b: number): number {
  return a + b;
}

// Or export a default object/class
export default class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
}
```

### Exporting Types and Interfaces

You can export types and interfaces:

```typescript
// types.ts
export interface Person {
  name: string;
  age: number;
}

export type Status = "active" | "inactive";
```

## Importing (Using Code from Other Files)

### Named Imports

Import specific items by name:

```typescript
// main.ts
import { add, subtract, PI } from "./math";

const result = add(5, 3);
console.log(result); // Output: 8
```

### Default Import

Import the default export:

```typescript
// main.ts
import calculate from "./calculator";

const result = calculate(5, 3);
```

### Mixed Imports

Import both default and named exports:

```typescript
// main.ts
import calculate, { PI } from "./calculator";
```

### Import Everything

Import all exports as an object:

```typescript
// main.ts
import * as math from "./math";

const result = math.add(5, 3);
console.log(math.PI);
```

### Type-Only Imports

Import only types (removed at compile time):

```typescript
// main.ts
import type { Person } from "./types";

const person: Person = {
  name: "Alice",
  age: 25,
};
```

## File Extensions

When importing, you typically omit the `.ts` extension:

```typescript
// Good
import { add } from "./math";

// Also works (but less common)
import { add } from "./math.ts";
```

## Re-exporting

You can re-export from another module:

```typescript
// utils.ts
export { add, subtract } from "./math";
export { Person } from "./types";
```

# Common Mistakes

- **Forgetting to export**: Code must be exported to be used in other files
- **Wrong import path**: Make sure paths are correct (relative or absolute)
- **Mixing default and named exports incorrectly**: Default exports don't use curly braces
- **Circular dependencies**: Module A imports B, B imports A (causes issues)
- **Not using type-only imports**: Use `import type` for types to avoid runtime imports

# Practice Exercises

1. Create a math module with add, subtract, multiply, and divide functions, and export them.
2. Create a types module with a Person interface and export it.
3. Create a main file that imports and uses the math functions.
4. Create a default export for a Calculator class.
5. Re-export multiple items from different modules in an index file.

Example solution for exercise 1:

```typescript
// math.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

export function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Division by zero");
  }
  return a / b;
}
```

# Key Takeaways

- Modules split code into separate, reusable files
- Use `export` to make code available to other files
- Use `import` to use code from other files
- Named exports use `{}`, default exports don't
- You can export functions, variables, types, and interfaces
- Use `import type` for type-only imports
- Modules make code more organized and maintainable

# Related Topics

- Functions (TypeScript Beginner #2)
- Interfaces Introduction (TypeScript Beginner #8)
- Classes (TypeScript Intermediate #2)
