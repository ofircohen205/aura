---
title: "Interfaces Introduction"
language: typescript
difficulty: beginner
prerequisites: ["Objects", "Basic Type System"]
keywords: [interfaces, type definitions, object types, contracts, shape]
---

# Learning Objectives

- Understand what interfaces are and why we use them
- Define interfaces for objects
- Use interfaces to type function parameters
- Understand optional and readonly properties
- Create reusable type definitions

# Prerequisites

- Objects
- Basic Type System

# Introduction

Interfaces define the "shape" or structure that objects should have. They act as contracts that specify what properties an object must have and what types those properties should be. Interfaces make your code more maintainable and help catch errors early.

# Core Concepts

## Defining Interfaces

You define an interface using the `interface` keyword:

```typescript
interface Person {
  name: string;
  age: number;
  city: string;
}
```

## Using Interfaces

Use interfaces to type objects:

```typescript
interface Person {
  name: string;
  age: number;
  city: string;
}

const person: Person = {
  name: "Alice",
  age: 25,
  city: "New York",
};

// TypeScript ensures the object matches the interface
// const person2: Person = {
//     name: "Bob"
//     // Error! Missing 'age' and 'city'
// };
```

## Optional Properties

Make properties optional using `?`:

```typescript
interface Person {
  name: string;
  age: number;
  email?: string; // Optional property
}

const person1: Person = {
  name: "Alice",
  age: 25,
  // email is optional, so we can omit it
};

const person2: Person = {
  name: "Bob",
  age: 30,
  email: "bob@example.com",
};
```

## Readonly Properties

Make properties read-only using `readonly`:

```typescript
interface Point {
  readonly x: number;
  readonly y: number;
}

const point: Point = { x: 10, y: 20 };
// point.x = 30;  // Error! Cannot assign to 'x' because it is a read-only property
```

## Interfaces with Methods

Interfaces can define methods:

```typescript
interface Calculator {
  add(a: number, b: number): number;
  subtract(a: number, b: number): number;
}

const calc: Calculator = {
  add(a, b) {
    return a + b;
  },
  subtract(a, b) {
    return a - b;
  },
};
```

## Function Parameters

Use interfaces to type function parameters:

```typescript
interface User {
  name: string;
  age: number;
}

function greetUser(user: User): void {
  console.log(`Hello, ${user.name}!`);
}

greetUser({ name: "Alice", age: 25 }); // OK
```

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

# Common Mistakes

- **Forgetting required properties**: All non-optional properties must be present
- **Wrong property types**: Properties must match the interface type exactly
- **Trying to modify readonly properties**: `readonly` prevents modification
- **Confusing interfaces with classes**: Interfaces define shape, classes implement behavior
- **Over-complicating interfaces**: Keep interfaces simple and focused

# Practice Exercises

1. Create an interface for a Book with title, author, and year properties.
2. Create an interface for a Student that extends a Person interface, adding a studentId.
3. Write a function that accepts a Person interface and returns a greeting.
4. Create an interface with optional and readonly properties.
5. Create an interface for a Shape with a method to calculate area.

Example solution for exercise 1:

```typescript
interface Book {
  title: string;
  author: string;
  year: number;
}

const book: Book = {
  title: "The Great Gatsby",
  author: "F. Scott Fitzgerald",
  year: 1925,
};
```

# Key Takeaways

- Interfaces define the shape/structure of objects
- Use `interface` keyword to define reusable type contracts
- Optional properties use `?`, readonly properties use `readonly`
- Interfaces can define methods, not just properties
- Interfaces can extend other interfaces
- TypeScript ensures objects match their interface definitions
- Interfaces make code more maintainable and self-documenting

# Related Topics

- Objects (TypeScript Beginner #4)
- Basic Type System (TypeScript Beginner #7)
- Classes (TypeScript Intermediate #2)
