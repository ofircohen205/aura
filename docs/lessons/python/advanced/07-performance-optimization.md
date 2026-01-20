---
title: "Performance Optimization"
language: python
difficulty: advanced
prerequisites: ["Functions", "Generators", "Data Structures"]
keywords: [performance, optimization, profiling, cProfile, timeit, memory, efficiency, bottlenecks]
---

# Learning Objectives

- Profile code to identify bottlenecks
- Use appropriate data structures for performance
- Optimize loops and iterations
- Understand when to optimize
- Use caching and memoization
- Optimize memory usage

# Prerequisites

- Functions
- Generators
- Data Structures

# Introduction

Performance optimization is about making code run faster and use less memory. However, premature optimization is often wasteful. The key is to measure first, identify bottlenecks, then optimize. Understanding performance optimization helps you write efficient code when it matters.

# Core Concepts

## Measure First

Always profile before optimizing:

```python
import time

def slow_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

# Time it
start = time.time()
result = slow_function()
elapsed = time.time() - start
print(f"Took {elapsed:.4f} seconds")
```

## Using timeit

More accurate timing:

```python
import timeit

code = """
total = 0
for i in range(1000):
    total += i
"""

time_taken = timeit.timeit(code, number=1000)
print(f"Average time: {time_taken/1000:.6f} seconds")
```

## Using cProfile

Profile to find bottlenecks:

```python
import cProfile

def my_function():
    # Your code here
    pass

cProfile.run('my_function()')
```

## Choose Right Data Structures

```python
# List lookup: O(n)
items = [1, 2, 3, 4, 5]
if 5 in items:  # Slow for large lists
    pass

# Set lookup: O(1)
items_set = {1, 2, 3, 4, 5}
if 5 in items_set:  # Fast!
    pass

# Dictionary lookup: O(1)
data = {"a": 1, "b": 2}
value = data.get("a")  # Fast!
```

## Optimize Loops

```python
# Slow: repeated function calls
result = []
for item in items:
    result.append(process(item))

# Faster: list comprehension
result = [process(item) for item in items]

# Even faster: generator if you don't need all at once
result = (process(item) for item in items)
```

## Caching and Memoization

Cache expensive computations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# First call computes, subsequent calls use cache
print(fibonacci(100))  # Fast due to caching
```

## Avoid Unnecessary Operations

```python
# Slow: creating new list each time
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result

# Faster: use generator or list comprehension
def process_data(data):
    return [item * 2 for item in data]
```

## String Concatenation

```python
# Slow: creates new string each time
result = ""
for word in words:
    result += word  # Creates new string!

# Fast: use join
result = "".join(words)
```

## Use Built-in Functions

Built-ins are often faster:

```python
# Slow: manual loop
total = 0
for num in numbers:
    total += num

# Fast: built-in
total = sum(numbers)
```

# Common Mistakes

- **Premature optimization**: Optimize only after profiling
- **Micro-optimizations**: Focus on big bottlenecks, not small details
- **Sacrificing readability**: Don't make code unreadable for small gains
- **Not measuring**: Always measure before and after optimization
- **Wrong data structures**: Using list when set/dict would be better

# Practice Exercises

1. Profile a function and identify the slowest part.
2. Optimize a function that processes a large list.
3. Use caching to speed up a recursive function.
4. Compare performance of different data structures for lookups.
5. Optimize string operations in a function.

Example solution for exercise 3:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def expensive_calculation(n):
    if n <= 1:
        return n
    return expensive_calculation(n-1) + expensive_calculation(n-2)

# Much faster with caching
result = expensive_calculation(30)
```

# Key Takeaways

- Always measure before optimizing
- Use `timeit` and `cProfile` to profile code
- Choose appropriate data structures (set/dict for lookups)
- Use list comprehensions and generators
- Cache expensive computations with `@lru_cache`
- Use built-in functions when possible
- Optimize bottlenecks, not everything
- Don't sacrifice readability for small performance gains

# Related Topics

- Functions (Python Beginner #6)
- Generators (Python Intermediate #8)
- Data Structures (covered in beginner/intermediate lessons)
