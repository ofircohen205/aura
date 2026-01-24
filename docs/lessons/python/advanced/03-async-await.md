---
title: "Async/Await and Asynchronous Programming"
language: python
difficulty: advanced
prerequisites: ["Generators", "Functions"]
keywords: [async, await, asyncio, coroutines, asynchronous, concurrency, event loop]
---

# Learning Objectives

- Understand asynchronous programming concepts
- Create async functions using `async def`
- Use `await` to wait for async operations
- Run async code with `asyncio`
- Understand the event loop
- Work with async context managers and iterators

# Prerequisites

- Generators
- Functions

# Introduction

Asynchronous programming allows your code to handle multiple operations concurrently without blocking. Python's `async/await` syntax makes it easier to write asynchronous code. Understanding async programming is essential for I/O-bound applications like web servers, APIs, and data processing.

# Core Concepts

## Async Functions

Define async functions with `async def`:

```python
import asyncio

async def greet():
    print("Hello")
    await asyncio.sleep(1)  # Simulate async operation
    print("World")

# Run async function
asyncio.run(greet())
```

## Await

Use `await` to wait for async operations:

```python
import asyncio

async def fetch_data():
    print("Fetching data...")
    await asyncio.sleep(2)  # Simulate network request
    return "Data received"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

## Running Multiple Tasks Concurrently

```python
import asyncio

async def task(name, delay):
    print(f"Task {name} starting")
    await asyncio.sleep(delay)
    print(f"Task {name} completed")
    return f"Result from {name}"

async def main():
    # Run tasks concurrently
    results = await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )
    print(results)

asyncio.run(main())
# Tasks run concurrently, not sequentially
```

## Creating Tasks

Create tasks to run coroutines concurrently:

```python
import asyncio

async def background_task():
    for i in range(5):
        print(f"Background: {i}")
        await asyncio.sleep(1)

async def main():
    # Create task (starts running)
    task = asyncio.create_task(background_task())

    # Do other work
    await asyncio.sleep(2)
    print("Main work done")

    # Wait for task to complete
    await task

asyncio.run(main())
```

## Async Context Managers

Use `async with` for async context managers:

```python
class AsyncFile:
    async def __aenter__(self):
        # Async setup
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Async cleanup
        await asyncio.sleep(0.1)

async def main():
    async with AsyncFile() as file:
        print("Using async file")

asyncio.run(main())
```

## Async Iterators

Iterate over async sequences:

```python
class AsyncCounter:
    def __init__(self, max):
        self.max = max
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.max:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.current += 1
        return self.current

async def main():
    async for num in AsyncCounter(5):
        print(num)

asyncio.run(main())
```

## Error Handling

Handle exceptions in async code:

```python
import asyncio

async def might_fail():
    await asyncio.sleep(1)
    raise ValueError("Something went wrong")

async def main():
    try:
        await might_fail()
    except ValueError as e:
        print(f"Caught error: {e}")

asyncio.run(main())
```

# Common Mistakes

- **Forgetting `await`**: Async functions must be awaited
- **Mixing sync and async incorrectly**: Can't use `await` in sync functions
- **Not using `asyncio.run()`**: Need event loop to run async code
- **Blocking the event loop**: Don't use blocking operations in async code
- **Not handling exceptions**: Async exceptions need to be caught with try/except

# Practice Exercises

1. Create an async function that simulates fetching data from multiple URLs concurrently.
2. Create an async function that processes a list of items with a delay between each.
3. Use `asyncio.gather()` to run multiple async operations and collect results.
4. Create an async context manager for resource management.
5. Write an async function that handles timeouts using `asyncio.wait_for()`.

Example solution for exercise 1:

```python
import asyncio

async def fetch_url(url, delay):
    print(f"Fetching {url}...")
    await asyncio.sleep(delay)
    return f"Data from {url}"

async def main():
    urls = [
        ("http://example.com", 2),
        ("http://test.com", 1),
        ("http://demo.com", 3)
    ]

    results = await asyncio.gather(
        *[fetch_url(url, delay) for url, delay in urls]
    )
    print(results)

asyncio.run(main())
```

# Key Takeaways

- Use `async def` to define async functions (coroutines)
- Use `await` to wait for async operations
- Use `asyncio.run()` to run async code
- Use `asyncio.gather()` to run multiple tasks concurrently
- Async code is great for I/O-bound operations
- Don't block the event loop with synchronous operations
- Async context managers use `async with`
- Async iterators use `async for`

# Related Topics

- Generators (Python Intermediate #8)
- Context Managers (Python Intermediate #9)
- Advanced Generators (Python Advanced #2)
