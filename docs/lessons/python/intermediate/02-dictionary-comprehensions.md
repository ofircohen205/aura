---
title: "Dictionary Comprehensions"
language: python
difficulty: intermediate
prerequisites: ["Dictionaries", "List Comprehensions"]
keywords:
  [dictionary comprehensions, dict comprehensions, mapping, transformations, key-value pairs]
---

# Learning Objectives

- Create dictionaries using comprehensions
- Transform existing dictionaries
- Filter dictionary items with comprehensions
- Combine multiple dictionaries
- Understand when to use dictionary comprehensions

# Prerequisites

- Dictionaries
- List Comprehensions

# Introduction

Just like list comprehensions provide a concise way to create lists, dictionary comprehensions provide an elegant way to create dictionaries. They're perfect for transforming data, creating mappings, and building dictionaries from other data structures.

# Core Concepts

## Basic Dictionary Comprehension

The basic syntax: `{key_expression: value_expression for item in iterable}`

```python
# Traditional approach
squares = {}
for x in range(5):
    squares[x] = x ** 2
print(squares)  # Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Dictionary comprehension
squares = {x: x ** 2 for x in range(5)}
print(squares)  # Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

## From Lists

Create dictionaries from lists:

```python
# Map names to their lengths
names = ["Alice", "Bob", "Charlie"]
name_lengths = {name: len(name) for name in names}
print(name_lengths)  # Output: {'Alice': 5, 'Bob': 3, 'Charlie': 7}

# Create index mapping
items = ["apple", "banana", "orange"]
indexed = {i: item for i, item in enumerate(items)}
print(indexed)  # Output: {0: 'apple', 1: 'banana', 2: 'orange'}
```

## Filtering Dictionaries

Add conditions to filter items:

```python
# Keep only even values
numbers = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
evens = {k: v for k, v in numbers.items() if v % 2 == 0}
print(evens)  # Output: {'b': 2, 'd': 4}

# Keep items where key starts with 'a'
words = {"apple": 5, "banana": 6, "apricot": 7, "cherry": 6}
a_words = {k: v for k, v in words.items() if k.startswith("a")}
print(a_words)  # Output: {'apple': 5, 'apricot': 7}
```

## Transforming Keys and Values

Transform both keys and values:

```python
# Uppercase keys, double values
data = {"name": "alice", "age": 25}
transformed = {k.upper(): v * 2 for k, v in data.items()}
print(transformed)  # Output: {'NAME': 'alicealice', 'AGE': 50}

# Swap keys and values
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
print(swapped)  # Output: {1: 'a', 2: 'b', 3: 'c'}
```

## Conditional Value Assignment

Use conditional expressions for values:

```python
# Mark numbers as "even" or "odd"
numbers = [1, 2, 3, 4, 5]
labels = {num: "even" if num % 2 == 0 else "odd" for num in numbers}
print(labels)  # Output: {1: 'odd', 2: 'even', 3: 'odd', 4: 'even', 5: 'odd'}
```

## From Two Lists

Create dictionary from two lists:

```typescript
keys = ["name", "age", "city"]
values = ["Alice", 25, "New York"]
person = {k: v for k, v in zip(keys, values)}
print(person)  # Output: {'name': 'Alice', 'age': 25, 'city': 'New York'}
```

## Nested Comprehensions

You can nest comprehensions:

```python
# Create nested dictionary structure
matrix = {i: {j: i * j for j in range(3)} for i in range(3)}
print(matrix)
# Output: {0: {0: 0, 1: 0, 2: 0}, 1: {0: 0, 1: 1, 2: 2}, 2: {0: 0, 1: 2, 2: 4}}
```

# Common Mistakes

- **Confusing with list comprehensions**: Use `{}` not `[]` for dictionaries
- **Duplicate keys**: Later values overwrite earlier ones with same key
- **Over-complicating**: Sometimes a simple loop is clearer
- **Forgetting `.items()`**: Need to iterate over key-value pairs
- **Wrong order**: `{key: value}` not `{value: key}` unless intentionally swapping

# Practice Exercises

1. Create a dictionary mapping numbers 1-5 to their squares.
2. Create a dictionary from a list of words, mapping each word to its length.
3. Filter a dictionary to keep only items where the value is greater than 10.
4. Create a dictionary that swaps keys and values from an existing dictionary.
5. Create a dictionary from two lists (keys and values) using zip.

Example solution for exercise 1:

```python
squares = {x: x ** 2 for x in range(1, 6)}
print(squares)  # Output: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

# Key Takeaways

- Dictionary comprehensions create dictionaries concisely
- Syntax: `{key: value for item in iterable if condition}`
- Can transform keys, values, or both
- Use `.items()` to iterate over existing dictionaries
- Can filter items with conditions
- Useful for data transformations and mappings
- More Pythonic than loops for simple transformations

# Related Topics

- Dictionaries (Python Beginner #9)
- List Comprehensions (Python Intermediate #1)
- Generators (Python Intermediate #8)
