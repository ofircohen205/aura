---
title: "Interfaces"
language: typescript
difficulty: intermediate
prerequisites: ["Interfaces Introduction", "Objects"]
keywords:
  [interfaces, type definitions, contracts, extending interfaces, optional properties, readonly]
---

# Learning Objectives

- Create comprehensive interfaces
- Extend and combine interfaces
- Use optional and readonly properties
- Understand interface vs type aliases
- Create interfaces for functions and classes
- Use index signatures

# Prerequisites

- Interfaces Introduction
- Objects

# Introduction

Interfaces are fundamental to TypeScript's type system. While you learned the basics earlier, intermediate interfaces cover advanced patterns like extending interfaces, function interfaces, and index signatures. Mastering interfaces is essential for building robust TypeScript applications.

# Core Concepts

## Extending Interfaces

Interfaces can extend other interfaces:

```typescript
interface Animal {
  name: string;
  age: number;
}

interface Dog extends Animal {
  breed: string;
  bark(): void;
}

const myDog: Dog = {
  name: "Buddy",
  age: 3,
  breed: "Golden Retriever",
  bark() {
    console.log("Woof!");
  },
};
```

## Multiple Inheritance

Interfaces can extend multiple interfaces:

```typescript
interface Flyable {
  fly(): void;
}

interface Swimmable {
  swim(): void;
}

interface Duck extends Flyable, Swimmable {
  quack(): void;
}

const duck: Duck = {
  fly() {
    console.log("Flying");
  },
  swim() {
    console.log("Swimming");
  },
  quack() {
    console.log("Quack");
  },
};
```

## Optional and Readonly Properties

```typescript
interface User {
  readonly id: number; // Cannot be changed after creation
  name: string;
  email?: string; // Optional
  age?: number; // Optional
}

const user: User = {
  id: 1,
  name: "Alice",
  // email and age are optional
};

// user.id = 2;  // Error! id is readonly
```

## Function Interfaces

Interfaces can describe function signatures:

```typescript
interface MathOperation {
  (a: number, b: number): number;
}

const add: MathOperation = (a, b) => a + b;
const multiply: MathOperation = (a, b) => a * b;

console.log(add(5, 3)); // Output: 8
```

## Index Signatures

Allow dynamic property names:

```typescript
interface StringDictionary {
  [key: string]: string;
}

const dict: StringDictionary = {
  name: "Alice",
  city: "New York",
  // Can add any string key with string value
};

interface NumberDictionary {
  [key: string]: number;
}

const scores: NumberDictionary = {
  math: 95,
  science: 87,
};
```

## Interface vs Type Alias

Both can be similar, but have differences:

```typescript
// Interface
interface Person {
  name: string;
  age: number;
}

// Type alias (similar)
type PersonType = {
  name: string;
  age: number;
};

// Interfaces can be extended and merged
interface Person {
  email?: string; // Merges with previous declaration
}

// Type aliases can use unions, intersections, etc.
type ID = string | number;
type Status = "active" | "inactive";
```

## Class Implementing Interfaces

Classes can implement interfaces:

```typescript
interface Drawable {
  draw(): void;
}

class Circle implements Drawable {
  draw() {
    console.log("Drawing circle");
  }
}

class Rectangle implements Drawable {
  draw() {
    console.log("Drawing rectangle");
  }
}
```

## Generic Interfaces

Interfaces can be generic:

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
```

# Common Mistakes

- **Confusing interface and type**: Use interfaces for object shapes, types for unions/intersections
- **Not using readonly when appropriate**: Mark properties that shouldn't change
- **Overusing index signatures**: They reduce type safety
- **Forgetting optional properties**: Use `?` for properties that might not exist
- **Not extending when you should**: Use inheritance to avoid duplication

# Practice Exercises

1. Create an interface that extends another interface with additional properties.
2. Create an interface for a function that validates input and returns a boolean.
3. Create an interface with index signatures for a configuration object.
4. Create a generic interface for a repository pattern.
5. Create interfaces that use multiple inheritance.

Example solution for exercise 1:

```typescript
interface Vehicle {
  make: string;
  model: string;
  year: number;
}

interface Car extends Vehicle {
  doors: number;
  fuelType: string;
}

const myCar: Car = {
  make: "Toyota",
  model: "Camry",
  year: 2020,
  doors: 4,
  fuelType: "gasoline",
};
```

# Key Takeaways

- Interfaces define contracts for object shapes
- Interfaces can extend other interfaces (single or multiple)
- Use `readonly` for immutable properties
- Use `?` for optional properties
- Index signatures allow dynamic property names
- Interfaces can describe function signatures
- Classes can implement interfaces
- Interfaces can be generic
- Prefer interfaces for object shapes, types for unions/intersections

# Related Topics

- Interfaces Introduction (TypeScript Beginner #8)
- Classes (next lesson)
- Generics (TypeScript Advanced #1)
