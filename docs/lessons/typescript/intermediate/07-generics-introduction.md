---
title: "Generics Introduction"
language: typescript
difficulty: intermediate
prerequisites: ["Functions", "Interfaces", "Classes"]
keywords:
  [generics, type parameters, reusable code, type safety, generic functions, generic classes]
---

# Learning Objectives

- Understand what generics are and why they're useful
- Create generic functions
- Create generic interfaces and classes
- Use generic constraints
- Understand when to use generics
- Work with multiple type parameters

# Prerequisites

- Functions
- Interfaces
- Classes

# Introduction

Generics allow you to create reusable code that works with multiple types while maintaining type safety. Instead of using `any` or creating separate functions for each type, generics let you write code once and use it with different types. Understanding generics is essential for writing flexible, type-safe TypeScript code.

# Core Concepts

## Generic Functions

Functions that work with multiple types:

```typescript
// Without generics (limited)
function identity(arg: number): number {
  return arg;
}

// With generics (flexible)
function identity<T>(arg: T): T {
  return arg;
}

// Usage
const num = identity<number>(42);
const str = identity<string>("hello");
const bool = identity<boolean>(true);

// TypeScript can infer types
const num2 = identity(42); // TypeScript knows it's number
```

## Generic Interfaces

```typescript
interface Container<T> {
  value: T;
  getValue(): T;
  setValue(value: T): void;
}

const numberContainer: Container<number> = {
  value: 42,
  getValue() {
    return this.value;
  },
  setValue(v) {
    this.value = v;
  },
};

const stringContainer: Container<string> = {
  value: "hello",
  getValue() {
    return this.value;
  },
  setValue(v) {
    this.value = v;
  },
};
```

## Generic Classes

```typescript
class Box<T> {
  private contents: T;

  constructor(value: T) {
    this.contents = value;
  }

  getValue(): T {
    return this.contents;
  }

  setValue(value: T): void {
    this.contents = value;
  }
}

const numberBox = new Box<number>(42);
const stringBox = new Box<string>("hello");
```

## Generic Constraints

Limit what types can be used:

```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(item: T): void {
  console.log(item.length);
}

logLength("hello"); // OK - string has length
logLength([1, 2, 3]); // OK - array has length
// logLength(42);       // Error - number doesn't have length
```

## Multiple Type Parameters

```typescript
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}

const result = pair<string, number>("Alice", 25);
console.log(result); // Output: ["Alice", 25]
```

## Using Type Parameters in Constraints

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const person = { name: "Alice", age: 25 };
const name = getProperty(person, "name"); // Type: string
const age = getProperty(person, "age"); // Type: number
// const invalid = getProperty(person, "email");  // Error!
```

## Default Type Parameters

```typescript
interface ApiResponse<T = any> {
  data: T;
  status: number;
}

const response1: ApiResponse<string> = { data: "hello", status: 200 };
const response2: ApiResponse = { data: 42, status: 200 }; // Uses default 'any'
```

# Common Mistakes

- **Overusing generics**: Not everything needs to be generic
- **Using `any` instead of generics**: Generics provide type safety
- **Forgetting constraints**: Use constraints to limit generic types
- **Too many type parameters**: Keep it simple, 1-2 parameters usually enough
- **Not understanding inference**: Let TypeScript infer when possible

# Practice Exercises

1. Create a generic function that returns the first element of an array.
2. Create a generic class for a stack data structure.
3. Create a generic function with constraints that works only with objects.
4. Create a generic function that swaps two values.
5. Create a generic interface for a repository pattern.

Example solution for exercise 1:

```typescript
function first<T>(array: T[]): T | undefined {
  return array[0];
}

const numbers = [1, 2, 3];
const firstNum = first(numbers); // Type: number | undefined

const strings = ["a", "b", "c"];
const firstStr = first(strings); // Type: string | undefined
```

# Key Takeaways

- Generics provide type-safe, reusable code
- Use `<T>` syntax for type parameters
- Generics work with functions, interfaces, and classes
- Use constraints (`extends`) to limit generic types
- TypeScript can often infer generic types
- Don't overuse generics - use when they add value
- Generics maintain type safety while providing flexibility

# Related Topics

- Functions (TypeScript Beginner #2)
- Interfaces (TypeScript Intermediate #1)
- Classes (TypeScript Intermediate #2)
- Advanced Generics (TypeScript Advanced #1)
