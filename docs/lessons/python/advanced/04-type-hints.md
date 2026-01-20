---
title: "Type Hints and Type Checking"
language: python
difficulty: advanced
prerequisites: ["Functions", "Object-Oriented Programming Basics"]
keywords: [type hints, typing, mypy, static typing, annotations, type checking]
---

# Learning Objectives

- Add type hints to functions and variables
- Use the `typing` module for complex types
- Understand generic types
- Use type checking tools like `mypy`
- Annotate classes and methods
- Work with Optional, Union, and other type constructs

# Prerequisites

- Functions
- Object-Oriented Programming Basics

# Introduction

Type hints allow you to annotate your Python code with type information. While Python remains dynamically typed, type hints provide documentation, enable static type checking, and improve IDE support. Understanding type hints makes your code more maintainable and helps catch errors early.

# Core Concepts

## Basic Type Hints

Add type hints to function parameters and return values:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b
```

## Variable Type Hints

Annotate variables (Python 3.6+):

```python
name: str = "Alice"
age: int = 25
is_student: bool = True
```

## The typing Module

Use `typing` for more complex types:

```python
from typing import List, Dict, Tuple, Optional, Union

# List of strings
names: List[str] = ["Alice", "Bob"]

# Dictionary mapping string to int
scores: Dict[str, int] = {"Alice": 95, "Bob": 87}

# Tuple with specific types
point: Tuple[int, int] = (10, 20)

# Optional (can be None)
age: Optional[int] = None
age = 25  # Also valid

# Union (one of several types)
value: Union[int, str] = 42
value = "hello"  # Also valid
```

## Generic Types (Python 3.9+)

Use built-in types directly:

```python
# Python 3.9+ - use built-in types
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95}
point: tuple[int, int] = (10, 20)

# Python 3.10+ - use | for Union
value: int | str = 42
age: int | None = None  # Or use Optional[int]
```

## Function Type Hints

```python
from typing import Callable, Optional

# Function that takes int and returns int
def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Optional parameter
def greet(name: str, title: Optional[str] = None) -> str:
    if title:
        return f"Hello, {title} {name}!"
    return f"Hello, {name}!"
```

## Class Type Hints

```python
class Person:
    def __init__(self, name: str, age: int) -> None:
        self.name: str = name
        self.age: int = age

    def get_info(self) -> str:
        return f"{self.name} is {self.age} years old"
```

## Type Aliases

Create aliases for complex types:

```python
from typing import Dict, List

# Type alias
UserId = int
UserData = Dict[str, str]
UserList = List[UserData]

def get_users() -> UserList:
    return [{"name": "Alice"}, {"name": "Bob"}]
```

## Type Checking with mypy

Install and use mypy for static type checking:

```bash
pip install mypy
mypy your_file.py
```

Example:

```python
# example.py
def add(a: int, b: int) -> int:
    return a + b

result = add("hello", "world")  # Type error!
```

Running `mypy example.py` will catch the type error.

# Common Mistakes

- **Type hints are optional**: Python still runs without them
- **Using wrong syntax for older Python**: Use `typing` module for Python < 3.9
- **Over-annotating**: Don't add types where they're obvious
- **Not using mypy**: Type hints don't enforce types at runtime
- **Confusing Optional and Union**: `Optional[T]` is `Union[T, None]`

# Practice Exercises

1. Add type hints to a function that processes a list of numbers.
2. Create a function with Optional and Union type hints.
3. Add type hints to a class with methods.
4. Create type aliases for complex nested types.
5. Use mypy to check type errors in your code.

Example solution for exercise 1:

```python
from typing import List

def process_numbers(numbers: List[int]) -> dict[str, float]:
    return {
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers) if numbers else 0,
        "count": len(numbers)
    }

result = process_numbers([1, 2, 3, 4, 5])
print(result)
```

# Key Takeaways

- Type hints provide type information without changing runtime behavior
- Use `typing` module for complex types (Python < 3.9)
- Use built-in types directly in Python 3.9+ (`list[str]` instead of `List[str]`)
- `Optional[T]` means the value can be `T` or `None`
- `Union[A, B]` means the value can be `A` or `B`
- Use `mypy` for static type checking
- Type hints improve code documentation and IDE support

# Related Topics

- Functions (Python Beginner #6)
- Object-Oriented Programming Basics (Python Intermediate #6)
- Generics (covered in this lesson)
