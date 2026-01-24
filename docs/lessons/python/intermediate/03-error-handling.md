---
title: "Error Handling"
language: python
difficulty: intermediate
prerequisites: ["Error Handling Basics", "Functions"]
keywords: [exceptions, try, except, finally, raise, custom exceptions, error handling patterns]
---

# Learning Objectives

- Handle multiple exception types
- Use `finally` for cleanup operations
- Raise custom exceptions
- Create custom exception classes
- Understand exception hierarchy
- Use context managers for resource management

# Prerequisites

- Error Handling Basics
- Functions

# Introduction

While basic error handling covers simple cases, real-world programs need more sophisticated error handling. This lesson covers advanced exception handling, custom exceptions, and best practices for managing errors in larger applications.

# Core Concepts

## Handling Multiple Exceptions

You can handle different exceptions differently:

```python
try:
    # Code that might raise different exceptions
    value = int(input("Enter a number: "))
    result = 10 / value
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("You can't divide by zero!")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Exception Hierarchy

Exceptions are organized in a hierarchy. Catching a parent exception catches all child exceptions:

```python
try:
    # Some code
    pass
except ArithmeticError:  # Catches ZeroDivisionError, OverflowError, etc.
    print("Math error occurred")
except Exception:  # Catches almost all exceptions
    print("General error occurred")
```

## The finally Clause

Code in `finally` always runs, whether an exception occurred or not:

```python
file = None
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    if file:
        file.close()  # Always close the file
    print("Cleanup complete")
```

## Raising Exceptions

You can raise exceptions with custom messages:

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

## Custom Exceptions

Create your own exception classes:

```python
class InvalidEmailError(Exception):
    """Raised when email format is invalid"""
    pass

class AgeError(Exception):
    """Base class for age-related errors"""
    pass

class NegativeAgeError(AgeError):
    """Raised when age is negative"""
    pass

class TooOldError(AgeError):
    """Raised when age is too high"""
    pass

def validate_user(email, age):
    if "@" not in email:
        raise InvalidEmailError("Invalid email format")
    if age < 0:
        raise NegativeAgeError("Age cannot be negative")
    if age > 150:
        raise TooOldError("Age seems unrealistic")

try:
    validate_user("invalid-email", -5)
except NegativeAgeError as e:
    print(f"Age error: {e}")
except InvalidEmailError as e:
    print(f"Email error: {e}")
```

## Exception Chaining

Preserve original exception information:

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    raise ValueError("Invalid calculation") from e
```

## Context Managers (with statement)

Use `with` for automatic resource cleanup:

```python
# Automatically closes file, even if error occurs
with open("data.txt", "r") as file:
    content = file.read()
    # File is automatically closed here, even if an error occurs
```

## Best Practices

### Be Specific

```python
# Good - specific exception
try:
    value = int(input())
except ValueError:
    print("Invalid number")

# Bad - too broad
try:
    value = int(input())
except:  # Catches everything - not recommended
    print("Error")
```

### Don't Swallow Exceptions

```python
# Bad - silently ignores errors
try:
    risky_operation()
except:
    pass  # Error is lost!

# Good - at least log it
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise if needed
```

# Common Mistakes

- **Catching too broad**: `except:` catches everything - be specific
- **Swallowing exceptions**: At least log errors, don't just `pass`
- **Not using finally for cleanup**: Use `finally` or context managers
- **Raising generic Exception**: Create specific exception types
- **Losing exception context**: Use `from` to chain exceptions

# Practice Exercises

1. Write a function that safely divides two numbers, raising a custom exception for division by zero.
2. Create a custom exception class for validation errors and use it in a validation function.
3. Write code that opens a file and ensures it's closed even if an error occurs (use `finally`).
4. Write a function that validates an email and raises a custom exception if invalid.
5. Use a context manager to read a file and handle FileNotFoundError.

Example solution for exercise 1:

```python
class DivisionByZeroError(Exception):
    pass

def safe_divide(a, b):
    if b == 0:
        raise DivisionByZeroError("Cannot divide by zero")
    return a / b

try:
    result = safe_divide(10, 0)
except DivisionByZeroError as e:
    print(f"Error: {e}")
```

# Key Takeaways

- Handle specific exceptions for better error messages
- Use `finally` for cleanup that must always happen
- Create custom exceptions for domain-specific errors
- Use context managers (`with`) for automatic resource cleanup
- Don't catch exceptions too broadly - be specific
- Always log or handle exceptions, don't silently ignore them
- Exception hierarchy allows catching related exceptions together

# Related Topics

- Error Handling Basics (Python Beginner #10)
- Functions (Python Beginner #6)
- Context Managers (Python Intermediate #9)
- Logging (covered in advanced topics)
