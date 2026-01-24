---
title: "Input and Output"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Basic Operations and Expressions"]
keywords: [input, output, print, user input, reading input, displaying output, console]
---

# Learning Objectives

- Use the `print()` function to display output
- Use the `input()` function to get user input
- Understand how to format output
- Convert string input to numbers when needed

# Prerequisites

- Variables and Data Types
- Basic Operations and Expressions

# Introduction

So far, we've worked with values that we define in our code. But real programs need to interact with users - they need to display information and get input. In Python, we use `print()` to show output and `input()` to get user input.

# Core Concepts

## Displaying Output with print()

The `print()` function displays text or values on the screen.

```python
# Print a simple message
print("Hello, World!")

# Print a variable
name = "Alice"
print(name)  # Output: Alice

# Print multiple items (separated by spaces)
print("Hello", "World")  # Output: Hello World

# Print with a custom separator
print("Python", "is", "fun", sep="-")  # Output: Python-is-fun
```

## Getting User Input with input()

The `input()` function reads text from the user. It always returns a string.

```python
# Get user input
name = input("What is your name? ")
print("Hello,", name)

# The prompt is optional
age = input()
print("You entered:", age)
```

## Converting Input to Numbers

Since `input()` always returns a string, you need to convert it to a number if you want to do math with it.

```python
# This won't work for math (age is a string)
age = input("How old are you? ")
# age + 5  # This would cause an error!

# Convert to integer
age = int(input("How old are you? "))
next_year = age + 1
print(f"Next year you'll be {next_year}")

# Convert to float
height = float(input("What is your height in meters? "))
print(f"Your height is {height} meters")
```

## Formatting Output

There are several ways to format output in Python:

### Using f-strings (Recommended)

```python
name = "Alice"
age = 25
print(f"My name is {name} and I am {age} years old")
# Output: My name is Alice and I am 25 years old
```

### Using .format()

```python
name = "Alice"
age = 25
print("My name is {} and I am {} years old".format(name, age))
```

### Using % formatting (Older style)

```python
name = "Alice"
age = 25
print("My name is %s and I am %d years old" % (name, age))
```

## Complete Example

Here's a simple program that gets user input and displays output:

```python
# Get user information
name = input("What is your name? ")
age = int(input("How old are you? "))
height = float(input("What is your height in meters? "))

# Display the information
print(f"\nHello, {name}!")
print(f"You are {age} years old")
print(f"Your height is {height} meters")

# Do some calculations
next_year_age = age + 1
print(f"Next year you'll be {next_year_age} years old")
```

# Common Mistakes

- **Forgetting that input() returns a string**: Always convert to `int()` or `float()` for numbers
- **Trying to do math with string input**: `age = input()` then `age + 1` will fail - convert first!
- **Not providing a prompt**: `input()` with no prompt can confuse users - always include a message
- **Forgetting quotes in print()**: `print(Hello)` is wrong, use `print("Hello")`

# Practice Exercises

1. Write a program that asks for the user's name and greets them.
2. Write a program that asks for two numbers and displays their sum.
3. Write a program that asks for the user's age and tells them how old they'll be in 10 years.
4. Write a program that asks for the radius of a circle and calculates and displays its area.
5. Write a program that asks for a person's first and last name, then displays their full name.

Example solution for exercise 2:

```python
# Get two numbers from user
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))

# Calculate and display sum
sum = num1 + num2
print(f"The sum of {num1} and {num2} is {sum}")
```

# Key Takeaways

- Use `print()` to display output to the user
- Use `input()` to get text input from the user (always returns a string)
- Convert string input to numbers using `int()` or `float()` when needed
- Use f-strings for easy and readable output formatting
- Always provide a clear prompt message with `input()`

# Related Topics

- Variables and Data Types (Python Beginner #1)
- Basic Operations and Expressions (Python Beginner #2)
- Conditionals (next lesson)
- Strings (Python Beginner #8)
