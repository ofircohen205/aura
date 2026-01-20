---
title: "Dictionaries"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Lists", "Strings"]
keywords: [dictionaries, dict, key-value pairs, mapping, hash tables, lookup]
---

# Learning Objectives

- Understand what dictionaries are and when to use them
- Create and access dictionary elements
- Add, modify, and remove dictionary items
- Use common dictionary methods
- Loop through dictionaries

# Prerequisites

- Variables and Data Types
- Lists
- Strings

# Introduction

A dictionary is a collection of key-value pairs. Unlike lists which use numeric indices, dictionaries use keys (which can be strings, numbers, or other immutable types) to access values. Dictionaries are perfect for storing related information, like a person's details or a word and its definition.

# Core Concepts

## Creating Dictionaries

You create dictionaries using curly braces `{}` with key-value pairs:

```python
# Empty dictionary
my_dict = {}

# Dictionary with key-value pairs
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}

# Using dict() constructor
student = dict(name="Alice", age=20, grade="A")
```

## Accessing Dictionary Values

You access values using their keys:

```python
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}

print(student["name"])  # Output: Alice
print(student["age"])   # Output: 20

# Using .get() method (safer - returns None if key doesn't exist)
print(student.get("name"))      # Output: Alice
print(student.get("email"))     # Output: None (key doesn't exist)
print(student.get("email", "N/A"))  # Output: N/A (default value)
```

## Adding and Modifying Items

You can add new items or modify existing ones:

```python
student = {"name": "Alice", "age": 20}

# Add new key-value pair
student["grade"] = "A"
print(student)  # Output: {'name': 'Alice', 'age': 20, 'grade': 'A'}

# Modify existing value
student["age"] = 21
print(student)  # Output: {'name': 'Alice', 'age': 21, 'grade': 'A'}
```

## Removing Items

You can remove items in several ways:

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Using del
del student["grade"]
print(student)  # Output: {'name': 'Alice', 'age': 20}

# Using .pop() (returns the value)
age = student.pop("age")
print(age)      # Output: 20
print(student)  # Output: {'name': 'Alice'}

# Using .popitem() (removes and returns last item as tuple)
item = student.popitem()
print(item)     # Output: ('name', 'Alice')
print(student)  # Output: {}

# Clear all items
student = {"name": "Alice", "age": 20}
student.clear()
print(student)  # Output: {}
```

## Dictionary Methods

### Getting Keys, Values, and Items

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Get all keys
print(student.keys())    # Output: dict_keys(['name', 'age', 'grade'])

# Get all values
print(student.values())  # Output: dict_values(['Alice', 20, 'A'])

# Get all key-value pairs as tuples
print(student.items())   # Output: dict_items([('name', 'Alice'), ('age', 20), ('grade', 'A')])
```

### Checking for Keys

```python
student = {"name": "Alice", "age": 20}

# Check if key exists
if "name" in student:
    print("Name exists")

# Using .get() with default
email = student.get("email", "not provided")
print(email)  # Output: not provided
```

### Updating Dictionaries

```python
student = {"name": "Alice", "age": 20}

# Update with another dictionary
student.update({"grade": "A", "email": "alice@example.com"})
print(student)  # Output: {'name': 'Alice', 'age': 20, 'grade': 'A', 'email': 'alice@example.com'}
```

## Looping Through Dictionaries

You can loop through dictionaries in several ways:

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Loop through keys
for key in student:
    print(key)  # Output: name, age, grade

# Loop through keys explicitly
for key in student.keys():
    print(key)

# Loop through values
for value in student.values():
    print(value)  # Output: Alice, 20, A

# Loop through key-value pairs
for key, value in student.items():
    print(f"{key}: {value}")
# Output:
# name: Alice
# age: 20
# grade: A
```

## Nested Dictionaries

Dictionaries can contain other dictionaries:

```python
students = {
    "alice": {"age": 20, "grade": "A"},
    "bob": {"age": 19, "grade": "B"},
    "charlie": {"age": 21, "grade": "A"}
}

print(students["alice"]["grade"])  # Output: A
```

## Dictionary Comprehensions

You can create dictionaries using comprehensions:

```python
# Create dictionary of squares
squares = {x: x**2 for x in range(5)}
print(squares)  # Output: {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Create dictionary from two lists
keys = ["name", "age", "city"]
values = ["Alice", 25, "New York"]
person = {k: v for k, v in zip(keys, values)}
print(person)  # Output: {'name': 'Alice', 'age': 25, 'city': 'New York'}
```

# Common Mistakes

- **Accessing non-existent key**: `dict["key"]` raises KeyError if key doesn't exist - use `.get()` instead
- **Using mutable types as keys**: Only immutable types (strings, numbers, tuples) can be keys
- **Confusing keys and values**: Keys are what you use to look up, values are what you get back
- **Forgetting that dictionaries are unordered** (in Python < 3.7): Order is preserved in Python 3.7+
- **Using `=` for copying**: `dict2 = dict1` creates a reference, not a copy

# Practice Exercises

1. Create a dictionary representing a person with name, age, and city.
2. Write a function that counts how many times each character appears in a string.
3. Write a function that takes a list of words and returns a dictionary mapping each word to its length.
4. Write a function that merges two dictionaries (if keys overlap, use values from the second dictionary).
5. Create a nested dictionary for a library with books, where each book has title, author, and year.

Example solution for exercise 2:

```python
def count_chars(text):
    char_count = {}
    for char in text:
        if char in char_count:
            char_count[char] += 1
        else:
            char_count[char] = 1
    return char_count

result = count_chars("hello")
print(result)  # Output: {'h': 1, 'e': 1, 'l': 2, 'o': 1}
```

# Key Takeaways

- Dictionaries store key-value pairs using curly braces `{}`
- Access values using keys: `dict["key"]` or `dict.get("key")`
- Dictionaries are mutable - you can add, modify, and remove items
- Use `.keys()`, `.values()`, and `.items()` to iterate
- Dictionaries are great for storing related information
- Keys must be immutable types (strings, numbers, tuples)
- Use `.get()` to safely access values that might not exist

# Related Topics

- Variables and Data Types (Python Beginner #1)
- Lists (Python Beginner #7)
- Error Handling (next lesson)
- Dictionary Comprehensions (covered in this lesson)
