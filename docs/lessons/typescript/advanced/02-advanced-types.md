---
title: "Advanced Types"
language: typescript
difficulty: advanced
prerequisites: ["Basic Type System", "Generics Introduction"]
keywords:
  [advanced types, conditional types, mapped types, template literals, type guards, branded types]
---

# Learning Objectives

- Use conditional types for type-level logic
- Create and use mapped types
- Work with template literal types
- Understand type guards and narrowing
- Create branded types for type safety
- Combine advanced type features

# Prerequisites

- Basic Type System
- Generics Introduction

# Introduction

TypeScript's advanced type system enables sophisticated type manipulation and inference. Understanding conditional types, mapped types, and template literal types allows you to create powerful, type-safe abstractions. These features are used extensively in modern TypeScript libraries.

# Core Concepts

## Conditional Types

Types that depend on conditions:

```typescript
type NonNullable<T> = T extends null | undefined ? never : T;

type Test1 = NonNullable<string | null>; // string
type Test2 = NonNullable<number | undefined>; // number

// Extract function return type
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

type FuncReturn = MyReturnType<() => string>; // string
```

## Mapped Types

Transform object types:

```typescript
// Make all properties optional
type Partial<T> = {
  [P in keyof T]?: T[P];
};

// Make all properties required
type Required<T> = {
  [P in keyof T]-?: T[P];
};

// Change property types
type Stringify<T> = {
  [P in keyof T]: string;
};

interface User {
  name: string;
  age: number;
}

type StringUser = Stringify<User>;
// { name: string; age: string; }
```

## Template Literal Types

Create string literal types:

```typescript
type Greeting = `Hello, ${string}`;

const greet: Greeting = "Hello, World"; // OK
// const invalid: Greeting = "Hi";  // Error

// With unions
type Event = "click" | "change" | "submit";
type Handler = `on${Capitalize<Event>}`;
// "onClick" | "onChange" | "onSubmit"
```

## Type Guards

Narrow types with type guards:

```typescript
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function process(value: unknown) {
  if (isString(value)) {
    // TypeScript knows value is string here
    console.log(value.toUpperCase());
  }
}
```

## Branded Types

Create distinct types from primitives:

```typescript
type UserId = number & { readonly brand: unique symbol };
type ProductId = number & { readonly brand: unique symbol };

function createUserId(id: number): UserId {
  return id as UserId;
}

function createProductId(id: number): ProductId {
  return id as ProductId;
}

const userId = createUserId(1);
const productId = createProductId(1);

// userId === productId  // Error! Different branded types
```

## Recursive Types

Types that reference themselves:

```typescript
type JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue };

const json: JsonValue = {
  name: "Alice",
  age: 25,
  tags: ["developer", "typescript"],
  metadata: {
    active: true,
  },
};
```

# Common Mistakes

- **Over-complicating**: Simple types are often better
- **Circular references**: Can cause infinite type recursion
- **Performance**: Complex types slow down compilation
- **Readability**: Complex types can be hard to understand

# Practice Exercises

1. Create a conditional type that extracts array element types.
2. Create a mapped type that makes all properties readonly and optional.
3. Create template literal types for CSS class names.
4. Create a type guard function for a custom type.
5. Create a branded type for email addresses.

Example solution for exercise 1:

```typescript
type ArrayElement<T> = T extends (infer U)[] ? U : never;

type Element1 = ArrayElement<number[]>; // number
type Element2 = ArrayElement<string[]>; // string
type Element3 = ArrayElement<number>; // never
```

# Key Takeaways

- Conditional types enable type-level conditionals
- Mapped types transform object properties
- Template literal types create string literal unions
- Type guards narrow types at runtime
- Branded types create distinct types from primitives
- Recursive types enable complex data structures
- Use advanced types when they add value

# Related Topics

- Basic Type System (TypeScript Beginner #7)
- Advanced Generics (TypeScript Advanced #1)
- Utility Types Introduction (TypeScript Intermediate #8)
