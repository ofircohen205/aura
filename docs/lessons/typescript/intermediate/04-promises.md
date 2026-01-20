---
title: "Promises"
language: typescript
difficulty: intermediate
prerequisites: ["Functions", "Error Handling Basics"]
keywords:
  [promises, async, then, catch, finally, Promise.all, Promise.race, asynchronous programming]
---

# Learning Objectives

- Understand what promises are and why they're useful
- Create and use promises
- Handle promise resolution and rejection
- Chain promises together
- Use Promise.all() and Promise.race()
- Convert callback-based code to promises

# Prerequisites

- Functions
- Error Handling Basics

# Introduction

Promises represent the eventual completion (or failure) of an asynchronous operation. They're essential for handling asynchronous code in JavaScript/TypeScript. Understanding promises is crucial before learning async/await, and they're still widely used in modern TypeScript applications.

# Core Concepts

## Creating Promises

```typescript
// Create a promise
const promise = new Promise<string>((resolve, reject) => {
  // Async operation
  setTimeout(() => {
    resolve("Success!");
  }, 1000);
});
```

## Using Promises

### then() and catch()

```typescript
function fetchData(): Promise<string> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve("Data received");
    }, 1000);
  });
}

fetchData()
  .then(data => {
    console.log(data); // Output: Data received
  })
  .catch(error => {
    console.error(error);
  });
```

## Chaining Promises

```typescript
function step1(): Promise<number> {
  return Promise.resolve(10);
}

function step2(value: number): Promise<number> {
  return Promise.resolve(value * 2);
}

function step3(value: number): Promise<string> {
  return Promise.resolve(`Result: ${value}`);
}

step1()
  .then(step2)
  .then(step3)
  .then(result => console.log(result)) // Output: Result: 20
  .catch(error => console.error(error));
```

## Error Handling

```typescript
function mightFail(): Promise<string> {
  return new Promise((resolve, reject) => {
    const success = Math.random() > 0.5;
    if (success) {
      resolve("Success!");
    } else {
      reject(new Error("Something went wrong"));
    }
  });
}

mightFail()
  .then(result => console.log(result))
  .catch(error => console.error(error.message));
```

## Promise.all()

Wait for all promises to resolve:

```typescript
const promise1 = Promise.resolve(1);
const promise2 = Promise.resolve(2);
const promise3 = Promise.resolve(3);

Promise.all([promise1, promise2, promise3])
  .then(values => {
    console.log(values); // Output: [1, 2, 3]
  })
  .catch(error => {
    // If any promise rejects, this catches it
    console.error(error);
  });
```

## Promise.race()

Get result of first settled promise:

```typescript
const fast = new Promise(resolve => setTimeout(() => resolve("Fast"), 100));
const slow = new Promise(resolve => setTimeout(() => resolve("Slow"), 500));

Promise.race([fast, slow]).then(result => {
  console.log(result); // Output: Fast (wins the race)
});
```

## Promise.allSettled()

Wait for all promises to settle (resolve or reject):

```typescript
const promises = [
  Promise.resolve("Success"),
  Promise.reject("Error"),
  Promise.resolve("Another success"),
];

Promise.allSettled(promises).then(results => {
  results.forEach((result, index) => {
    if (result.status === "fulfilled") {
      console.log(`Promise ${index}: ${result.value}`);
    } else {
      console.log(`Promise ${index}: ${result.reason}`);
    }
  });
});
```

## Converting Callbacks to Promises

```typescript
function readFile(path: string, callback: (error: Error | null, data?: string) => void) {
  // Simulated file read
  setTimeout(() => {
    callback(null, "File content");
  }, 1000);
}

// Convert to promise
function readFilePromise(path: string): Promise<string> {
  return new Promise((resolve, reject) => {
    readFile(path, (error, data) => {
      if (error) {
        reject(error);
      } else {
        resolve(data!);
      }
    });
  });
}

readFilePromise("file.txt")
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

# Common Mistakes

- **Forgetting to return promises in chains**: Must return to chain properly
- **Not handling errors**: Always use `.catch()` or try/catch with async/await
- **Promise constructor anti-pattern**: Don't wrap promises unnecessarily
- **Not understanding Promise.all()**: Fails fast if any promise rejects
- **Mixing callbacks and promises**: Be consistent with async patterns

# Practice Exercises

1. Create a promise that resolves after a delay and use it.
2. Chain multiple promises together to process data sequentially.
3. Use Promise.all() to fetch data from multiple sources concurrently.
4. Create a function that converts a callback-based API to promises.
5. Use Promise.race() to implement a timeout pattern.

Example solution for exercise 1:

```typescript
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

delay(1000).then(() => {
  console.log("1 second has passed");
});
```

# Key Takeaways

- Promises represent asynchronous operations
- Use `.then()` for success, `.catch()` for errors
- Promises can be chained together
- `Promise.all()` waits for all promises
- `Promise.race()` gets first settled promise
- `Promise.allSettled()` waits for all to complete (success or failure)
- Always handle promise rejections
- Promises are the foundation for async/await

# Related Topics

- Functions (TypeScript Beginner #2)
- Async/Await (next lesson)
- Error Handling (covered in this lesson)
