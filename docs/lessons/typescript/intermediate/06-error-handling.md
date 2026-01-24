---
title: "Error Handling"
language: typescript
difficulty: intermediate
prerequisites: ["Functions", "Promises", "Async/Await"]
keywords: [error handling, try, catch, throw, custom errors, error types, exception handling]
---

# Learning Objectives

- Handle errors effectively in TypeScript
- Create custom error classes
- Handle errors in async code
- Understand error types and narrowing
- Use error boundaries and error handling patterns
- Distinguish between different error types

# Prerequisites

- Functions
- Promises
- Async/Await

# Introduction

Robust error handling is essential for building reliable applications. TypeScript's type system helps catch errors at compile time, but runtime errors still need proper handling. Understanding error handling patterns helps you write more resilient code.

# Core Concepts

## Basic Error Handling

```typescript
try {
  // Code that might throw
  const result = riskyOperation();
} catch (error) {
  // Handle error
  console.error("An error occurred:", error);
}
```

## Type-Safe Error Handling

TypeScript helps with error types:

```typescript
try {
  // Some operation
} catch (error) {
  if (error instanceof Error) {
    console.error(error.message);
  } else {
    console.error("Unknown error:", error);
  }
}
```

## Custom Error Classes

Create specific error types:

```typescript
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

class NotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NotFoundError";
  }
}

function validateUser(name: string) {
  if (!name) {
    throw new ValidationError("Name is required", "name");
  }
}

try {
  validateUser("");
} catch (error) {
  if (error instanceof ValidationError) {
    console.error(`Validation error in ${error.field}: ${error.message}`);
  }
}
```

## Error Handling in Async Code

```typescript
async function fetchData() {
  try {
    const response = await fetch("/api/data");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      console.error("Fetch error:", error.message);
    }
    throw error; // Re-throw if needed
  }
}
```

## Result Pattern

Return success/error instead of throwing:

```typescript
type Result<T, E = Error> = { success: true; data: T } | { success: false; error: E };

function divide(a: number, b: number): Result<number> {
  if (b === 0) {
    return { success: false, error: new Error("Division by zero") };
  }
  return { success: true, data: a / b };
}

const result = divide(10, 2);
if (result.success) {
  console.log(result.data); // TypeScript knows data exists
} else {
  console.error(result.error);
}
```

## Error Boundaries

Handle errors at component level:

```typescript
class ErrorBoundary {
  private error: Error | null = null;

  execute<T>(fn: () => T): T | null {
    try {
      return fn();
    } catch (error) {
      this.error = error instanceof Error ? error : new Error(String(error));
      return null;
    }
  }

  getError(): Error | null {
    return this.error;
  }
}
```

## Multiple Error Types

```typescript
try {
  // Code that might throw different errors
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle validation error
  } else if (error instanceof NotFoundError) {
    // Handle not found error
  } else if (error instanceof Error) {
    // Handle generic error
  } else {
    // Handle unknown error
  }
}
```

# Common Mistakes

- **Catching too broadly**: Catch specific errors when possible
- **Swallowing errors**: At least log errors, don't silently ignore
- **Not re-throwing when needed**: Sometimes you need to propagate errors
- **Not checking error types**: Use `instanceof` to narrow error types
- **Forgetting error handling in async**: Use try/catch with await

# Practice Exercises

1. Create a custom error class and use it in a validation function.
2. Write an async function with comprehensive error handling.
3. Implement a Result type pattern for a function that might fail.
4. Create an error handler that distinguishes between different error types.
5. Write a function that safely parses JSON with proper error handling.

Example solution for exercise 1:

```typescript
class InvalidInputError extends Error {
  constructor(
    message: string,
    public input: string
  ) {
    super(message);
    this.name = "InvalidInputError";
  }
}

function validateEmail(email: string): void {
  if (!email.includes("@")) {
    throw new InvalidInputError("Invalid email format", email);
  }
}

try {
  validateEmail("invalid-email");
} catch (error) {
  if (error instanceof InvalidInputError) {
    console.error(`Invalid input "${error.input}": ${error.message}`);
  }
}
```

# Key Takeaways

- Use try/catch for error handling
- Create custom error classes for specific error types
- Use `instanceof` to check error types
- Handle errors in async code with try/catch
- Consider Result pattern as alternative to exceptions
- Don't swallow errors - always handle or log them
- TypeScript helps with error type narrowing

# Related Topics

- Functions (TypeScript Beginner #2)
- Promises (TypeScript Intermediate #4)
- Async/Await (TypeScript Intermediate #5)
