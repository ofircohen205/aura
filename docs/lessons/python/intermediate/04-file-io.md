---
title: "File I/O"
language: python
difficulty: intermediate
prerequisites: ["Error Handling", "Strings"]
keywords: [files, file operations, reading, writing, context managers, file modes, paths]
---

# Learning Objectives

- Read from and write to files
- Understand different file modes
- Use context managers for file operations
- Work with different file formats (text, CSV, JSON)
- Handle file paths correctly
- Understand file encoding

# Prerequisites

- Error Handling
- Strings

# Introduction

Working with files is essential for most real-world programs. Python provides excellent tools for reading and writing files. Understanding file I/O allows you to persist data, read configuration files, process data files, and much more.

# Core Concepts

## Opening Files

Use the `open()` function to open files:

```python
# Basic file opening
file = open("data.txt", "r")  # 'r' = read mode
content = file.read()
file.close()  # Always close files!
```

## File Modes

Common file modes:

- `'r'` - Read (default, file must exist)
- `'w'` - Write (overwrites existing file)
- `'a'` - Append (adds to end of file)
- `'x'` - Exclusive creation (fails if file exists)
- `'b'` - Binary mode (e.g., `'rb'`, `'wb'`)
- `'+'` - Read and write (e.g., `'r+'`)

## Reading Files

### Read Entire File

```python
with open("data.txt", "r") as file:
    content = file.read()  # Reads entire file as string
    print(content)
```

### Read Line by Line

```python
with open("data.txt", "r") as file:
    for line in file:
        print(line.strip())  # strip() removes newline
```

### Read All Lines

```python
with open("data.txt", "r") as file:
    lines = file.readlines()  # Returns list of lines
    for line in lines:
        print(line.strip())
```

### Read Single Line

```python
with open("data.txt", "r") as file:
    first_line = file.readline()  # Reads one line
    second_line = file.readline()  # Reads next line
```

## Writing Files

### Write Text

```python
with open("output.txt", "w") as file:
    file.write("Hello, World!\n")
    file.write("This is line 2\n")
```

### Write Multiple Lines

```python
lines = ["Line 1\n", "Line 2\n", "Line 3\n"]
with open("output.txt", "w") as file:
    file.writelines(lines)
```

## Appending to Files

```python
with open("log.txt", "a") as file:
    file.write("New log entry\n")
```

## Context Managers (Recommended)

Always use `with` statement - automatically closes file:

```python
# Good - automatic cleanup
with open("data.txt", "r") as file:
    content = file.read()
# File is automatically closed here

# Bad - manual cleanup (easy to forget)
file = open("data.txt", "r")
content = file.read()
file.close()  # What if an error occurs before this?
```

## Working with Paths

Use `pathlib` for modern path handling:

```python
from pathlib import Path

# Create Path object
file_path = Path("data.txt")

# Check if exists
if file_path.exists():
    with open(file_path, "r") as file:
        content = file.read()

# Get file info
print(file_path.name)      # filename
print(file_path.suffix)    # extension
print(file_path.parent)    # directory
```

## File Encoding

Specify encoding for text files:

```python
# UTF-8 (default in Python 3)
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Other encodings
with open("data.txt", "r", encoding="latin-1") as file:
    content = file.read()
```

## Working with CSV Files

```python
import csv

# Reading CSV
with open("data.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)  # Each row is a list

# Reading as dictionary
with open("data.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row["name"])  # Access by column name

# Writing CSV
with open("output.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Age", "City"])
    writer.writerow(["Alice", "25", "New York"])
```

## Working with JSON Files

```python
import json

# Reading JSON
with open("data.json", "r") as file:
    data = json.load(file)  # Returns dict or list
    print(data["name"])

# Writing JSON
data = {"name": "Alice", "age": 25}
with open("output.json", "w") as file:
    json.dump(data, file, indent=2)  # indent for pretty printing
```

# Common Mistakes

- **Forgetting to close files**: Always use `with` statement
- **Wrong file mode**: Using `'w'` when you meant `'r'` (overwrites file!)
- **Not handling FileNotFoundError**: File might not exist
- **Not specifying encoding**: Can cause issues with special characters
- **Reading large files entirely**: Use line-by-line for large files
- **Not using `newline=""` for CSV**: Can cause extra blank lines

# Practice Exercises

1. Write a program that reads a text file and prints each line with line numbers.
2. Write a program that reads a file and writes a copy with all lines reversed.
3. Write a program that reads a CSV file and calculates the average of a numeric column.
4. Write a program that reads a JSON file, modifies it, and writes it back.
5. Write a function that safely reads a file, returning None if the file doesn't exist.

Example solution for exercise 1:

```python
def print_with_line_numbers(filename):
    with open(filename, "r") as file:
        for line_num, line in enumerate(file, 1):
            print(f"{line_num}: {line.rstrip()}")

print_with_line_numbers("data.txt")
```

# Key Takeaways

- Always use `with` statement for file operations (automatic cleanup)
- File modes: `'r'` (read), `'w'` (write), `'a'` (append)
- Read entire file with `read()`, line-by-line with `for line in file`
- Use `pathlib.Path` for modern path handling
- Specify encoding when working with non-ASCII text
- Use `csv` module for CSV files, `json` module for JSON files
- Handle `FileNotFoundError` when files might not exist

# Related Topics

- Error Handling (Python Intermediate #3)
- Strings (Python Beginner #8)
- Modules (Python Intermediate #5)
