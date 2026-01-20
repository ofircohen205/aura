---
title: "Basic Operations and Expressions"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types"]
keywords:
  [
    arithmetic,
    operations,
    addition,
    subtraction,
    multiplication,
    division,
    expressions,
    operators,
    order of operations,
  ]
---

# Learning Objectives

- Perform basic arithmetic operations (addition, subtraction, multiplication, division)
- Understand operator precedence and order of operations
- Use parentheses to control calculation order
- Work with different data types in expressions

# Prerequisites

- Variables and Data Types

# Introduction

Once you can store values in variables, the next step is to perform calculations with them. Python supports all the basic arithmetic operations you learned in math class, plus a few extras that are useful in programming.

# Core Concepts

## Arithmetic Operators

Python provides several arithmetic operators:

### Addition (+)

```python
result = 5 + 3
print(result)  # Output: 8

# Can also add variables
a = 10
b = 20
sum = a + b
print(sum)  # Output: 30
```

### Subtraction (-)

```python
result = 10 - 3
print(result)  # Output: 7

a = 50
b = 20
difference = a - b
print(difference)  # Output: 30
```

### Multiplication (\*)

```python
result = 4 * 5
print(result)  # Output: 20

a = 6
b = 7
product = a * b
print(product)  # Output: 42
```

### Division (/)

Division always returns a float, even if the result is a whole number.

```python
result = 10 / 2
print(result)  # Output: 5.0 (not 5!)

result = 7 / 2
print(result)  # Output: 3.5
```

### Floor Division (//)

Returns the whole number part of division (drops the decimal).

```python
result = 10 // 3
print(result)  # Output: 3 (not 3.333...)

result = 7 // 2
print(result)  # Output: 3
```

### Modulo (%)

Returns the remainder after division.

```python
result = 10 % 3
print(result)  # Output: 1 (10 divided by 3 is 3 with remainder 1)

result = 15 % 4
print(result)  # Output: 3
```

### Exponentiation (\*\*)

Raises a number to a power.

```python
result = 2 ** 3
print(result)  # Output: 8 (2 to the power of 3)

result = 5 ** 2
print(result)  # Output: 25 (5 squared)
```

## Order of Operations

Python follows the same order of operations as mathematics (PEMDAS):

1. Parentheses
2. Exponents
3. Multiplication and Division (left to right)
4. Addition and Subtraction (left to right)

```python
result = 2 + 3 * 4
print(result)  # Output: 14 (not 20!)
# Multiplication happens first: 3 * 4 = 12, then 2 + 12 = 14

result = (2 + 3) * 4
print(result)  # Output: 20
# Parentheses first: 2 + 3 = 5, then 5 * 4 = 20
```

## Combining Operations

You can combine multiple operations in a single expression:

```python
# Calculate the area of a rectangle
length = 10
width = 5
area = length * width
print(area)  # Output: 50

# Calculate the average of three numbers
num1 = 85
num2 = 90
num3 = 95
average = (num1 + num2 + num3) / 3
print(average)  # Output: 90.0
```

## String Operations

You can also use `+` with strings to concatenate (join) them:

```python
first_name = "Alice"
last_name = "Smith"
full_name = first_name + " " + last_name
print(full_name)  # Output: Alice Smith

# You can multiply strings too!
greeting = "Hello" * 3
print(greeting)  # Output: HelloHelloHello
```

# Common Mistakes

- **Forgetting that division returns a float**: `10 / 2` gives `5.0`, not `5`
- **Wrong order of operations**: `2 + 3 * 4` is `14`, not `20` (use parentheses if needed)
- **Mixing types incorrectly**: You can't do `"Hello" + 5` (string + number), but you can do `"Hello" + str(5)`
- **Using `^` for exponentiation**: Python uses `**`, not `^` (which is a different operator)

# Practice Exercises

1. Calculate the area of a circle with radius 5. (Hint: area = π × radius², use 3.14 for π)
2. Calculate how many full weeks are in 50 days, and how many days remain.
3. Create variables for a person's first name and last name, then create a full name by concatenating them with a space.
4. Calculate the average of the numbers 15, 23, 31, and 42.
5. Write an expression that calculates: (10 + 5) × 3 - 8

Example solutions:

```python
# Exercise 1
radius = 5
pi = 3.14
area = pi * radius ** 2
print(area)  # Output: 78.5

# Exercise 2
total_days = 50
weeks = total_days // 7
remaining_days = total_days % 7
print(f"{weeks} weeks and {remaining_days} days")  # Output: 7 weeks and 1 days

# Exercise 3
first_name = "John"
last_name = "Doe"
full_name = first_name + " " + last_name
print(full_name)  # Output: John Doe

# Exercise 4
average = (15 + 23 + 31 + 42) / 4
print(average)  # Output: 27.75

# Exercise 5
result = (10 + 5) * 3 - 8
print(result)  # Output: 37
```

# Key Takeaways

- Python supports basic arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Division (`/`) always returns a float
- Use `//` for integer division and `%` for remainder
- Python follows PEMDAS order of operations
- Use parentheses to control the order of calculations
- You can concatenate strings with `+` and repeat them with `*`

# Related Topics

- Variables and Data Types (previous lesson)
- Input and Output (next lesson)
- Strings (Python Beginner #8)
