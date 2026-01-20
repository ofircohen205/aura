---
title: "Conditionals (if/else)"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Basic Operations and Expressions"]
keywords: [conditionals, if, else, elif, comparison, boolean, decision making, control flow]
---

# Learning Objectives

- Use `if` statements to make decisions in your code
- Understand comparison operators
- Use `else` and `elif` for multiple conditions
- Write programs that respond differently based on conditions

# Prerequisites

- Variables and Data Types
- Basic Operations and Expressions

# Introduction

So far, your programs have executed line by line from top to bottom. But real programs need to make decisions - they need to do different things based on different conditions. In Python, we use `if`, `elif`, and `else` statements to control the flow of our program.

# Core Concepts

## The if Statement

The `if` statement checks a condition and executes code only if the condition is `True`.

```python
age = 18

if age >= 18:
    print("You are an adult")
```

## Comparison Operators

Python provides several operators to compare values:

- `==` - equal to
- `!=` - not equal to
- `<` - less than
- `>` - greater than
- `<=` - less than or equal to
- `>=` - greater than or equal to

```python
age = 20

if age >= 18:
    print("You can vote")

if age < 18:
    print("You cannot vote yet")

if age == 18:
    print("You just became an adult!")
```

## The else Clause

Use `else` to execute code when the condition is `False`.

```python
age = 15

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")
```

## The elif Clause

Use `elif` (short for "else if") to check multiple conditions in order.

```python
score = 85

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
elif score >= 60:
    print("Grade: D")
else:
    print("Grade: F")
```

## Multiple Conditions

You can combine conditions using `and`, `or`, and `not`:

```python
age = 25
has_license = True

# Using 'and' - both must be True
if age >= 18 and has_license:
    print("You can drive")

# Using 'or' - at least one must be True
if age < 18 or age > 65:
    print("You get a discount")

# Using 'not' - reverses the condition
if not has_license:
    print("You need a license to drive")
```

## Nested Conditionals

You can put `if` statements inside other `if` statements:

```python
age = 20
has_license = True

if age >= 18:
    if has_license:
        print("You can drive")
    else:
        print("You need a license")
else:
    print("You are too young to drive")
```

# Common Mistakes

- **Using `=` instead of `==`**: `if age = 18` is wrong (that's assignment), use `if age == 18`
- **Missing colon `:`**: `if age >= 18` is wrong, use `if age >= 18:`
- **Wrong indentation**: Python uses indentation to show what code belongs to the `if` block
- **Confusing `and` with `or`**: `and` means both must be true, `or` means at least one must be true

# Practice Exercises

1. Write a program that checks if a number is positive, negative, or zero.
2. Write a program that determines if a person can vote (must be 18 or older).
3. Write a program that assigns a letter grade based on a score (A: 90+, B: 80-89, C: 70-79, D: 60-69, F: below 60).
4. Write a program that checks if a year is a leap year (divisible by 4, but not by 100 unless also divisible by 400).
5. Write a program that checks if a number is even or odd.

Example solution for exercise 1:

```python
number = 5

if number > 0:
    print("Positive")
elif number < 0:
    print("Negative")
else:
    print("Zero")
```

# Key Takeaways

- Use `if` to check conditions and execute code conditionally
- Use `else` for the alternative case
- Use `elif` to check multiple conditions in order
- Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Combine conditions with `and`, `or`, and `not`
- Python uses indentation to show code blocks
- Always use `==` for comparison, not `=` (which is assignment)

# Related Topics

- Variables and Data Types (Python Beginner #1)
- Loops (next lesson)
- Boolean Logic (covered in this lesson)
