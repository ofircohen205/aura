---
title: "Strings"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Lists"]
keywords: [strings, text, methods, formatting, slicing, concatenation, immutability]
---

# Learning Objectives

- Work with strings and understand string methods
- Use string formatting (f-strings)
- Slice and manipulate strings
- Understand that strings are immutable
- Use common string methods like `upper()`, `lower()`, `split()`, and `join()`

# Prerequisites

- Variables and Data Types
- Lists

# Introduction

Strings are sequences of characters used to represent text. In Python, strings are very powerful and come with many built-in methods for manipulation. Understanding strings is essential since most programs work with text data.

# Core Concepts

## Creating Strings

You can create strings using single quotes, double quotes, or triple quotes:

```python
# Single quotes
name = 'Alice'

# Double quotes
greeting = "Hello"

# Triple quotes for multi-line strings
message = """This is a
multi-line
string"""

# All are equivalent
text1 = "Hello"
text2 = 'Hello'
print(text1 == text2)  # Output: True
```

## String Indexing and Slicing

Strings work like lists - you can access individual characters:

```python
text = "Python"

print(text[0])    # Output: P
print(text[1])    # Output: y
print(text[-1])  # Output: n (last character)

# Slicing works the same as lists
print(text[0:3])  # Output: Pyt
print(text[:3])   # Output: Pyt
print(text[3:])   # Output: hon
```

## String Concatenation

You can combine strings using `+`:

```python
first = "Hello"
second = "World"
combined = first + " " + second
print(combined)  # Output: Hello World

# You can also use +=
greeting = "Hello"
greeting += ", World!"
print(greeting)  # Output: Hello, World!
```

## String Formatting with f-strings

f-strings (formatted string literals) are the modern way to format strings:

```python
name = "Alice"
age = 25

# f-string
message = f"My name is {name} and I am {age} years old"
print(message)  # Output: My name is Alice and I am 25 years old

# You can do calculations inside
result = f"Next year I'll be {age + 1} years old"
print(result)  # Output: Next year I'll be 26 years old
```

## Common String Methods

### Case Conversion

```python
text = "Hello World"

print(text.upper())  # Output: HELLO WORLD
print(text.lower())  # Output: hello world
print(text.title())  # Output: Hello World
print(text.capitalize())  # Output: Hello world
```

### Finding and Replacing

```python
text = "Hello World"

# Find substring
print(text.find("World"))  # Output: 6 (index where it starts)
print(text.find("Python"))  # Output: -1 (not found)

# Check if substring exists
print("World" in text)  # Output: True

# Replace
new_text = text.replace("World", "Python")
print(new_text)  # Output: Hello Python
```

### Splitting and Joining

```python
# Split into a list
text = "apple,banana,orange"
fruits = text.split(",")
print(fruits)  # Output: ['apple', 'banana', 'orange']

# Join list into string
fruits = ["apple", "banana", "orange"]
text = ", ".join(fruits)
print(text)  # Output: apple, banana, orange
```

### Stripping Whitespace

```python
text = "  Hello World  "

print(text.strip())   # Output: Hello World (removes both sides)
print(text.lstrip())  # Output: Hello World   (removes left)
print(text.rstrip())  # Output:   Hello World (removes right)
```

### Checking String Content

```python
text = "Hello123"

print(text.isalpha())  # Output: False (contains numbers)
print(text.isdigit())  # Output: False (contains letters)
print(text.isalnum())  # Output: True (letters and numbers)
print(text.startswith("Hello"))  # Output: True
print(text.endswith("123"))      # Output: True
```

## String Immutability

Strings are immutable - you can't change them in place:

```python
text = "Hello"
# text[0] = "h"  # Error! Strings are immutable

# Instead, create a new string
text = "h" + text[1:]
print(text)  # Output: hello
```

## String Length

Use `len()` to get the length of a string:

```python
text = "Python"
print(len(text))  # Output: 6
```

# Common Mistakes

- **Trying to modify strings directly**: Strings are immutable, create new ones instead
- **Forgetting quotes**: `name = Alice` is wrong, use `name = "Alice"`
- **Confusing `find()` and `index()`**: `find()` returns -1 if not found, `index()` raises an error
- **Not handling case sensitivity**: "Hello" != "hello" - use `lower()` for comparisons
- **Forgetting that string methods return new strings**: They don't modify the original

# Practice Exercises

1. Write a function that takes a string and returns it reversed.
2. Write a function that counts how many times a character appears in a string.
3. Write a function that checks if a string is a palindrome (reads same forwards and backwards).
4. Write a function that takes a sentence and capitalizes the first letter of each word.
5. Write a function that removes all vowels from a string.

Example solution for exercise 1:

```python
def reverse_string(text):
    return text[::-1]

result = reverse_string("Python")
print(result)  # Output: nohtyP
```

# Key Takeaways

- Strings are sequences of characters created with quotes
- You can index and slice strings like lists
- Use f-strings for modern string formatting
- Strings are immutable - methods return new strings
- Common methods: `upper()`, `lower()`, `split()`, `join()`, `replace()`, `strip()`
- Use `len()` to get string length
- Use `in` to check if a substring exists

# Related Topics

- Variables and Data Types (Python Beginner #1)
- Lists (Python Beginner #7)
- Dictionaries (next lesson)
- String Methods (covered in this lesson)
