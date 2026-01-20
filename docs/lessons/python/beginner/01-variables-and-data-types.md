---
title: "Variables and Data Types"
language: python
difficulty: beginner
prerequisites: []
keywords: [variables, data types, integers, floats, strings, booleans, type, assignment]
---

# Learning Objectives

- Understand what variables are and how to create them
- Learn about Python's basic data types: integers, floats, strings, and booleans
- Practice assigning values to variables
- Learn how to check the type of a variable

# Prerequisites

- None (this is the first lesson!)

# Introduction

Variables are like labeled boxes where you can store information. In Python, you can store different types of data in variables, such as numbers, text, or true/false values. Understanding variables and data types is the foundation of programming.

# Core Concepts

## What is a Variable?

A variable is a name that refers to a value. You create a variable by giving it a name and assigning a value using the `=` sign.

```python
# Create a variable called 'name' and assign it the value "Alice"
name = "Alice"

# Create a variable called 'age' and assign it the value 25
age = 25
```

## Basic Data Types

Python has several built-in data types. Here are the most common ones:

### Integers (int)

Whole numbers, both positive and negative.

```python
age = 25
temperature = -5
count = 0
```

### Floats (float)

Numbers with decimal points.

```python
price = 19.99
temperature = 98.6
pi = 3.14159
```

### Strings (str)

Text enclosed in quotes (single or double).

```python
name = "Alice"
greeting = 'Hello'
message = "Python is fun!"
```

### Booleans (bool)

True or False values (note the capital letters).

```python
is_student = True
is_graduated = False
```

## Checking Variable Types

You can check the type of a variable using the `type()` function:

```python
age = 25
print(type(age))  # Output: <class 'int'>

name = "Alice"
print(type(name))  # Output: <class 'str'>

price = 19.99
print(type(price))  # Output: <class 'float'>

is_active = True
print(type(is_active))  # Output: <class 'bool'>
```

## Variable Naming Rules

- Variable names can contain letters, numbers, and underscores
- They must start with a letter or underscore (not a number)
- They are case-sensitive (`age` and `Age` are different)
- Use descriptive names that explain what the variable stores

```python
# Good variable names
student_name = "Bob"
student_age = 20
is_enrolled = True

# Bad variable names (avoid these)
x = "Bob"  # Not descriptive
2name = "Bob"  # Can't start with a number
student-name = "Bob"  # Can't use hyphens
```

# Common Mistakes

- **Forgetting quotes for strings**: `name = Alice` (wrong) vs `name = "Alice"` (correct)
- **Using lowercase true/false**: Python uses `True` and `False` with capital letters
- **Starting variable names with numbers**: `2students` is invalid, use `two_students` instead
- **Using reserved words**: Don't use Python keywords like `if`, `for`, `class` as variable names

# Practice Exercises

1. Create a variable called `my_name` and assign it your name as a string.
2. Create a variable called `my_age` and assign it your age as an integer.
3. Create a variable called `my_height` and assign it your height in meters as a float (e.g., 1.75).
4. Create a variable called `is_student` and assign it `True` or `False`.
5. Print the type of each variable you created using `type()`.

Example solution:

```python
my_name = "Alice"
my_age = 25
my_height = 1.65
is_student = True

print(type(my_name))    # <class 'str'>
print(type(my_age))     # <class 'int'>
print(type(my_height))  # <class 'float'>
print(type(is_student)) # <class 'bool'>
```

# Key Takeaways

- Variables store values and are created using the `=` assignment operator
- Python has several data types: `int` (integers), `float` (decimals), `str` (text), and `bool` (True/False)
- Use `type()` to check what type a variable is
- Choose descriptive variable names that explain what they store
- Variable names must follow Python's naming rules

# Related Topics

- Basic Operations and Expressions (next lesson)
- Strings (Python Beginner #8)
- Type Conversion (covered in later lessons)
