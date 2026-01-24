---
title: "Lists"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Loops", "Functions"]
keywords: [lists, arrays, indexing, slicing, append, methods, sequences, collections]
---

# Learning Objectives

- Create and work with lists
- Access list elements using indexing
- Modify lists by adding, removing, and changing elements
- Use list slicing to get subsets of lists
- Use common list methods like `append()`, `remove()`, and `len()`

# Prerequisites

- Variables and Data Types
- Loops
- Functions

# Introduction

A list is a collection of items stored in a specific order. Lists are one of Python's most versatile data structures - you can store numbers, strings, or even other lists. Lists are mutable, meaning you can change them after creating them.

# Core Concepts

## Creating Lists

You create a list using square brackets `[]`:

```python
# Empty list
my_list = []

# List of numbers
numbers = [1, 2, 3, 4, 5]

# List of strings
fruits = ["apple", "banana", "orange"]

# Mixed types (allowed in Python)
mixed = [1, "hello", 3.14, True]
```

## Accessing List Elements

You access elements using their index (position). Indexing starts at 0:

```python
fruits = ["apple", "banana", "orange"]

print(fruits[0])  # Output: apple (first element)
print(fruits[1])  # Output: banana (second element)
print(fruits[2])  # Output: orange (third element)
```

## Negative Indexing

You can use negative indices to count from the end:

```python
fruits = ["apple", "banana", "orange"]

print(fruits[-1])  # Output: orange (last element)
print(fruits[-2])  # Output: banana (second to last)
print(fruits[-3])  # Output: apple (third to last)
```

## Modifying Lists

Lists are mutable - you can change their elements:

```python
fruits = ["apple", "banana", "orange"]
fruits[1] = "grape"  # Change the second element
print(fruits)  # Output: ['apple', 'grape', 'orange']
```

## List Slicing

You can get a subset of a list using slicing `[start:stop:step]`:

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(numbers[2:5])    # Output: [2, 3, 4] (from index 2 to 4)
print(numbers[:3])     # Output: [0, 1, 2] (first 3 elements)
print(numbers[3:])     # Output: [3, 4, 5, 6, 7, 8, 9] (from index 3 to end)
print(numbers[::2])    # Output: [0, 2, 4, 6, 8] (every 2nd element)
print(numbers[::-1])   # Output: [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (reversed)
```

## Common List Methods

### Adding Elements

```python
fruits = ["apple", "banana"]

# Add to the end
fruits.append("orange")
print(fruits)  # Output: ['apple', 'banana', 'orange']

# Insert at a specific position
fruits.insert(1, "grape")
print(fruits)  # Output: ['apple', 'grape', 'banana', 'orange']

# Add multiple elements
fruits.extend(["kiwi", "mango"])
print(fruits)  # Output: ['apple', 'grape', 'banana', 'orange', 'kiwi', 'mango']
```

### Removing Elements

```python
fruits = ["apple", "banana", "orange", "banana"]

# Remove by value (removes first occurrence)
fruits.remove("banana")
print(fruits)  # Output: ['apple', 'orange', 'banana']

# Remove by index
del fruits[0]
print(fruits)  # Output: ['orange', 'banana']

# Remove and return the last element
last = fruits.pop()
print(last)    # Output: banana
print(fruits)  # Output: ['orange']
```

### Other Useful Methods

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

# Get length
print(len(numbers))  # Output: 8

# Count occurrences
print(numbers.count(1))  # Output: 2

# Find index
print(numbers.index(4))  # Output: 2

# Sort (modifies the list)
numbers.sort()
print(numbers)  # Output: [1, 1, 2, 3, 4, 5, 9, 6]

# Sort without modifying (returns new list)
sorted_numbers = sorted(numbers)
```

## Looping Through Lists

You can loop through lists in several ways:

```python
fruits = ["apple", "banana", "orange"]

# Loop through values
for fruit in fruits:
    print(fruit)

# Loop through indices
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Loop with both index and value
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

## List Comprehensions (Preview)

List comprehensions provide a concise way to create lists:

```python
# Create a list of squares
squares = [x**2 for x in range(5)]
print(squares)  # Output: [0, 1, 4, 9, 16]

# Create a list of even numbers
evens = [x for x in range(10) if x % 2 == 0]
print(evens)  # Output: [0, 2, 4, 6, 8]
```

# Common Mistakes

- **Index out of range**: `list[10]` when the list only has 5 elements
- **Forgetting that indexing starts at 0**: First element is `list[0]`, not `list[1]`
- **Confusing `append()` and `extend()`**: `append()` adds one item, `extend()` adds multiple
- **Modifying a list while iterating**: Can cause unexpected behavior
- **Using `=` for copying**: `list2 = list1` creates a reference, not a copy

# Practice Exercises

1. Create a list of your favorite fruits and print each one.
2. Write a function that takes a list of numbers and returns the sum.
3. Write a function that takes a list and returns a new list with duplicates removed.
4. Write a function that finds the maximum value in a list (without using `max()`).
5. Create a list of numbers 1-10, then remove all even numbers from it.

Example solution for exercise 2:

```python
def sum_list(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = sum_list([1, 2, 3, 4, 5])
print(result)  # Output: 15
```

# Key Takeaways

- Lists are ordered collections created with square brackets `[]`
- Access elements using index (starts at 0): `list[0]`
- Use negative indices to count from the end: `list[-1]`
- Lists are mutable - you can modify them
- Use slicing `[start:stop:step]` to get subsets
- Common methods: `append()`, `remove()`, `pop()`, `len()`, `sort()`
- You can loop through lists with `for` loops

# Related Topics

- Variables and Data Types (Python Beginner #1)
- Loops (Python Beginner #5)
- Functions (Python Beginner #6)
- Strings (next lesson)
- List Comprehensions (Python Intermediate #1)
