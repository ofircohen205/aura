---
title: "Basic Operations"
language: java
difficulty: beginner
prerequisites: ["Variables and Data Types"]
keywords:
  [
    arithmetic,
    operators,
    addition,
    subtraction,
    multiplication,
    division,
    expressions,
    order of operations,
  ]
---

# Learning Objectives

- Perform basic arithmetic operations in Java
- Understand operator precedence
- Use parentheses to control calculation order
- Work with different data types in expressions
- Understand integer division vs floating-point division

# Prerequisites

- Variables and Data Types

# Introduction

Once you can store values in variables, the next step is to perform calculations with them. Java supports all the basic arithmetic operations, plus some additional operators that are useful in programming.

# Core Concepts

## Arithmetic Operators

Java provides several arithmetic operators:

### Addition (+)

```java
int a = 5;
int b = 3;
int sum = a + b;
System.out.println(sum);  // Output: 8

// Can also add directly
int result = 10 + 20;
System.out.println(result);  // Output: 30
```

### Subtraction (-)

```java
int a = 10;
int b = 3;
int difference = a - b;
System.out.println(difference);  // Output: 7
```

### Multiplication (\*)

```java
int a = 4;
int b = 5;
int product = a * b;
System.out.println(product);  // Output: 20
```

### Division (/)

Division behavior depends on the types involved:

```java
// Integer division (both operands are int)
int result = 10 / 3;
System.out.println(result);  // Output: 3 (not 3.333...)

// Floating-point division (at least one operand is double/float)
double result2 = 10.0 / 3;
System.out.println(result2);  // Output: 3.3333333333333335

double result3 = 10 / 3.0;
System.out.println(result3);  // Output: 3.3333333333333335
```

### Modulo (%)

Returns the remainder after division:

```java
int remainder = 10 % 3;
System.out.println(remainder);  // Output: 1 (10 divided by 3 is 3 with remainder 1)

int remainder2 = 15 % 4;
System.out.println(remainder2);  // Output: 3
```

## Order of Operations

Java follows the same order of operations as mathematics (PEMDAS):

1. Parentheses
2. Exponents (not a basic operator in Java)
3. Multiplication and Division (left to right)
4. Addition and Subtraction (left to right)

```java
int result = 2 + 3 * 4;
System.out.println(result);  // Output: 14 (not 20!)
// Multiplication happens first: 3 * 4 = 12, then 2 + 12 = 14

int result2 = (2 + 3) * 4;
System.out.println(result2);  // Output: 20
// Parentheses first: 2 + 3 = 5, then 5 * 4 = 20
```

## Compound Assignment Operators

Java provides shorthand operators for common operations:

```java
int x = 5;

x += 3;  // Same as: x = x + 3
System.out.println(x);  // Output: 8

x -= 2;  // Same as: x = x - 2
System.out.println(x);  // Output: 6

x *= 2;  // Same as: x = x * 2
System.out.println(x);  // Output: 12

x /= 3;  // Same as: x = x / 3
System.out.println(x);  // Output: 4

x %= 3;  // Same as: x = x % 3
System.out.println(x);  // Output: 1
```

## Increment and Decrement

Java provides operators to increase or decrease by 1:

```java
int count = 5;

// Post-increment (use value, then increment)
int a = count++;
System.out.println(a);    // Output: 5
System.out.println(count); // Output: 6

// Pre-increment (increment, then use value)
int b = ++count;
System.out.println(b);    // Output: 7
System.out.println(count); // Output: 7

// Decrement works the same way
count--;  // Decrease by 1
--count;  // Decrease by 1
```

## String Concatenation

The `+` operator also works with strings:

```java
String firstName = "Alice";
String lastName = "Smith";
String fullName = firstName + " " + lastName;
System.out.println(fullName);  // Output: Alice Smith

// Mixing strings and numbers
int age = 25;
String message = "I am " + age + " years old";
System.out.println(message);  // Output: I am 25 years old
```

# Common Mistakes

- **Integer division confusion**: `10 / 3` gives `3`, not `3.333...` (use `10.0 / 3` for decimal result)
- **Wrong order of operations**: `2 + 3 * 4` is `14`, not `20` (use parentheses if needed)
- **Forgetting parentheses**: Always use parentheses to clarify intent
- **Mixing types incorrectly**: Be careful when mixing int and double in calculations
- **Post-increment vs pre-increment**: `x++` uses value then increments, `++x` increments then uses value

# Practice Exercises

1. Calculate the area of a rectangle with length 10 and width 5.
2. Calculate how many full weeks are in 50 days, and how many days remain.
3. Write code that calculates: (10 + 5) \* 3 - 8
4. Create variables for a person's first and last name, then concatenate them with a space.
5. Calculate the average of the numbers 15, 23, 31, and 42.

Example solution for exercise 1:

```java
int length = 10;
int width = 5;
int area = length * width;
System.out.println("Area: " + area);  // Output: Area: 50
```

# Key Takeaways

- Java supports basic arithmetic: `+`, `-`, `*`, `/`, `%`
- Integer division (`int / int`) returns an integer (truncates decimal)
- Floating-point division requires at least one `double` or `float`
- Java follows PEMDAS order of operations
- Use parentheses to control calculation order
- Compound assignment operators (`+=`, `-=`, etc.) provide shorthand
- The `+` operator concatenates strings

# Related Topics

- Variables and Data Types (Java Beginner #2)
- Input and Output (next lesson)
- Conditionals (Java Beginner #5)
