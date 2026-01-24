---
title: "Advanced Patterns"
language: typescript
difficulty: advanced
prerequisites: ["All previous TypeScript lessons"]
keywords:
  [
    patterns,
    advanced patterns,
    type-safe patterns,
    builder pattern,
    repository pattern,
    advanced techniques,
  ]
---

# Learning Objectives

- Implement advanced TypeScript patterns
- Create type-safe builder patterns
- Implement repository patterns with generics
- Use advanced type patterns
- Understand when to use advanced patterns
- Combine multiple advanced features

# Prerequisites

- All previous TypeScript lessons

# Introduction

Advanced TypeScript patterns combine multiple features to solve complex problems with type safety. Understanding these patterns helps you build robust, type-safe applications. However, use them when they add value - simplicity is often better.

# Core Concepts

## Type-Safe Builder Pattern

```typescript
class QueryBuilder<T> {
  private conditions: string[] = [];

  where<K extends keyof T>(field: K, operator: string, value: T[K]): this {
    this.conditions.push(`${String(field)} ${operator} ${value}`);
    return this;
  }

  build(): string {
    return this.conditions.join(" AND ");
  }
}

interface User {
  name: string;
  age: number;
}

const query = new QueryBuilder<User>().where("name", "=", "Alice").where("age", ">", 18).build();
```

## Repository Pattern with Generics

```typescript
interface Repository<T, ID = string> {
  findById(id: ID): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<T>;
  delete(id: ID): Promise<void>;
}

class UserRepository implements Repository<User, number> {
  async findById(id: number): Promise<User | null> {
    // Implementation
    return null;
  }

  async findAll(): Promise<User[]> {
    return [];
  }

  async save(user: User): Promise<User> {
    return user;
  }

  async delete(id: number): Promise<void> {
    // Implementation
  }
}
```

## Discriminated Union Patterns

```typescript
type Result<T, E = Error> = { success: true; data: T } | { success: false; error: E };

function divide(a: number, b: number): Result<number> {
  if (b === 0) {
    return { success: false, error: new Error("Division by zero") };
  }
  return { success: true, data: a / b };
}

function processResult(result: Result<number>) {
  if (result.success) {
    console.log(result.data); // TypeScript knows data exists
  } else {
    console.error(result.error);
  }
}
```

## Type-Safe Event System

```typescript
type EventMap = {
  click: MouseEvent;
  change: Event;
  submit: SubmitEvent;
};

class EventEmitter<T extends Record<string, any>> {
  private listeners: { [K in keyof T]?: Array<(event: T[K]) => void> } = {};

  on<K extends keyof T>(event: K, handler: (event: T[K]) => void): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event]!.push(handler);
  }

  emit<K extends keyof T>(event: K, data: T[K]): void {
    this.listeners[event]?.forEach(handler => handler(data));
  }
}

const emitter = new EventEmitter<EventMap>();
emitter.on("click", event => {
  // event is MouseEvent
});
```

# Common Mistakes

- **Over-engineering**: Simple solutions are often better
- **Too many type parameters**: Keep it manageable
- **Complex type gymnastics**: Prioritize readability
- **Not understanding trade-offs**: Advanced patterns have costs

# Practice Exercises

1. Create a type-safe builder for constructing API requests.
2. Implement a generic repository pattern for different entity types.
3. Create a type-safe event emitter with specific event types.
4. Implement a Result type pattern for error handling.
5. Create a type-safe configuration builder.

Example solution for exercise 2:

```typescript
interface Entity {
  id: number;
}

interface Repository<T extends Entity> {
  findById(id: number): Promise<T | null>;
  save(entity: T): Promise<T>;
}

class BaseRepository<T extends Entity> implements Repository<T> {
  async findById(id: number): Promise<T | null> {
    // Implementation
    return null;
  }

  async save(entity: T): Promise<T> {
    return entity;
  }
}

class UserRepository extends BaseRepository<User> {}
```

# Key Takeaways

- Advanced patterns combine multiple TypeScript features
- Builder patterns enable fluent, type-safe APIs
- Repository patterns provide data access abstraction
- Discriminated unions enable type-safe error handling
- Type-safe event systems prevent runtime errors
- Use patterns when they solve real problems
- Prioritize readability and maintainability

# Related Topics

- All previous TypeScript lessons
- Design Patterns Introduction (TypeScript Intermediate #9)
- Advanced Generics (TypeScript Advanced #1)
