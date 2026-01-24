---
title: "Conditional Types"
language: typescript
difficulty: advanced
prerequisites: ["Advanced Generics", "Advanced Types"]
keywords:
  [conditional types, type inference, infer, distributive conditional types, type manipulation]
---

# Learning Objectives

- Master conditional type syntax
- Use the `infer` keyword effectively
- Understand distributive conditional types
- Create utility types with conditionals
- Combine conditional types with other features
- Understand when conditionals distribute

# Prerequisites

- Advanced Generics
- Advanced Types

# Introduction

Conditional types enable type-level logic - types that depend on other types. They're one of TypeScript's most powerful features, allowing you to create sophisticated type transformations. Understanding conditional types unlocks advanced type patterns used in libraries and frameworks.

# Core Concepts

## Basic Conditional Types

```typescript
type IsArray<T> = T extends any[] ? true : false;

type Test1 = IsArray<number[]>; // true
type Test2 = IsArray<string>; // false
```

## The infer Keyword

Extract types from other types:

```typescript
// Extract array element type
type ArrayElement<T> = T extends (infer U)[] ? U : never;

type Element = ArrayElement<number[]>; // number

// Extract function return type
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

type FuncReturn = ReturnType<() => string>; // string

// Extract function parameters
type Parameters<T> = T extends (...args: infer P) => any ? P : never;

type FuncParams = Parameters<(a: number, b: string) => void>;
// [number, string]
```

## Distributive Conditional Types

Conditional types distribute over union types:

```typescript
type ToArray<T> = T extends any ? T[] : never;

type StrArrOrNumArr = ToArray<string | number>;
// string[] | number[] (distributed, not (string | number)[])

// Prevent distribution
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;

type UnionArray = ToArrayNonDist<string | number>;
// (string | number)[]
```

## Nested Conditionals

```typescript
type Flatten<T> = T extends (infer U)[] ? (U extends any[] ? Flatten<U> : U) : T;

type Nested = Flatten<number[][]>; // number
```

## Conditional Type Constraints

```typescript
type NonFunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? never : K;
}[keyof T];

interface User {
  name: string;
  age: number;
  greet(): void;
}

type Props = NonFunctionPropertyNames<User>; // "name" | "age"
```

## Practical Examples

```typescript
// Extract promise type
type Awaited<T> = T extends Promise<infer U> ? U : T;

type PromiseValue = Awaited<Promise<string>>; // string

// Check if type is never
type IsNever<T> = [T] extends [never] ? true : false;

type Test1 = IsNever<never>; // true
type Test2 = IsNever<string>; // false
```

# Common Mistakes

- **Not understanding distribution**: Conditionals distribute over unions
- **Circular references**: Can cause infinite type recursion
- **Over-complicating**: Simple types are often better
- **Performance**: Complex conditionals slow compilation

# Practice Exercises

1. Create a conditional type that extracts the first parameter of a function.
2. Create a type that checks if a type is a promise and extracts its value.
3. Create a conditional type that removes null and undefined from a union.
4. Create a type that extracts all non-function properties from an object type.
5. Create a recursive conditional type that flattens nested arrays.

Example solution for exercise 1:

```typescript
type FirstParameter<T> = T extends (first: infer P, ...args: any[]) => any ? P : never;

type Param = FirstParameter<(a: string, b: number) => void>; // string
```

# Key Takeaways

- Conditional types enable type-level conditionals
- `infer` extracts types from other types
- Conditionals distribute over union types
- Can be nested for complex logic
- Used extensively in utility types
- Powerful but can be complex
- Use when they add real value

# Related Topics

- Advanced Generics (TypeScript Advanced #1)
- Advanced Types (TypeScript Advanced #2)
- Utility Types Introduction (TypeScript Intermediate #8)
