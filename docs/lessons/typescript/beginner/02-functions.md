---
title: "Functions"
language: typescript
difficulty: beginner
prerequisites: ["Variables and Basic Types"]
keywords: [functions, parameters, return types, arrow functions, function declarations]
---

# Learning Objectives

- Understand how to declare and call functions in TypeScript
- Learn about function parameters and return types
- Use arrow functions
- Understand the difference between function declarations and arrow functions
- Work with optional and default parameters

# Prerequisites

- Variables and Basic Types

# Introduction

Functions are reusable blocks of code that perform a specific task. TypeScript adds type safety to functions by allowing you to specify parameter types and return types. This helps catch errors before your code runs and makes your code more self-documenting.

# Core Concepts

## Function Declarations

You declare functions using the `function` keyword:

```typescript
function greet(name: string): void {
  console.log(`Hello, ${name}!`);
}

greet("Alice"); // Output: Hello, Alice!
```

## Function Parameters and Return Types

TypeScript lets you specify types for parameters and return values:

```typescript
// Function with parameters and return type
function add(a: number, b: number): number {
  return a + b;
}

const result = add(5, 3);
console.log(result); // Output: 8
```

## Arrow Functions

Arrow functions provide a shorter syntax:

```typescript
// Traditional function
function multiply(a: number, b: number): number {
  return a * b;
}

// Arrow function (equivalent)
const multiply = (a: number, b: number): number => {
  return a * b;
};

// Arrow function with implicit return
const multiply = (a: number, b: number): number => a * b;
```

## Optional Parameters

You can make parameters optional using `?`:

```typescript
function greet(name: string, title?: string): void {
  if (title) {
    console.log(`Hello, ${title} ${name}!`);
  } else {
    console.log(`Hello, ${name}!`);
  }
}

greet("Alice"); // Output: Hello, Alice!
greet("Bob", "Mr."); // Output: Hello, Mr. Bob!
```

## Default Parameters

You can provide default values for parameters:

```typescript
function greet(name: string, greeting: string = "Hello"): void {
  console.log(`${greeting}, ${name}!`);
}

greet("Alice"); // Output: Hello, Alice!
greet("Bob", "Hi"); // Output: Hi, Bob!
greet("Charlie", "Goodbye"); // Output: Goodbye, Charlie!
```

## Functions That Don't Return

Use `void` for functions that don't return a value:

```typescript
function printMessage(message: string): void {
  console.log(message);
  // No return statement needed
}
```

## Type Inference

TypeScript can infer return types:

```typescript
// TypeScript infers return type as number
function add(a: number, b: number) {
  return a + b;
}

// Explicit return type (recommended for clarity)
function add(a: number, b: number): number {
  return a + b;
}
```

# Common Mistakes

- **Forgetting parameter types**: Always specify types for function parameters
- **Wrong return type**: Make sure the return type matches what you actually return
- **Using `void` incorrectly**: `void` means no return value, not `undefined`
- **Confusing arrow functions**: Arrow functions have different `this` binding (advanced topic)
- **Optional vs default parameters**: `?` makes it optional, `=` provides a default

# Practice Exercises

1. Write a function that takes two numbers and returns their sum.
2. Write a function that takes a name and an optional greeting, and prints a message.
3. Write an arrow function that calculates the area of a rectangle.
4. Write a function that takes a number and returns `true` if it's even, `false` otherwise.
5. Write a function with a default parameter that greets a user (default greeting: "Hello").

Example solution for exercise 1:

```typescript
function add(a: number, b: number): number {
  return a + b;
}

const result = add(5, 3);
console.log(result); // Output: 8
```

# Key Takeaways

- Functions are declared with `function` keyword or arrow syntax
- Always specify parameter types and return types
- Use `void` for functions that don't return a value
- Optional parameters use `?`, default parameters use `=`
- Arrow functions provide shorter syntax
- TypeScript helps catch function-related errors before runtime

# Related Topics

- Variables and Basic Types (TypeScript Beginner #1)
- Arrays (next lesson)
- Type Annotations (covered in this lesson)
