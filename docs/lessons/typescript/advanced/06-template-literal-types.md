---
title: "Template Literal Types"
language: typescript
difficulty: advanced
prerequisites: ["Advanced Types", "Basic Type System"]
keywords: [template literal types, string manipulation, type-level strings, pattern matching]
---

# Learning Objectives

- Create template literal types
- Manipulate string types at the type level
- Use template literals with unions
- Create type-safe string patterns
- Combine template literals with other advanced types
- Understand string type manipulation

# Prerequisites

- Advanced Types
- Basic Type System

# Introduction

Template literal types allow you to manipulate and combine string literal types. They enable type-safe string patterns, API route types, CSS class names, and more. Understanding template literal types unlocks powerful type-safe string manipulation patterns.

# Core Concepts

## Basic Template Literal Types

```typescript
type Greeting = `Hello, ${string}`;

const greet1: Greeting = "Hello, World"; // OK
const greet2: Greeting = "Hello, TypeScript"; // OK
// const invalid: Greeting = "Hi";  // Error

type Event = "click" | "change";
type Handler = `on${Capitalize<Event>}`;
// "onClick" | "onChange"
```

## String Manipulation Utilities

TypeScript provides string manipulation types:

```typescript
// Uppercase
type Upper = Uppercase<"hello">; // "HELLO"

// Lowercase
type Lower = Lowercase<"HELLO">; // "hello"

// Capitalize
type Cap = Capitalize<"hello">; // "Hello"

// Uncapitalize
type Uncap = Uncapitalize<"Hello">; // "hello"
```

## Combining with Unions

Template literals distribute over unions:

```typescript
type Color = "red" | "blue" | "green";
type Size = "small" | "large";

type ButtonClass = `btn-${Color}-${Size}`;
// "btn-red-small" | "btn-red-large" | "btn-blue-small" | ...

// All combinations
type AllCombinations = `${Color}-${Size}`;
```

## Pattern Matching

```typescript
type ExtractRoute<T> = T extends `/${infer Route}` ? Route : never;

type Route1 = ExtractRoute<"/users">; // "users"
type Route2 = ExtractRoute<"/posts/123">; // "posts/123"
```

## API Route Types

```typescript
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type Route = "/users" | "/posts" | "/comments";

type ApiEndpoint = `${HttpMethod} ${Route}`;
// "GET /users" | "POST /users" | "GET /posts" | ...
```

## CSS Class Names

```typescript
type Variant = "primary" | "secondary" | "danger";
type Size = "sm" | "md" | "lg";

type ButtonClass = `btn btn-${Variant} btn-${Size}`;
// "btn btn-primary btn-sm" | "btn btn-primary btn-md" | ...
```

## Complex Patterns

```typescript
type PathParams<T> = T extends `${string}:${infer Param}/${infer Rest}`
  ? Param | PathParams<`/${Rest}`>
  : T extends `${string}:${infer Param}`
    ? Param
    : never;

type Params = PathParams<"/users/:id/posts/:postId">;
// "id" | "postId"
```

# Common Mistakes

- **Over-complex patterns**: Keep template literals readable
- **Not understanding distribution**: They distribute over unions
- **Performance**: Complex template literals can slow compilation

# Practice Exercises

1. Create template literal types for CSS class combinations.
2. Create a type that extracts route parameters from a path string.
3. Create a type that generates event handler names from event types.
4. Create a type-safe API endpoint type system.
5. Create a type that validates email-like string patterns.

Example solution for exercise 1:

```typescript
type Color = "red" | "blue" | "green";
type Variant = "light" | "dark";

type ColorClass = `text-${Color}-${Variant}`;
// "text-red-light" | "text-red-dark" | "text-blue-light" | ...
```

# Key Takeaways

- Template literal types manipulate string types
- Use `${Type}` syntax for interpolation
- String utilities: `Uppercase`, `Lowercase`, `Capitalize`, `Uncapitalize`
- Template literals distribute over unions
- Can extract patterns with `infer`
- Enable type-safe string patterns
- Useful for routes, CSS classes, event names

# Related Topics

- Advanced Types (TypeScript Advanced #2)
- Mapped Types (TypeScript Advanced #5)
- Type Guards (TypeScript Advanced #3)
