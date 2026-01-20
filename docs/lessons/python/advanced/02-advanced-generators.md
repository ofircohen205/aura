---
title: "Advanced Generators"
language: python
difficulty: advanced
prerequisites: ["Generators", "Decorators"]
keywords: [generators, yield from, coroutines, send, throw, close, generator pipelines]
---

# Learning Objectives

- Use `yield from` for generator delegation
- Send values into generators using `send()`
- Handle exceptions in generators with `throw()`
- Close generators properly with `close()`
- Build complex generator pipelines
- Understand generator coroutines

# Prerequisites

- Generators
- Decorators

# Introduction

While basic generators are powerful, advanced generator features enable even more sophisticated patterns. Understanding `yield from`, `send()`, and generator coroutines unlocks patterns for data processing, state machines, and cooperative multitasking.

# Core Concepts

## yield from

Delegates to another generator:

```python
def count_up_to(max):
    for i in range(1, max + 1):
        yield i

def count_twice(max):
    yield from count_up_to(max)  # Delegate to another generator
    yield from count_up_to(max)  # Delegate again

for num in count_twice(3):
    print(num)
# Output: 1, 2, 3, 1, 2, 3
```

## Sending Values to Generators

Use `send()` to send values into a generator:

```python
def accumulator():
    total = 0
    while True:
        value = yield total  # Receive value via yield
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)  # Start generator (prime it)
print(acc.send(10))  # Output: 10
print(acc.send(5))   # Output: 15
print(acc.send(3))   # Output: 18
```

## Generator throw()

Raise exceptions inside generators:

```python
def counter():
    count = 0
    while True:
        try:
            value = yield count
            if value is None:
                count += 1
            else:
                count = value
        except ValueError:
            count = 0
        except GeneratorExit:
            print("Generator closing")
            raise

gen = counter()
next(gen)
print(gen.send(None))  # 1
gen.throw(ValueError)  # Reset counter
print(gen.send(None))  # 1 (reset)
```

## Generator close()

Properly close generators:

```python
def file_reader(filename):
    try:
        with open(filename, 'r') as file:
            for line in file:
                yield line.strip()
    except GeneratorExit:
        print("Cleaning up file reader")
        raise

reader = file_reader("data.txt")
next(reader)
reader.close()  # Triggers GeneratorExit
```

## Generator Pipelines

Chain generators for data processing:

```python
def numbers():
    for i in range(10):
        yield i

def even_filter(nums):
    for num in nums:
        if num % 2 == 0:
            yield num

def square(nums):
    for num in nums:
        yield num ** 2

# Chain generators
pipeline = square(even_filter(numbers()))
print(list(pipeline))  # Output: [0, 4, 16, 36, 64]
```

## Coroutines

Generators that consume values (coroutines):

```python
def grep(pattern):
    print(f"Looking for {pattern}")
    while True:
        line = yield
        if pattern in line:
            print(line)

g = grep("python")
next(g)  # Prime the coroutine
g.send("I love python")  # Output: I love python
g.send("Java is great")
g.send("python is awesome")  # Output: python is awesome
```

# Common Mistakes

- **Not priming generator**: Must call `next()` before using `send()`
- **Sending to non-started generator**: Generator must be started first
- **Forgetting to handle GeneratorExit**: Should clean up resources
- **Not understanding yield from**: It delegates, doesn't just call
- **Confusing generators and coroutines**: Generators produce, coroutines consume

# Practice Exercises

1. Create a generator that uses `yield from` to combine multiple generators.
2. Create a coroutine that accumulates values and can be reset.
3. Build a generator pipeline that filters, transforms, and aggregates data.
4. Create a generator that handles exceptions gracefully using `throw()`.
5. Implement a generator that can be closed cleanly with proper cleanup.

Example solution for exercise 2:

```python
def accumulator():
    total = 0
    while True:
        try:
            value = yield total
            if value == "reset":
                total = 0
            elif value is not None:
                total += value
        except ValueError:
            total = 0

acc = accumulator()
next(acc)
print(acc.send(10))  # 10
print(acc.send(5))   # 15
print(acc.send("reset"))  # 0
print(acc.send(3))   # 3
```

# Key Takeaways

- `yield from` delegates to another generator
- `send()` sends values into generators (coroutines)
- `throw()` raises exceptions inside generators
- `close()` properly closes generators
- Generators can be chained into pipelines
- Coroutines are generators that consume values
- Always prime generators with `next()` before using `send()`

# Related Topics

- Generators (Python Intermediate #8)
- Decorators (Python Advanced #1)
- Async/Await (Python Advanced #3)
