---
title: "Mapped Types"
language: typescript
difficulty: advanced
prerequisites: ["Advanced Types", "Utility Types Introduction"]
keywords:
  [mapped types, type transformation, key remapping, template literal types, type manipulation]
---

# Learning Objectives

- Create custom mapped types
- Transform object properties with mapped types
- Use key remapping
- Combine mapped types with template literals
- Understand mapped type modifiers
- Create complex type transformations

# Prerequisites

- Advanced Types
- Utility Types Introduction

# Introduction

Mapped types allow you to create new types by transforming properties of existing types. They're the foundation of many utility types and enable powerful type transformations. Understanding mapped types helps you create reusable type utilities and maintain type safety across transformations.

# Core Concepts

## Basic Mapped Types

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

## Modifiers

Add or remove modifiers:

```typescript
// Remove readonly
type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};

// Remove optional
type Required<T> = {
  [P in keyof T]-?: T[P];
};

// Add readonly
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};
```

## Key Remapping

Transform keys:

```typescript
type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

interface User {
  name: string;
  age: number;
}

type UserGetters = Getters<User>;
// {
//     getName: () => string;
//     getAge: () => number;
// }
```

## Filtering Keys

```typescript
type NonFunctionPropertyNames<T> = {
  [K in keyof T]: T[K] extends Function ? never : K;
}[keyof T];

type NonFunctionProperties<T> = {
  [K in NonFunctionPropertyNames<T>]: T[K];
};

interface User {
  name: string;
  age: number;
  greet(): void;
}

type Props = NonFunctionProperties<User>;
// { name: string; age: number; }
```

## Template Literal Types in Mapped Types

```typescript
type EventHandlers<T> = {
  [K in keyof T as `on${Capitalize<string & K>}`]: (event: T[K]) => void;
};

type Events = {
  click: MouseEvent;
  change: Event;
};

type Handlers = EventHandlers<Events>;
// {
//     onClick: (event: MouseEvent) => void;
//     onChange: (event: Event) => void;
// }
```

## Deep Mapped Types

```typescript
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

interface Nested {
  user: {
    name: string;
    age: number;
  };
}

type ReadonlyNested = DeepReadonly<Nested>;
// All properties are deeply readonly
```

# Common Mistakes

- **Over-complicating**: Keep mapped types readable
- **Not understanding modifiers**: `-?` removes optional, `-readonly` removes readonly
- **Circular references**: Can cause infinite recursion
- **Performance**: Complex mapped types slow compilation

# Practice Exercises

1. Create a mapped type that makes all properties nullable.
2. Create a mapped type that prefixes all keys with a string.
3. Create a mapped type that extracts only string properties.
4. Create a deep partial type (makes nested properties optional).
5. Create a mapped type that creates setters from properties.

Example solution for exercise 1:

```typescript
type Nullable<T> = {
  [P in keyof T]: T[P] | null;
};

interface User {
  name: string;
  age: number;
}

type NullableUser = Nullable<User>;
// { name: string | null; age: number | null; }
```

# Key Takeaways

- Mapped types transform object properties
- Use `[P in keyof T]` to iterate over properties
- Modifiers: `?`, `readonly`, `-?`, `-readonly`
- Key remapping with `as` clause
- Can filter keys with conditional types
- Template literals enable key transformation
- Can be nested for deep transformations

# Related Topics

- Advanced Types (TypeScript Advanced #2)
- Utility Types Introduction (TypeScript Intermediate #8)
- Conditional Types (TypeScript Advanced #4)
