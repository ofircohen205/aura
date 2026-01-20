---
title: "List Comprehensions"
language: python
difficulty: intermediate
prerequisites: ["Lists", "Loops", "Conditionals"]
keywords:
  [list comprehensions, functional programming, concise syntax, generators, filtering, mapping]
---

# Learning Objectives

- Understand what list comprehensions are and why they're useful
- Write list comprehensions for simple transformations
- Use conditional expressions in list comprehensions
- Create nested list comprehensions
- Understand when to use comprehensions vs loops

# Prerequisites

- Lists
- Loops
- Conditionals

# Introduction

List comprehensions provide a concise and readable way to create lists in Python. They're a more "Pythonic" alternative to using loops and conditionals to build lists. Once you understand them, they make your code more elegant and often more efficient.

# Core Concepts

## Basic List Comprehension

The basic syntax: `[expression for item in iterable]`

```python
# Traditional approach
squares = []
for x in range(5):
    squares.append(x ** 2)
print(squares)  # Output: [0, 1, 4, 9, 16]

# List comprehension (more concise)
squares = [x ** 2 for x in range(5)]
print(squares)  # Output: [0, 1, 4, 9, 16]
```

## List Comprehension with Conditionals

Add a condition to filter items: `[expression for item in iterable if condition]`

```python
# Get only even numbers
evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # Output: [0, 2, 4, 6, 8]

# Get squares of even numbers only
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
print(even_squares)  # Output: [0, 4, 16, 36, 64]
```

## Conditional Expressions

Use if-else in the expression: `[value_if_true if condition else value_if_false for item in iterable]`

```python
# Mark even numbers as "even", odd as "odd"
labels = ["even" if x % 2 == 0 else "odd" for x in range(5)]
print(labels)  # Output: ['even', 'odd', 'even', 'odd', 'even']
```

## Working with Strings

```python
# Convert to uppercase
words = ["hello", "world", "python"]
uppercase = [word.upper() for word in words]
print(uppercase)  # Output: ['HELLO', 'WORLD', 'PYTHON']

# Get word lengths
lengths = [len(word) for word in words]
print(lengths)  # Output: [5, 5, 6]

# Filter words by length
long_words = [word for word in words if len(word) > 5]
print(long_words)  # Output: ['python']
```

## Nested List Comprehensions

You can nest comprehensions:

```python
# Create a 3x3 matrix
matrix = [[i * j for j in range(3)] for i in range(3)]
print(matrix)
# Output: [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# Flatten a 2D list
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [num for row in matrix for num in row]
print(flattened)  # Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

## Dictionary Comprehensions

Similar syntax works for dictionaries:

```python
# Create dictionary of squares
squares_dict = {x: x ** 2 for x in range(5)}
print(squares_dict)  # Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Filter dictionary
numbers = {"a": 1, "b": 2, "c": 3, "d": 4}
evens = {k: v for k, v in numbers.items() if v % 2 == 0}
print(evens)  # Output: {'b': 2, 'd': 4}
```

## Set Comprehensions

Works for sets too:

```python
# Create set of squares
squares_set = {x ** 2 for x in range(5)}
print(squares_set)  # Output: {0, 1, 4, 9, 16}
```

# Common Mistakes

- **Over-complicating**: Sometimes a simple loop is clearer
- **Nested comprehensions that are hard to read**: Break into multiple lines or use loops
- **Forgetting the brackets**: `[x for x in range(5)]` not `x for x in range(5)`
- **Confusing order in nested comprehensions**: Read left to right, outer to inner
- **Using when a generator would be better**: For large data, consider generator expressions

# Practice Exercises

1. Create a list of squares for numbers 1-10.
2. Create a list of even numbers from 0-20.
3. Create a list that converts all strings in a list to their lengths.
4. Create a list that contains "even" or "odd" for numbers 0-9.
5. Create a flattened list from a 2D list using a comprehension.

Example solution for exercise 1:

```python
squares = [x ** 2 for x in range(1, 11)]
print(squares)  # Output: [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

# Key Takeaways

- List comprehensions provide concise syntax for creating lists
- Syntax: `[expression for item in iterable if condition]`
- Can include conditionals for filtering and conditional expressions
- Work with strings, numbers, and nested structures
- Also available for dictionaries and sets
- Use when it improves readability, not always
- Can be more efficient than equivalent loops

# Related Topics

- Lists (Python Beginner #7)
- Dictionary Comprehensions (covered in this lesson)
- Generators (Python Intermediate #8)
- Functional Programming (Python Advanced #5)
