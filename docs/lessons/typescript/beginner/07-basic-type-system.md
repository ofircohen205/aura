---
title: "Basic Type System"
language: typescript
difficulty: beginner
prerequisites: ["Variables and Basic Types", "Functions"]
keywords: [types, type system, type annotations, type inference, union types, any, unknown]
---

# Learning Objectives

- Understand TypeScript's type system
- Use type annotations effectively
- Understand type inference
- Work with union types
- Understand the difference between `any` and `unknown`

# Prerequisites

- Variables and Basic Types
- Functions

# Introduction

TypeScript's main feature is its type system. Types help catch errors before your code runs and make your code more self-documenting. Understanding how TypeScript's type system works is essential for writing effective TypeScript code.

# Core Concepts

## Type Annotations

You can explicitly specify types:

```typescript
// Variable type annotations
let name: string = "Alice";
let age: number = 25;
let isStudent: boolean = true;

// Function parameter and return types
function greet(name: string): string {
  return `Hello, ${name}!`;
}
```

## Type Inference

TypeScript can often figure out types automatically:

```typescript
// TypeScript infers these types
let name = "Alice"; // type: string
let age = 25; // type: number
let numbers = [1, 2, 3]; // type: number[]

// Explicit annotations are optional but recommended for clarity
let name: string = "Alice";
```

## Union Types

A value can be one of several types:

```typescript
// Value can be string OR number
let id: string | number;
id = "abc123"; // OK
id = 123; // OK
// id = true;   // Error!

// Function that accepts string or number
function printId(id: string | number): void {
  console.log(id);
}

printId("abc"); // OK
printId(123); // OK
```

## The `any` Type

`any` disables type checking (use sparingly):

```typescript
let value: any = "hello";
value = 42; // OK
value = true; // OK
value.foo.bar; // No error (but might crash at runtime!)

// Avoid using 'any' when possible
```

## The `unknown` Type

`unknown` is safer than `any` - requires type checking before use:

```typescript
let value: unknown = "hello";

// value.toUpperCase();  // Error! Can't use unknown without checking

if (typeof value === "string") {
  console.log(value.toUpperCase()); // OK - TypeScript knows it's a string
}
```

## Type Assertions

Tell TypeScript you know more about a type than it does:

```typescript
let value: unknown = "hello";

// Type assertion (use with caution)
let str = value as string;
console.log(str.toUpperCase()); // OK

// Alternative syntax
let str2 = <string>value;
```

## Literal Types

A type that represents a specific value:

```typescript
// Variable can only be this specific value
let direction: "up" | "down" | "left" | "right";
direction = "up"; // OK
direction = "north"; // Error!

// Function with literal return type
function getStatus(): "success" | "error" {
  return "success";
}
```

# Common Mistakes

- **Overusing `any`**: Defeats the purpose of TypeScript - use specific types
- **Not using type annotations**: While inference works, explicit types are clearer
- **Ignoring type errors**: Fix type errors, don't suppress them
- **Using `any` instead of `unknown`**: `unknown` is safer when you don't know the type
- **Type assertions without validation**: Assertions don't validate, they just tell TypeScript to trust you

# Practice Exercises

1. Create a variable that can be either a string or a number.
2. Write a function that accepts `string | number` and returns a string.
3. Create a variable with a literal type that can only be "red", "green", or "blue".
4. Write a function that safely handles an `unknown` value by checking its type.
5. Create a function with explicit return type annotations.

Example solution for exercise 2:

```typescript
function toString(value: string | number): string {
  if (typeof value === "string") {
    return value;
  } else {
    return value.toString();
  }
}

console.log(toString("hello")); // Output: hello
console.log(toString(42)); // Output: 42
```

# Key Takeaways

- TypeScript's type system catches errors before runtime
- Use type annotations for clarity, even when inference works
- Union types (`|`) allow values to be one of several types
- Avoid `any` - use specific types or `unknown` when needed
- `unknown` is safer than `any` - requires type checking
- Type assertions tell TypeScript about types you know
- Literal types represent specific values

# Related Topics

- Variables and Basic Types (TypeScript Beginner #1)
- Functions (TypeScript Beginner #2)
- Interfaces (TypeScript Intermediate #1)
