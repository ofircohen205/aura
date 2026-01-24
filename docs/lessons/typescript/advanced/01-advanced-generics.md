---
title: "Advanced Generics"
language: typescript
difficulty: advanced
prerequisites: ["Generics Introduction", "Interfaces", "Classes"]
keywords:
  [generics, conditional types, mapped types, type inference, generic constraints, utility types]
---

# Learning Objectives

- Use advanced generic patterns
- Understand conditional types
- Work with mapped types
- Use generic constraints effectively
- Understand type inference in generics
- Create complex generic utilities

# Prerequisites

- Generics Introduction
- Interfaces
- Classes

# Introduction

Advanced generics enable powerful type manipulation and inference. Understanding conditional types, mapped types, and advanced constraints unlocks sophisticated type patterns. These features are used in libraries and frameworks to provide excellent developer experience with strong type safety.

# Core Concepts

## Generic Constraints with keyof

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const person = { name: "Alice", age: 25 };
const name = getProperty(person, "name"); // Type: string
// const invalid = getProperty(person, "email");  // Error!
```

## Conditional Types

Types that depend on conditions:

```typescript
type IsArray<T> = T extends any[] ? true : false;

type Test1 = IsArray<number[]>; // true
type Test2 = IsArray<string>; // false

// Extract array element type
type ArrayElement<T> = T extends (infer U)[] ? U : never;

type Element = ArrayElement<number[]>; // number
```

## Mapped Types

Create new types by transforming properties:

```typescript
type Optional<T> = {
  [P in keyof T]?: T[P];
};

type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

interface User {
  name: string;
  age: number;
}

type OptionalUser = Optional<User>;
// { name?: string; age?: number; }
```

## Template Literal Types

```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;

type ClickEvent = EventName<"click">; // "onClick"
type ChangeEvent = EventName<"change">; // "onChange"
```

## Infer Keyword

Extract types from other types:

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

function getString(): string {
  return "hello";
}

type StringReturn = ReturnType<typeof getString>; // string
```

## Distributive Conditional Types

```typescript
type ToArray<T> = T extends any ? T[] : never;

type StrArrOrNumArr = ToArray<string | number>;
// string[] | number[] (distributed)
```

# Common Mistakes

- **Over-complicating types**: Keep types readable
- **Not understanding inference**: `infer` can be tricky
- **Circular type references**: Can cause infinite recursion
- **Performance**: Complex types can slow down compiler

# Practice Exercises

1. Create a conditional type that checks if a type is a function.
2. Create a mapped type that makes all properties nullable.
3. Use `infer` to extract the return type of a function.
4. Create a type that extracts all function property names from an object.
5. Create a generic type that deep-readonly an object.

Example solution for exercise 1:

```typescript
type IsFunction<T> = T extends (...args: any[]) => any ? true : false;

type Test1 = IsFunction<() => void>; // true
type Test2 = IsFunction<string>; // false
```

# Key Takeaways

- Conditional types enable type-level logic
- Mapped types transform object types
- `infer` extracts types from other types
- `keyof` and constraints enable powerful generic patterns
- Template literal types create string literal types
- Advanced generics enable sophisticated type manipulation
- Use when they add value, not just because you can

# Related Topics

- Generics Introduction (TypeScript Intermediate #7)
- Utility Types Introduction (TypeScript Intermediate #8)
- Advanced Types (next lesson)
