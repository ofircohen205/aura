---
title: "Loops (for/while)"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Conditionals"]
keywords: [loops, for, while, iteration, range, break, continue, repetition]
---

# Learning Objectives

- Use `for` loops to repeat code a specific number of times
- Use `while` loops to repeat code while a condition is true
- Understand when to use `for` vs `while`
- Use `range()` to generate sequences of numbers
- Control loops with `break` and `continue`

# Prerequisites

- Variables and Data Types
- Conditionals

# Introduction

Often, you need to repeat the same code multiple times. Instead of writing the same code over and over, you can use loops. Python has two main types of loops: `for` loops (when you know how many times to repeat) and `while` loops (when you repeat until a condition is met).

# Core Concepts

## The for Loop

Use `for` loops when you know how many times to repeat or when iterating over a sequence.

```python
# Print numbers 1 to 5
for i in range(1, 6):
    print(i)

# Output:
# 1
# 2
# 3
# 4
# 5
```

## The range() Function

`range()` generates a sequence of numbers:

- `range(5)` - numbers 0 to 4 (5 numbers)
- `range(1, 6)` - numbers 1 to 5 (start at 1, stop before 6)
- `range(0, 10, 2)` - numbers 0, 2, 4, 6, 8 (start, stop, step)

```python
# Count from 0 to 4
for i in range(5):
    print(i)

# Count from 1 to 5
for i in range(1, 6):
    print(i)

# Count by 2s: 0, 2, 4, 6, 8
for i in range(0, 10, 2):
    print(i)
```

## Looping Over Lists

You can loop directly over items in a list:

```python
fruits = ["apple", "banana", "orange"]

for fruit in fruits:
    print(fruit)

# Output:
# apple
# banana
# orange
```

## The while Loop

Use `while` loops when you want to repeat until a condition becomes false.

```python
count = 0

while count < 5:
    print(count)
    count = count + 1  # Important: update the counter!

# Output:
# 0
# 1
# 2
# 3
# 4
```

## Controlling Loops

### break - Exit the Loop Early

```python
for i in range(10):
    if i == 5:
        break  # Exit the loop when i is 5
    print(i)

# Output: 0, 1, 2, 3, 4
```

### continue - Skip to Next Iteration

```python
for i in range(10):
    if i % 2 == 0:  # If i is even
        continue  # Skip the rest and go to next iteration
    print(i)

# Output: 1, 3, 5, 7, 9 (only odd numbers)
```

## Nested Loops

You can put loops inside other loops:

```python
# Print a multiplication table
for i in range(1, 4):
    for j in range(1, 4):
        print(f"{i} x {j} = {i * j}")
    print()  # Empty line between tables

# Output:
# 1 x 1 = 1
# 1 x 2 = 2
# 1 x 3 = 3
#
# 2 x 1 = 2
# 2 x 2 = 4
# 2 x 3 = 6
# ...
```

# Common Mistakes

- **Infinite while loops**: Forgetting to update the condition variable
- **Off-by-one errors**: `range(5)` gives 0-4, not 1-5
- **Using `=` instead of `==` in conditions**: `while count = 5` is wrong
- **Forgetting indentation**: Code inside the loop must be indented
- **Modifying a list while iterating**: Can cause unexpected behavior

# Practice Exercises

1. Write a program that prints all even numbers from 0 to 20.
2. Write a program that calculates the sum of numbers from 1 to 100.
3. Write a program that prints a countdown from 10 to 1, then prints "Blast off!".
4. Write a program that asks the user for a number and prints its multiplication table (1 to 10).
5. Write a program that finds the factorial of a number (5! = 5 × 4 × 3 × 2 × 1 = 120).

Example solution for exercise 2:

```python
total = 0

for i in range(1, 101):
    total = total + i

print(f"The sum is {total}")  # Output: The sum is 5050
```

# Key Takeaways

- Use `for` loops when you know how many times to repeat
- Use `while` loops when repeating until a condition is met
- `range()` generates sequences of numbers
- Always update the condition in `while` loops to avoid infinite loops
- Use `break` to exit a loop early
- Use `continue` to skip to the next iteration
- Loops can be nested (loop inside a loop)

# Related Topics

- Conditionals (Python Beginner #4)
- Functions (next lesson)
- Lists (Python Beginner #7)
