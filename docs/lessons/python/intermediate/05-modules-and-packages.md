---
title: "Modules and Packages"
language: python
difficulty: intermediate
prerequisites: ["Functions", "File I/O"]
keywords: [modules, packages, import, from, __init__, namespace, code organization]
---

# Learning Objectives

- Understand what modules and packages are
- Create and use your own modules
- Organize code into packages
- Understand the import system
- Use `__init__.py` files
- Understand namespace and scope

# Prerequisites

- Functions
- File I/O

# Introduction

As programs grow larger, organizing code becomes essential. Python's module and package system allows you to split code into logical, reusable units. Understanding modules and packages is crucial for writing maintainable, scalable Python applications.

# Core Concepts

## What is a Module?

A module is a Python file containing functions, classes, and variables:

```python
# math_utils.py (a module)
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
```

## Importing Modules

### Import Entire Module

```python
import math_utils

result = math_utils.add(5, 3)
print(math_utils.PI)
```

### Import Specific Items

```python
from math_utils import add, multiply

result = add(5, 3)  # No need for module prefix
```

### Import with Alias

```python
import math_utils as math

result = math.add(5, 3)
```

### Import All (Not Recommended)

```python
from math_utils import *  # Imports everything

# Can cause namespace pollution
add(5, 3)  # Works, but unclear where it comes from
```

## Creating Packages

A package is a directory containing multiple modules:

```
my_package/
    __init__.py
    module1.py
    module2.py
    subpackage/
        __init__.py
        module3.py
```

### The `__init__.py` File

Makes a directory a package (can be empty or contain initialization code):

```python
# my_package/__init__.py
from .module1 import function1
from .module2 import function2

__all__ = ['function1', 'function2']  # Controls what gets imported with *
```

## Using Packages

```python
# Import from package
from my_package import function1
from my_package.module2 import function2

# Import from subpackage
from my_package.subpackage import module3
```

## Standard Library Modules

Python comes with many built-in modules:

```python
import os
import sys
import datetime
import json
import csv
import random
import math

# Use them
print(os.getcwd())  # Current directory
print(datetime.datetime.now())  # Current time
print(random.randint(1, 10))  # Random number
```

## Module Search Path

Python searches for modules in:

1. Current directory
2. Directories in `PYTHONPATH`
3. Standard library directories
4. Site-packages directory

## `if __name__ == "__main__"`

Allows code to run when executed directly, but not when imported:

```python
# my_module.py
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    # This only runs when file is executed directly
    print(greet("World"))
    # Not when imported: import my_module
```

## Relative Imports

Import from within a package:

```python
# In my_package/module2.py
from .module1 import something  # Same package
from ..parent_package import something  # Parent package
```

# Common Mistakes

- **Circular imports**: Module A imports B, B imports A (causes issues)
- **Not using `__init__.py`**: Directory won't be recognized as package
- **Importing with `*`**: Causes namespace pollution
- **Wrong import path**: Make sure modules are in Python path
- **Naming conflicts**: Module name conflicts with standard library

# Practice Exercises

1. Create a module with utility functions and import it in another file.
2. Create a package with multiple modules and use `__init__.py` to expose functions.
3. Write a module that can be both imported and run as a script.
4. Organize related functions into a package structure.
5. Use a standard library module (like `random` or `datetime`) in your code.

Example solution for exercise 1:

```python
# utils.py
def square(x):
    return x ** 2

def cube(x):
    return x ** 3

# main.py
import utils

result1 = utils.square(5)
result2 = utils.cube(3)
print(result1, result2)  # Output: 25 27
```

# Key Takeaways

- Modules are Python files containing reusable code
- Packages are directories containing multiple modules
- Use `import` to use modules and packages
- `__init__.py` makes a directory a package
- Use `if __name__ == "__main__"` for executable modules
- Organize code into logical modules and packages
- Python's standard library provides many useful modules

# Related Topics

- Functions (Python Beginner #6)
- File I/O (Python Intermediate #4)
- Classes (Python Intermediate #6)
