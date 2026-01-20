---
title: "Utility Types Introduction"
language: typescript
difficulty: intermediate
prerequisites: ["Generics Introduction", "Interfaces"]
keywords: [utility types, Partial, Required, Pick, Omit, Readonly, Record, type manipulation]
---

# Learning Objectives

- Understand TypeScript's built-in utility types
- Use `Partial`, `Required`, `Readonly`
- Use `Pick` and `Omit` to select properties
- Use `Record` to create object types
- Combine utility types
- Understand when to use each utility type

# Prerequisites

- Generics Introduction
- Interfaces

# Introduction

TypeScript provides utility types that help you manipulate and transform existing types. These utilities make it easy to create new types based on existing ones without rewriting them. Understanding utility types helps you write more flexible and maintainable type definitions.

# Core Concepts

## Partial<T>

Makes all properties optional:

```typescript
interface User {
  name: string;
  age: number;
  email: string;
}

type PartialUser = Partial<User>;
// Equivalent to:
// {
//     name?: string;
//     age?: number;
//     email?: string;
// }

function updateUser(user: User, updates: Partial<User>): User {
  return { ...user, ...updates };
}
```

## Required<T>

Makes all properties required:

```typescript
interface Config {
  host?: string;
  port?: number;
}

type RequiredConfig = Required<Config>;
// All properties are now required
```

## Readonly<T>

Makes all properties readonly:

```typescript
interface Mutable {
  value: number;
}

type Immutable = Readonly<Mutable>;
// value is now readonly

const obj: Immutable = { value: 42 };
// obj.value = 100;  // Error! Cannot assign to readonly property
```

## Pick<T, K>

Select specific properties:

```typescript
interface User {
  name: string;
  age: number;
  email: string;
  password: string;
}

type PublicUser = Pick<User, "name" | "age" | "email">;
// Only has: name, age, email (no password)
```

## Omit<T, K>

Exclude specific properties:

```typescript
interface User {
  name: string;
  age: number;
  email: string;
  password: string;
}

type PublicUser = Omit<User, "password">;
// Has all properties except password
```

## Record<K, T>

Create object type with specific keys and value type:

```typescript
type UserRoles = Record<string, boolean>;
// Equivalent to: { [key: string]: boolean }

const roles: UserRoles = {
  admin: true,
  user: false,
  guest: false,
};

// With specific keys
type Status = "active" | "inactive" | "pending";
type StatusMap = Record<Status, number>;

const statusCounts: StatusMap = {
  active: 10,
  inactive: 5,
  pending: 2,
};
```

## Combining Utility Types

```typescript
interface User {
  name: string;
  age: number;
  email: string;
}

// Partial and Pick combined
type PartialName = Partial<Pick<User, "name">>;

// Readonly and Omit combined
type ReadonlyUser = Readonly<Omit<User, "password">>;
```

# Common Mistakes

- **Overusing utility types**: Sometimes a simple interface is clearer
- **Not understanding what they do**: Each utility has a specific purpose
- **Complex combinations**: Can become hard to read
- **Using when not needed**: Don't use utilities just because you can

# Practice Exercises

1. Create a type that makes all properties of an interface optional.
2. Create a type that picks only specific properties from an interface.
3. Create a type that omits sensitive properties (like password) from a user object.
4. Use Record to create a type mapping status codes to messages.
5. Combine utility types to create a readonly version of a partial type.

Example solution for exercise 2:

```typescript
interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
}

type ProductSummary = Pick<Product, "id" | "name" | "price">;

const summary: ProductSummary = {
  id: 1,
  name: "Widget",
  price: 19.99,
  // description not included
};
```

# Key Takeaways

- Utility types transform existing types
- `Partial<T>` makes all properties optional
- `Required<T>` makes all properties required
- `Readonly<T>` makes all properties readonly
- `Pick<T, K>` selects specific properties
- `Omit<T, K>` excludes specific properties
- `Record<K, T>` creates object types with specific structure
- Utility types can be combined for complex transformations

# Related Topics

- Generics Introduction (TypeScript Intermediate #7)
- Interfaces (TypeScript Intermediate #1)
- Advanced Types (TypeScript Advanced #2)
