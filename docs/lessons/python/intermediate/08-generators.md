---
title: "Generators"
language: python
difficulty: intermediate
prerequisites: ["Functions", "List Comprehensions"]
keywords: [generators, yield, iterator, memory efficient, lazy evaluation, generator expressions]
---

# Learning Objectives

- Understand what generators are and why they're useful
- Create generator functions using `yield`
- Use generator expressions
- Understand the difference between generators and lists
- Work with infinite sequences
- Understand memory efficiency of generators

# Prerequisites

- Functions
- List Comprehensions

# Introduction

Generators are a special type of iterator that generate values on-the-fly rather than storing them all in memory. They're memory-efficient and perfect for working with large datasets or infinite sequences. Understanding generators is essential for writing efficient Python code.

# Core Concepts

## Generator Functions

Functions that use `yield` instead of `return`:

```python
def count_up_to(max):
    count = 1
    while count <= max:
        yield count  # Yields value and pauses
        count += 1

# Create generator
counter = count_up_to(5)

# Use generator
for num in counter:
    print(num)
# Output: 1, 2, 3, 4, 5
```

## How Generators Work

Generators pause execution at `yield` and resume when next value is requested:

```python
def simple_generator():
    print("Start")
    yield 1
    print("Middle")
    yield 2
    print("End")
    yield 3

gen = simple_generator()
print(next(gen))  # Output: Start, then 1
print(next(gen))  # Output: Middle, then 2
print(next(gen))  # Output: End, then 3
```

## Generator Expressions

Similar to list comprehensions, but create generators:

```python
# List comprehension (creates list in memory)
squares_list = [x ** 2 for x in range(5)]
print(squares_list)  # Output: [0, 1, 4, 9, 16]

# Generator expression (creates generator)
squares_gen = (x ** 2 for x in range(5))
print(list(squares_gen))  # Output: [0, 1, 4, 9, 16]
# Or iterate directly:
for square in (x ** 2 for x in range(5)):
    print(square)
```

## Memory Efficiency

Generators are memory-efficient because they generate values on demand:

```python
# This would use a lot of memory
def squares_list(n):
    return [x ** 2 for x in range(n)]  # Creates entire list

# This uses minimal memory
def squares_generator(n):
    for x in range(n):
        yield x ** 2  # Generates one at a time

# Compare
import sys
list_memory = sys.getsizeof(squares_list(1000))
gen_memory = sys.getsizeof(squares_generator(1000))
print(f"List: {list_memory} bytes, Generator: {gen_memory} bytes")
```

## Infinite Sequences

Generators can represent infinite sequences:

```python
def infinite_counter():
    count = 0
    while True:
        yield count
        count += 1

counter = infinite_counter()
print(next(counter))  # 0
print(next(counter))  # 1
print(next(counter))  # 2
# Can continue forever...
```

## Practical Example: Reading Large Files

```python
def read_large_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip()  # Process one line at a time

# Memory efficient - doesn't load entire file
for line in read_large_file("huge_file.txt"):
    process(line)  # Process each line
```

## Generator Pipeline

Chain generators together:

```python
def numbers():
    for i in range(10):
        yield i

def squares(nums):
    for num in nums:
        yield num ** 2

def evens(nums):
    for num in nums:
        if num % 2 == 0:
            yield num

# Chain generators
pipeline = evens(squares(numbers()))
print(list(pipeline))  # Output: [0, 4, 16, 36, 64]
```

## Sending Values to Generators

You can send values back to generators:

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)  # Start generator
print(acc.send(10))  # Output: 10
print(acc.send(5))   # Output: 15
print(acc.send(3))   # Output: 18
```

# Common Mistakes

- **Trying to reuse exhausted generator**: Generators can only be iterated once
- **Not understanding lazy evaluation**: Values aren't generated until requested
- **Using when you need a list**: Sometimes you actually need a list, not a generator
- **Forgetting `next()` to start**: Some generators need to be started with `next()`
- **Confusing with list comprehensions**: Generators use `()`, lists use `[]`

# Practice Exercises

1. Create a generator that yields Fibonacci numbers.
2. Create a generator expression that yields squares of even numbers.
3. Write a generator that reads lines from a file one at a time.
4. Create a generator that yields prime numbers (infinite sequence).
5. Write a generator function that takes a list and yields elements in reverse.

Example solution for exercise 1:

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
for _ in range(10):
    print(next(fib))
# Output: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
```

# Key Takeaways

- Generators use `yield` instead of `return`
- Generators are memory-efficient - generate values on demand
- Generator expressions use `()` syntax: `(x**2 for x in range(5))`
- Generators can represent infinite sequences
- Generators are iterators - can only be iterated once
- Use generators for large datasets or when memory is a concern
- Generators enable lazy evaluation

# Related Topics

- Functions (Python Beginner #6)
- List Comprehensions (Python Intermediate #1)
- Iterators (covered in advanced topics)
