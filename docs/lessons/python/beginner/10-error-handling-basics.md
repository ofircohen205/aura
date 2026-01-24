---
title: "Error Handling Basics"
language: python
difficulty: beginner
prerequisites: ["Functions", "Conditionals"]
keywords: [errors, exceptions, try, except, error handling, debugging, traceback]
---

# Learning Objectives

- Understand what errors and exceptions are
- Use `try` and `except` to handle errors
- Handle specific types of errors
- Use `else` and `finally` clauses
- Write code that fails gracefully

# Prerequisites

- Functions
- Conditionals

# Introduction

When you write code, things can go wrong. A user might enter invalid input, a file might not exist, or you might try to divide by zero. Instead of letting your program crash, you can handle these errors gracefully using exception handling. This makes your programs more robust and user-friendly.

# Core Concepts

## What are Exceptions?

Exceptions are errors that occur during program execution. When an exception occurs, Python stops execution and shows an error message (traceback).

```python
# This will cause an error
result = 10 / 0
# ZeroDivisionError: division by zero

# This will also cause an error
numbers = [1, 2, 3]
print(numbers[10])
# IndexError: list index out of range
```

## Basic try-except

Use `try` and `except` to catch and handle errors:

```python
try:
    result = 10 / 0
except:
    print("An error occurred!")

# Output: An error occurred!
# Program continues instead of crashing
```

## Handling Specific Exceptions

You can catch specific types of errors:

```python
try:
    number = int(input("Enter a number: "))
    result = 10 / number
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("You can't divide by zero!")
```

## Common Exception Types

Here are some common exceptions you'll encounter:

- `ValueError` - Wrong type of value
- `TypeError` - Wrong type used in operation
- `IndexError` - Index out of range
- `KeyError` - Dictionary key doesn't exist
- `ZeroDivisionError` - Division by zero
- `FileNotFoundError` - File doesn't exist

```python
# ValueError
try:
    number = int("hello")
except ValueError:
    print("Can't convert 'hello' to a number")

# IndexError
try:
    items = [1, 2, 3]
    print(items[10])
except IndexError:
    print("Index out of range")

# KeyError
try:
    person = {"name": "Alice"}
    print(person["age"])
except KeyError:
    print("Key 'age' doesn't exist")
```

## Multiple Exceptions

You can handle multiple exceptions in one block:

```python
try:
    # Some code that might fail
    pass
except (ValueError, TypeError):
    print("Value or type error occurred")
```

## The else Clause

Code in `else` runs only if no exception occurred:

```python
try:
    number = int(input("Enter a number: "))
except ValueError:
    print("That's not a number!")
else:
    print(f"You entered: {number}")
    # This only runs if no error occurred
```

## The finally Clause

Code in `finally` always runs, whether an exception occurred or not:

```python
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    print("This always runs")
    # Good place to clean up resources
```

## Raising Exceptions

You can raise your own exceptions using `raise`:

```python
def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")
    return f"Age {age} is valid"

try:
    result = check_age(-5)
except ValueError as e:
    print(f"Error: {e}")  # Output: Error: Age cannot be negative
```

## Getting Error Information

You can get information about the error:

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
```

# Common Mistakes

- **Catching all exceptions with bare `except:`**: Always specify exception types when possible
- **Swallowing errors silently**: At least print or log the error
- **Catching too broad**: Catch specific exceptions, not all of them
- **Not cleaning up resources**: Use `finally` to ensure cleanup happens
- **Raising generic Exception**: Use specific exception types

# Practice Exercises

1. Write a function that safely converts a string to an integer, returning None if it fails.
2. Write a function that safely accesses a list element, returning a default value if index is out of range.
3. Write a function that safely gets a dictionary value, returning a default if key doesn't exist (without using .get()).
4. Write a function that divides two numbers and handles division by zero gracefully.
5. Write a function that validates user input (age must be between 0 and 120) and raises a ValueError if invalid.

Example solution for exercise 1:

```python
def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return None

result = safe_int("123")
print(result)  # Output: 123

result = safe_int("abc")
print(result)  # Output: None
```

# Key Takeaways

- Use `try` and `except` to handle errors gracefully
- Catch specific exception types when possible
- Use `else` for code that should run only if no error occurred
- Use `finally` for cleanup code that must always run
- You can raise your own exceptions with `raise`
- Error handling makes your programs more robust and user-friendly
- Don't catch all exceptions silently - handle them appropriately

# Related Topics

- Functions (Python Beginner #6)
- Conditionals (Python Beginner #4)
- Exception Handling (Python Intermediate #6 - more advanced topics)
