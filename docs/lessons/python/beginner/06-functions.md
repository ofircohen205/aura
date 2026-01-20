---
title: "Functions"
language: python
difficulty: beginner
prerequisites: ["Variables and Data Types", "Loops", "Conditionals"]
keywords: [functions, def, parameters, arguments, return, reusable code, modularity]
---

# Learning Objectives

- Understand what functions are and why we use them
- Learn how to define functions using `def`
- Pass arguments to functions
- Return values from functions
- Understand the difference between parameters and arguments

# Prerequisites

- Variables and Data Types
- Loops
- Conditionals

# Introduction

Functions are reusable blocks of code that perform a specific task. Instead of writing the same code multiple times, you can write it once in a function and call that function whenever you need it. Functions make your code more organized, easier to read, and easier to maintain.

# Core Concepts

## Defining a Function

You define a function using the `def` keyword:

```python
def greet():
    print("Hello, World!")

# Call the function
greet()  # Output: Hello, World!
```

## Functions with Parameters

Parameters are variables that receive values when the function is called:

```python
def greet(name):
    print(f"Hello, {name}!")

# Call the function with an argument
greet("Alice")  # Output: Hello, Alice!
greet("Bob")    # Output: Hello, Bob!
```

## Functions with Multiple Parameters

You can define functions with multiple parameters:

```python
def add_numbers(a, b):
    result = a + b
    print(f"{a} + {b} = {result}")

add_numbers(5, 3)   # Output: 5 + 3 = 8
add_numbers(10, 20) # Output: 10 + 20 = 30
```

## Returning Values

Use `return` to send a value back from the function:

```python
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)  # Output: 8

# You can use the returned value directly
print(add_numbers(10, 20))  # Output: 30
```

## Functions with Default Parameters

You can provide default values for parameters:

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")              # Output: Hello, Alice!
greet("Bob", "Hi")          # Output: Hi, Bob!
greet("Charlie", "Goodbye") # Output: Goodbye, Charlie!
```

## Functions Without Return

If a function doesn't have a `return` statement, it returns `None`:

```python
def print_message(message):
    print(message)

result = print_message("Hello")
print(result)  # Output: None
```

## Local vs Global Variables

Variables inside a function are local to that function:

```python
def my_function():
    local_var = "I'm local"
    print(local_var)

my_function()  # Output: I'm local
# print(local_var)  # Error! local_var doesn't exist outside the function

# Global variable
global_var = "I'm global"

def another_function():
    print(global_var)  # Can access global variables

another_function()  # Output: I'm global
```

# Common Mistakes

- **Forgetting the colon `:`**: `def my_function()` is wrong, use `def my_function():`
- **Confusing parameters and arguments**: Parameters are in the definition, arguments are what you pass
- **Not returning a value when needed**: If you need the result, use `return`
- **Trying to use local variables outside the function**: Local variables only exist inside the function
- **Missing parentheses when calling**: `greet` is the function object, `greet()` calls it

# Practice Exercises

1. Write a function called `square` that takes a number and returns its square.
2. Write a function called `is_even` that takes a number and returns `True` if it's even, `False` otherwise.
3. Write a function called `greet_user` that takes a name and an optional greeting (default "Hello") and prints a greeting.
4. Write a function called `calculate_area` that takes length and width and returns the area of a rectangle.
5. Write a function called `max_of_three` that takes three numbers and returns the largest one.

Example solution for exercise 1:

```python
def square(number):
    return number * number

result = square(5)
print(result)  # Output: 25
```

# Key Takeaways

- Functions are reusable blocks of code defined with `def`
- Parameters receive values, arguments are what you pass when calling
- Use `return` to send a value back from a function
- Functions can have default parameter values
- Variables inside functions are local to that function
- Functions make code more organized and reusable

# Related Topics

- Variables and Data Types (Python Beginner #1)
- Loops (Python Beginner #5)
- Lists (next lesson)
- Error Handling (Python Beginner #10)
