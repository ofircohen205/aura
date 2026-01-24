---
title: "Decorators"
language: python
difficulty: advanced
prerequisites: ["Functions", "Object-Oriented Programming Basics"]
keywords: [decorators, @ syntax, function wrappers, higher-order functions, metaprogramming]
---

# Learning Objectives

- Understand what decorators are and how they work
- Create simple function decorators
- Use the `@` decorator syntax
- Create decorators with parameters
- Understand decorator patterns
- Apply decorators to methods

# Prerequisites

- Functions
- Object-Oriented Programming Basics

# Introduction

Decorators are a powerful Python feature that allows you to modify or extend the behavior of functions and methods without permanently modifying them. They're a form of metaprogramming and are widely used in Python frameworks and libraries. Understanding decorators unlocks advanced Python patterns.

# Core Concepts

## What are Decorators?

Decorators are functions that take another function and extend its behavior:

```python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

def say_hello():
    print("Hello!")

# Apply decorator manually
say_hello = my_decorator(say_hello)
say_hello()
```

## The @ Syntax

Python provides a cleaner syntax using `@`:

```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before function
# Hello!
# After function
```

## Decorators with Arguments

Functions that take arguments need wrapper functions that accept arguments:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before function")
        result = func(*args, **kwargs)
        print("After function")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}!")
    return f"Greeted {name}"

result = greet("Alice")
```

## Common Decorator: Timing

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()
```

## Common Decorator: Logging

```python
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

@logger
def add(a, b):
    return a + b

add(5, 3)
```

## Decorators with Parameters

Decorators that accept their own parameters:

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Output: Hello, Alice! (three times)
```

## Preserving Function Metadata

Use `functools.wraps` to preserve original function metadata:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function"""
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def say_hello():
    """Says hello"""
    print("Hello!")

print(say_hello.__name__)  # Output: say_hello (not wrapper)
print(say_hello.__doc__)   # Output: Says hello
```

## Class Decorators

You can also decorate classes:

```python
def add_method(cls):
    def new_method(self):
        return "New method added!"
    cls.new_method = new_method
    return cls

@add_method
class MyClass:
    pass

obj = MyClass()
print(obj.new_method())  # Output: New method added!
```

## Built-in Decorators

Python provides several built-in decorators:

```python
class MyClass:
    @staticmethod
    def static_method():
        return "Static method"

    @classmethod
    def class_method(cls):
        return f"Class method of {cls.__name__}"

    @property
    def my_property(self):
        return "Property value"
```

# Common Mistakes

- **Forgetting to return the wrapper**: Decorator must return a function
- **Not preserving function metadata**: Use `@wraps` to keep original function info
- **Not handling arguments**: Wrapper must accept `*args, **kwargs`
- **Not returning function result**: Wrapper should return the result of calling the function
- **Confusing decorator syntax**: `@decorator` is equivalent to `func = decorator(func)`

# Practice Exercises

1. Create a decorator that measures and prints execution time of a function.
2. Create a decorator that retries a function a specified number of times on failure.
3. Create a decorator that caches function results (memoization).
4. Create a decorator that validates function arguments (e.g., ensure positive numbers).
5. Create a decorator that logs function calls with their arguments and return values.

Example solution for exercise 1:

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} executed in {elapsed:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()
```

# Key Takeaways

- Decorators modify or extend function behavior
- Use `@decorator` syntax for cleaner code
- Decorators are higher-order functions (functions that take/return functions)
- Use `*args, **kwargs` to handle any function signature
- Use `@wraps` to preserve function metadata
- Decorators can accept their own parameters
- Decorators enable powerful metaprogramming patterns

# Related Topics

- Functions (Python Beginner #6)
- Object-Oriented Programming Basics (Python Intermediate #6)
- Metaclasses (Python Advanced #6)
