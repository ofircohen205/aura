---
title: "Async/Await"
language: typescript
difficulty: intermediate
prerequisites: ["Promises", "Functions"]
keywords: [async, await, asynchronous, promises, error handling, concurrent execution]
---

# Learning Objectives

- Use `async` and `await` for asynchronous code
- Handle errors with try/catch in async functions
- Run multiple async operations concurrently
- Understand the relationship between async/await and promises
- Avoid common async/await pitfalls

# Prerequisites

- Promises
- Functions

# Introduction

`async/await` is syntactic sugar over promises that makes asynchronous code look and behave more like synchronous code. It's the modern, preferred way to handle asynchronous operations in TypeScript. Understanding async/await makes asynchronous programming much more intuitive.

# Core Concepts

## Async Functions

Functions marked with `async` return promises:

```typescript
async function fetchData(): Promise<string> {
  return "Data"; // Automatically wrapped in Promise
}

// Equivalent to:
function fetchData(): Promise<string> {
  return Promise.resolve("Data");
}
```

## Await

Use `await` to wait for a promise to resolve:

```typescript
async function getData() {
  const data = await fetchData(); // Waits for promise
  console.log(data); // "Data"
}
```

## Error Handling

Use try/catch with async/await:

```typescript
async function mightFail() {
  try {
    const data = await fetchData();
    return data;
  } catch (error) {
    console.error("Error:", error);
    throw error; // Re-throw if needed
  }
}
```

## Sequential Execution

```typescript
async function processSequentially() {
  const step1 = await doStep1(); // Waits for step1
  const step2 = await doStep2(step1); // Then does step2
  const step3 = await doStep3(step2); // Then does step3
  return step3;
}
```

## Concurrent Execution

Run multiple async operations in parallel:

```typescript
async function processConcurrently() {
  // All start at the same time
  const [result1, result2, result3] = await Promise.all([doStep1(), doStep2(), doStep3()]);

  return { result1, result2, result3 };
}
```

## Async Functions in Classes

```typescript
class DataService {
  async fetchUser(id: number): Promise<User> {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  }

  async fetchUsers(): Promise<User[]> {
    const response = await fetch("/api/users");
    return response.json();
  }
}

const service = new DataService();
const user = await service.fetchUser(1);
```

## Error Handling Patterns

```typescript
// Pattern 1: try/catch
async function withTryCatch() {
  try {
    const data = await fetchData();
    return data;
  } catch (error) {
    // Handle error
    return null;
  }
}

// Pattern 2: Return error as value
async function withErrorValue() {
  try {
    const data = await fetchData();
    return { data, error: null };
  } catch (error) {
    return { data: null, error };
  }
}
```

## Await in Loops

```typescript
// Sequential (one at a time)
async function processSequentially(items: string[]) {
  for (const item of items) {
    await processItem(item); // Waits for each
  }
}

// Concurrent (all at once)
async function processConcurrently(items: string[]) {
  await Promise.all(items.map(item => processItem(item)));
}
```

# Common Mistakes

- **Forgetting `await`**: Function returns Promise, not the value
- **Using `await` in non-async function**: Must be in `async` function
- **Sequential when concurrent would work**: Use `Promise.all()` for parallel operations
- **Not handling errors**: Always use try/catch or `.catch()`
- **Awaiting non-promises**: `await` works on promises, not regular values

# Practice Exercises

1. Convert a promise-based function to use async/await.
2. Create an async function that fetches data from multiple URLs concurrently.
3. Write an async function with proper error handling.
4. Create an async function that processes items in a loop (both sequential and concurrent versions).
5. Write an async class method that handles errors gracefully.

Example solution for exercise 2:

```typescript
async function fetchMultipleUrls(urls: string[]): Promise<string[]> {
  const promises = urls.map(url => fetch(url).then(r => r.text()));
  return Promise.all(promises);
}

const urls = ["http://example.com", "http://test.com"];
const results = await fetchMultipleUrls(urls);
console.log(results);
```

# Key Takeaways

- `async` functions return promises
- `await` waits for a promise to resolve
- Use try/catch for error handling in async functions
- Use `Promise.all()` for concurrent execution
- `await` can only be used in `async` functions
- Async/await makes asynchronous code more readable
- Don't forget `await` - it's easy to miss

# Related Topics

- Promises (TypeScript Intermediate #4)
- Error Handling (covered in this lesson)
- Functions (TypeScript Beginner #2)
