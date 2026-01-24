---
title: "Decorators"
language: typescript
difficulty: advanced
prerequisites: ["Classes", "Functions"]
keywords:
  [decorators, metadata, class decorators, method decorators, property decorators, experimental]
---

# Learning Objectives

- Understand TypeScript decorators
- Create class decorators
- Create method and property decorators
- Use parameter decorators
- Understand decorator factories
- Work with decorator metadata

# Prerequisites

- Classes
- Functions

# Introduction

Decorators are a TypeScript feature (currently experimental) that allows you to add metadata and modify classes, methods, and properties. They're widely used in frameworks like Angular and NestJS. Understanding decorators helps you work with these frameworks and create powerful abstractions.

# Core Concepts

## Enabling Decorators

Enable in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
```

## Class Decorators

Modify or replace class definitions:

```typescript
function sealed(constructor: Function) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }
}
```

## Method Decorators

Modify method behavior:

```typescript
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    const result = originalMethod.apply(this, args);
    console.log(`${propertyKey} returned`, result);
    return result;
  };

  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}
```

## Property Decorators

Modify properties:

```typescript
function readonly(target: any, propertyKey: string) {
  Object.defineProperty(target, propertyKey, {
    writable: false,
  });
}

class User {
  @readonly
  name: string = "Alice";
}

const user = new User();
// user.name = "Bob";  // Error in strict mode
```

## Decorator Factories

Decorators that accept parameters:

```typescript
function log(prefix: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    descriptor.value = function (...args: any[]) {
      console.log(`[${prefix}] Calling ${propertyKey}`);
      return originalMethod.apply(this, args);
    };
    return descriptor;
  };
}

class Service {
  @log("API")
  fetchData() {
    return "data";
  }
}
```

## Parameter Decorators

```typescript
function required(target: any, propertyKey: string, parameterIndex: number) {
  // Store metadata about required parameters
}

class UserService {
  getUser(@required id: number) {
    return { id, name: "Alice" };
  }
}
```

## Multiple Decorators

```typescript
@sealed
@frozen
class Example {
  @log
  @cache
  method() {
    return "result";
  }
}
```

# Common Mistakes

- **Not enabling experimental decorators**: Must enable in tsconfig.json
- **Decorator execution order**: Bottom-to-top, then top-to-bottom for factories
- **Losing `this` context**: Use arrow functions or `.apply()`
- **Overusing decorators**: Can make code harder to understand

# Practice Exercises

1. Create a class decorator that adds a timestamp property.
2. Create a method decorator that measures execution time.
3. Create a property decorator that validates values.
4. Create a decorator factory that logs with different log levels.
5. Combine multiple decorators on a class method.

Example solution for exercise 2:

```typescript
function timer(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  descriptor.value = function (...args: any[]) {
    const start = performance.now();
    const result = originalMethod.apply(this, args);
    const end = performance.now();
    console.log(`${propertyKey} took ${end - start}ms`);
    return result;
  };
  return descriptor;
}

class Service {
  @timer
  processData() {
    // Some processing
    return "done";
  }
}
```

# Key Takeaways

- Decorators modify classes, methods, and properties
- Enable with `experimentalDecorators` in tsconfig.json
- Class decorators receive constructor
- Method decorators receive target, propertyKey, descriptor
- Property decorators receive target, propertyKey
- Decorator factories accept parameters
- Decorators execute in specific order
- Used extensively in frameworks like Angular

# Related Topics

- Classes (TypeScript Intermediate #2)
- Functions (TypeScript Beginner #2)
- Metadata (advanced topic)
