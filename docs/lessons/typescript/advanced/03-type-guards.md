---
title: "Type Guards"
language: typescript
difficulty: advanced
prerequisites: ["Basic Type System", "Functions"]
keywords:
  [type guards, type narrowing, typeof, instanceof, user-defined type guards, discriminated unions]
---

# Learning Objectives

- Understand type narrowing and type guards
- Use `typeof` and `instanceof` for type narrowing
- Create user-defined type guards
- Work with discriminated unions
- Understand assertion functions
- Use type guards effectively

# Prerequisites

- Basic Type System
- Functions

# Introduction

Type guards are expressions that perform runtime checks and allow TypeScript to narrow types. They're essential for working with union types and `unknown` types safely. Understanding type guards enables you to write type-safe code that handles different types at runtime.

# Core Concepts

## typeof Type Guards

Narrow types using `typeof`:

```typescript
function process(value: string | number) {
  if (typeof value === "string") {
    // TypeScript knows value is string here
    console.log(value.toUpperCase());
  } else {
    // TypeScript knows value is number here
    console.log(value.toFixed(2));
  }
}
```

## instanceof Type Guards

Narrow types using `instanceof`:

```typescript
class Dog {
  bark() {
    console.log("Woof!");
  }
}

class Cat {
  meow() {
    console.log("Meow!");
  }
}

function makeSound(animal: Dog | Cat) {
  if (animal instanceof Dog) {
    animal.bark(); // TypeScript knows it's Dog
  } else {
    animal.meow(); // TypeScript knows it's Cat
  }
}
```

## User-Defined Type Guards

Create custom type guard functions:

```typescript
interface Fish {
  swim(): void;
}

interface Bird {
  fly(): void;
}

function isFish(pet: Fish | Bird): pet is Fish {
  return (pet as Fish).swim !== undefined;
}

function move(pet: Fish | Bird) {
  if (isFish(pet)) {
    pet.swim(); // TypeScript knows it's Fish
  } else {
    pet.fly(); // TypeScript knows it's Bird
  }
}
```

## Discriminated Unions

Use a common property to discriminate:

```typescript
interface Circle {
  kind: "circle";
  radius: number;
}

interface Rectangle {
  kind: "rectangle";
  width: number;
  height: number;
}

type Shape = Circle | Rectangle;

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
  }
}
```

## Assertion Functions

Functions that assert types:

```typescript
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error("Value is not a string");
  }
}

function process(value: unknown) {
  assertIsString(value);
  // TypeScript knows value is string here
  console.log(value.toUpperCase());
}
```

## in Operator

Check for property existence:

```typescript
interface Dog {
  bark(): void;
}

interface Cat {
  meow(): void;
}

function makeSound(pet: Dog | Cat) {
  if ("bark" in pet) {
    pet.bark(); // TypeScript knows it's Dog
  } else {
    pet.meow(); // TypeScript knows it's Cat
  }
}
```

# Common Mistakes

- **Not using type guards**: TypeScript can't narrow without them
- **Wrong type guard syntax**: Must return `value is Type`
- **Not handling all cases**: Exhaustiveness checking helps
- **Over-complicating**: Simple checks are often enough

# Practice Exercises

1. Create a type guard that checks if a value is a number array.
2. Create a discriminated union for different API response types.
3. Write a function that uses type guards to safely process unknown data.
4. Create an assertion function that validates an object shape.
5. Use type guards to narrow a union type in a function.

Example solution for exercise 1:

```typescript
function isNumberArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.every(item => typeof item === "number");
}

function process(value: unknown) {
  if (isNumberArray(value)) {
    const sum = value.reduce((a, b) => a + b, 0);
    console.log(`Sum: ${sum}`);
  }
}
```

# Key Takeaways

- Type guards narrow types at runtime
- Use `typeof` and `instanceof` for built-in types
- Create user-defined type guards with `value is Type` syntax
- Discriminated unions use a common property to narrow
- Assertion functions assert types and throw if wrong
- `in` operator checks for property existence
- Type guards enable safe type narrowing

# Related Topics

- Basic Type System (TypeScript Beginner #7)
- Functions (TypeScript Beginner #2)
- Advanced Types (TypeScript Advanced #2)
