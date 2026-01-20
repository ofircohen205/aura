---
title: "Type Annotations"
language: typescript
difficulty: beginner
prerequisites: ["Basic Type System", "Functions", "Arrays"]
keywords: [type annotations, explicit types, type safety, inference, best practices]
---

# Learning Objectives

- Understand when and why to use type annotations
- Add type annotations to variables, functions, and arrays
- Use type annotations effectively without over-annotating
- Understand the balance between explicit types and type inference
- Write more maintainable code with proper type annotations

# Prerequisites

- Basic Type System
- Functions
- Arrays

# Introduction

Type annotations explicitly tell TypeScript what type a value should be. While TypeScript can often infer types automatically, explicit annotations make your code clearer, catch errors earlier, and serve as documentation. Knowing when to use annotations and when to rely on inference is an important skill.

# Core Concepts

## When to Use Type Annotations

### Function Return Types

Always annotate function return types for clarity:

```typescript
// Good - explicit return type
function add(a: number, b: number): number {
  return a + b;
}

// Also works, but less clear
function add(a: number, b: number) {
  return a + b; // TypeScript infers: number
}
```

### Complex Types

Annotate complex types that might be unclear:

```typescript
// Good - explicit annotation
const users: Array<{ name: string; age: number }> = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 30 },
];

// Without annotation, TypeScript infers correctly but it's less clear
const users = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 30 },
];
```

### Variables That Change Type

Annotate when a variable's type might change:

```typescript
// Good - explicit annotation
let value: string | number;
value = "hello"; // OK
value = 42; // OK

// Without annotation, TypeScript infers from first assignment
let value = "hello";
value = 42; // Error! Type 'number' is not assignable to type 'string'
```

### Function Parameters

Always annotate function parameters:

```typescript
// Good - all parameters annotated
function processUser(name: string, age: number, isActive: boolean): void {
  // ...
}

// Bad - missing annotations
function processUser(name, age, isActive) {
  // All are 'any'!
  // ...
}
```

## When Type Inference is Enough

### Simple Variable Declarations

TypeScript can infer simple types:

```typescript
// Inference is fine here
const name = "Alice"; // string
const age = 25; // number
const isStudent = true; // boolean

// Explicit annotation is redundant
const name: string = "Alice"; // Unnecessary
```

### Array Literals

TypeScript infers array types from contents:

```typescript
// Inference works well
const numbers = [1, 2, 3]; // number[]
const names = ["Alice", "Bob"]; // string[]

// Explicit annotation only if needed for clarity
const numbers: number[] = [1, 2, 3];
```

## Best Practices

### Be Explicit for Public APIs

```typescript
// Public function - explicit types
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Internal helper - inference is OK
function formatPrice(price: number) {
  return `$${price.toFixed(2)}`;
}
```

### Use Type Aliases for Complex Types

```typescript
// Good - reusable type alias
type User = {
  name: string;
  age: number;
  email: string;
};

function createUser(user: User): User {
  return { ...user };
}

// Bad - inline complex type
function createUser(user: { name: string; age: number; email: string }): {
  name: string;
  age: number;
  email: string;
} {
  return { ...user };
}
```

### Avoid Over-Annotation

```typescript
// Too much annotation (redundant)
const name: string = "Alice";
const count: number = 5;
const active: boolean = true;

// Better (let TypeScript infer)
const name = "Alice";
const count = 5;
const active = true;
```

# Common Mistakes

- **Over-annotating**: Don't annotate when inference is clear
- **Under-annotating**: Always annotate function parameters and return types
- **Using `any` to avoid annotations**: Fix the types instead
- **Inconsistent style**: Be consistent within your codebase
- **Ignoring type errors**: Fix them, don't suppress with `any`

# Practice Exercises

1. Write a function with explicit parameter and return type annotations.
2. Create a type alias for a complex object type and use it in a function.
3. Write a function that accepts a union type and handles both cases.
4. Create an array with explicit type annotation, then one where inference is sufficient.
5. Write a function signature with all annotations, then identify which are necessary.

Example solution for exercise 1:

```typescript
interface Point {
  x: number;
  y: number;
}

function calculateDistance(p1: Point, p2: Point): number {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  return Math.sqrt(dx * dx + dy * dy);
}

const distance = calculateDistance({ x: 0, y: 0 }, { x: 3, y: 4 });
console.log(distance); // Output: 5
```

# Key Takeaways

- Always annotate function parameters and return types
- Annotate complex types and union types for clarity
- Let TypeScript infer simple variable types
- Use type aliases for reusable complex types
- Be explicit for public APIs, inference is OK for internal code
- Balance between explicit types and inference
- Type annotations serve as documentation

# Related Topics

- Basic Type System (TypeScript Beginner #7)
- Functions (TypeScript Beginner #2)
- Interfaces Introduction (TypeScript Beginner #8)
