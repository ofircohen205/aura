---
title: "Context Managers"
language: python
difficulty: intermediate
prerequisites: ["Error Handling", "File I/O"]
keywords: [context managers, with statement, __enter__, __exit__, resource management, try-finally]
---

# Learning Objectives

- Understand what context managers are
- Use the `with` statement for resource management
- Create custom context managers
- Understand `__enter__` and `__exit__` methods
- Use `contextlib` for simpler context managers
- Recognize when to use context managers

# Prerequisites

- Error Handling
- File I/O

# Introduction

Context managers ensure that setup and cleanup code is executed properly, even if errors occur. The `with` statement is Python's way of using context managers. They're essential for managing resources like files, database connections, and locks.

# Core Concepts

## Using Context Managers

The `with` statement automatically handles setup and cleanup:

```python
# File handling (most common use)
with open("data.txt", "r") as file:
    content = file.read()
    # File is automatically closed here, even if error occurs
```

## How Context Managers Work

Context managers use `__enter__` and `__exit__` methods:

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions

# Usage
with FileManager("data.txt", "r") as file:
    content = file.read()
```

## Creating Custom Context Managers

### Using a Class

```python
class Timer:
    def __init__(self):
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        print(f"Elapsed time: {elapsed:.2f} seconds")
        return False

with Timer():
    # Some code that takes time
    sum(range(1000000))
```

### Using `contextlib.contextmanager`

Simpler way using a decorator:

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.2f} seconds")

with timer():
    sum(range(1000000))
```

## Multiple Context Managers

You can use multiple context managers:

```python
with open("input.txt", "r") as infile, open("output.txt", "w") as outfile:
    content = infile.read()
    outfile.write(content.upper())
```

## Suppressing Exceptions

Context managers can suppress exceptions:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("temp_file.txt")  # Won't raise error if file doesn't exist
```

## Redirecting Output

```python
from contextlib import redirect_stdout
import io

f = io.StringIO()
with redirect_stdout(f):
    print("This goes to StringIO, not console")
output = f.getvalue()
```

# Common Mistakes

- **Forgetting `as` keyword**: `with open("file.txt") file:` is wrong
- **Not handling exceptions in `__exit__`**: Should return False to propagate exceptions
- **Not closing resources**: Always ensure cleanup in `__exit__`
- **Using when not needed**: Simple cases might not need context managers
- **Wrong exception handling**: `__exit__` receives exception info - handle appropriately

# Practice Exercises

1. Create a context manager that changes to a directory and changes back.
2. Create a context manager that temporarily modifies an environment variable.
3. Create a timer context manager that measures execution time.
4. Create a context manager that locks a resource (simulate with a flag).
5. Use `contextlib.contextmanager` to create a simple context manager.

Example solution for exercise 3:

```python
from contextlib import contextmanager
import time

@contextmanager
def timer():
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"Execution took {elapsed:.2f} seconds")

with timer():
    sum(range(1000000))
```

# Key Takeaways

- Context managers ensure proper resource cleanup
- Use `with` statement to use context managers
- Context managers implement `__enter__` and `__exit__` methods
- `contextlib.contextmanager` provides simpler way to create context managers
- Context managers are perfect for file handling, locks, and resource management
- `__exit__` receives exception information and can suppress exceptions
- Always ensure cleanup happens in `__exit__` method

# Related Topics

- Error Handling (Python Intermediate #3)
- File I/O (Python Intermediate #4)
- Decorators (Python Advanced #1)
