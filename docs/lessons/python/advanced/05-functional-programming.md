---
title: "Functional Programming Concepts"
language: python
difficulty: advanced
prerequisites: ["Functions", "List Comprehensions", "Generators"]
keywords:
  [functional programming, map, filter, reduce, lambda, higher-order functions, immutability]
---

# Learning Objectives

- Understand functional programming concepts
- Use `map()`, `filter()`, and `reduce()`
- Write lambda functions
- Understand higher-order functions
- Work with immutable data structures
- Apply functional patterns in Python

# Prerequisites

- Functions
- List Comprehensions
- Generators

# Introduction

Functional programming is a programming paradigm that treats computation as the evaluation of mathematical functions. While Python isn't purely functional, it supports many functional programming concepts. Understanding these concepts helps you write more concise, expressive, and maintainable code.

# Core Concepts

## Lambda Functions

Anonymous functions defined with `lambda`:

```python
# Regular function
def square(x):
    return x ** 2

# Lambda function (equivalent)
square = lambda x: x ** 2

# Use lambda directly
result = (lambda x: x ** 2)(5)
print(result)  # Output: 25

# Common use: as arguments
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # Output: [1, 4, 9, 16, 25]
```

## map()

Apply a function to every item in an iterable:

```python
# Using map
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # Output: [1, 4, 9, 16, 25]

# Using list comprehension (often preferred)
squared = [x ** 2 for x in numbers]

# map with multiple iterables
list1 = [1, 2, 3]
list2 = [4, 5, 6]
sums = list(map(lambda x, y: x + y, list1, list2))
print(sums)  # Output: [5, 7, 9]
```

## filter()

Keep items that meet a condition:

```python
# Using filter
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # Output: [2, 4, 6, 8, 10]

# Using list comprehension (often preferred)
evens = [x for x in numbers if x % 2 == 0]
```

## reduce()

Combine items into a single value (requires `functools`):

```python
from functools import reduce

# Sum of numbers
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda x, y: x + y, numbers)
print(total)  # Output: 15

# Find maximum
maximum = reduce(lambda x, y: x if x > y else y, numbers)
print(maximum)  # Output: 5

# Often, built-in functions are clearer
total = sum(numbers)  # Better than reduce
maximum = max(numbers)  # Better than reduce
```

## Higher-Order Functions

Functions that take or return other functions:

```python
def apply_operation(func, a, b):
    return func(a, b)

def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

result1 = apply_operation(add, 5, 3)  # Output: 8
result2 = apply_operation(multiply, 5, 3)  # Output: 15
```

## Function Composition

Combine functions:

```python
def compose(f, g):
    return lambda x: f(g(x))

def add_one(x):
    return x + 1

def multiply_two(x):
    return x * 2

# Compose: multiply_two then add_one
composed = compose(add_one, multiply_two)
result = composed(5)  # (5 * 2) + 1 = 11
print(result)  # Output: 11
```

## Partial Functions

Create functions with some arguments pre-filled:

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

# Create square function (exponent fixed at 2)
square = partial(power, exponent=2)
print(square(5))  # Output: 25

# Create cube function
cube = partial(power, exponent=3)
print(cube(3))  # Output: 27
```

## Immutability

Prefer immutable data structures:

```python
# Immutable: tuples, strings, frozensets
point = (10, 20)  # Can't modify
name = "Alice"    # Can't modify

# For mutable structures, create new ones instead of modifying
numbers = [1, 2, 3]
new_numbers = numbers + [4]  # New list, original unchanged
```

## Functional Patterns

```python
# Pipeline pattern
def pipeline(data, *functions):
    result = data
    for func in functions:
        result = func(result)
    return result

numbers = [1, 2, 3, 4, 5]
result = pipeline(
    numbers,
    lambda x: [n ** 2 for n in x],  # Square
    lambda x: [n for n in x if n % 2 == 0],  # Filter evens
    sum  # Sum
)
print(result)  # Output: 20 (4 + 16)
```

# Common Mistakes

- **Overusing lambda**: Sometimes a named function is clearer
- **Using reduce when simpler alternatives exist**: `sum()` is clearer than `reduce(add, ...)`
- **Not understanding immutability**: Functional style prefers immutable data
- **Mixing paradigms**: Be consistent - don't mix functional and imperative randomly
- **Performance concerns**: Functional code can be slower for some operations

# Practice Exercises

1. Use `map()` to convert a list of temperatures from Celsius to Fahrenheit.
2. Use `filter()` to get all words longer than 5 characters from a list.
3. Use `reduce()` to find the product of all numbers in a list.
4. Create a higher-order function that applies a function to each element of a list.
5. Write a function composition that applies multiple transformations in sequence.

Example solution for exercise 1:

```python
celsius = [0, 10, 20, 30, 40]
fahrenheit = list(map(lambda c: (c * 9/5) + 32, celsius))
print(fahrenheit)  # Output: [32.0, 50.0, 68.0, 86.0, 104.0]
```

# Key Takeaways

- Lambda functions create anonymous functions
- `map()` applies a function to every item
- `filter()` keeps items that meet a condition
- `reduce()` combines items into a single value
- Higher-order functions take or return functions
- Functional programming emphasizes immutability
- List comprehensions are often preferred over `map()`/`filter()`
- Functional patterns can make code more expressive

# Related Topics

- Functions (Python Beginner #6)
- List Comprehensions (Python Intermediate #1)
- Generators (Python Intermediate #8)
