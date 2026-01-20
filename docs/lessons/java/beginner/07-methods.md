---
title: "Methods"
language: java
difficulty: beginner
prerequisites: ["Functions", "Variables and Data Types"]
keywords: [methods, functions, parameters, return types, void, reusable code, modularity]
---

# Learning Objectives

- Understand what methods are and why we use them
- Learn how to define and call methods
- Pass arguments to methods
- Return values from methods
- Understand method overloading

# Prerequisites

- Functions (basic programming concept)
- Variables and Data Types

# Introduction

Methods are reusable blocks of code that perform a specific task. In Java, all code must be inside methods (which are inside classes). Methods make your code more organized, easier to read, and easier to maintain. Understanding methods is essential for writing well-structured Java programs.

# Core Concepts

## Defining Methods

You define methods inside a class:

```java
public class Example {
    // Method definition
    public static void greet() {
        System.out.println("Hello, World!");
    }

    public static void main(String[] args) {
        greet();  // Call the method
    }
}
```

## Method Syntax

```java
[access modifier] [static] [return type] [method name]([parameters]) {
    // method body
}
```

Example:

```java
public static int add(int a, int b) {
    return a + b;
}
```

## Methods with Parameters

Parameters receive values when the method is called:

```java
public static void greet(String name) {
    System.out.println("Hello, " + name + "!");
}

// Call the method
greet("Alice");  // Output: Hello, Alice!
```

## Methods with Return Values

Use `return` to send a value back:

```java
public static int add(int a, int b) {
    return a + b;
}

int result = add(5, 3);
System.out.println(result);  // Output: 8
```

## The void Return Type

Use `void` when a method doesn't return a value:

```java
public static void printMessage(String message) {
    System.out.println(message);
    // No return statement needed
}
```

## Method Overloading

You can have multiple methods with the same name but different parameters:

```java
public static int add(int a, int b) {
    return a + b;
}

public static double add(double a, double b) {
    return a + b;
}

public static int add(int a, int b, int c) {
    return a + b + c;
}

// All three can be used
System.out.println(add(5, 3));        // Uses first method
System.out.println(add(5.5, 3.2));    // Uses second method
System.out.println(add(1, 2, 3));     // Uses third method
```

## Static vs Instance Methods

### Static Methods

Belong to the class, called using the class name:

```java
public class MathUtils {
    public static int square(int x) {
        return x * x;
    }
}

// Call static method
int result = MathUtils.square(5);
```

### Instance Methods

Belong to an object, called on an instance (covered in OOP lessons):

```java
// Will be covered in intermediate lessons
```

# Common Mistakes

- **Forgetting the return type**: Must specify `void` or a type
- **Not returning a value**: Methods with non-void return type must return a value
- **Wrong parameter types**: Parameters must match when calling
- **Missing static keyword**: Static methods need `static` keyword
- **Method name conflicts**: Can't have two methods with same signature

# Practice Exercises

1. Write a method called `square` that takes a number and returns its square.
2. Write a method called `isEven` that takes a number and returns `true` if it's even, `false` otherwise.
3. Write a method called `greetUser` that takes a name and prints a greeting.
4. Write a method called `calculateArea` that takes length and width and returns the area of a rectangle.
5. Write an overloaded method `max` that finds the maximum of two numbers (both int and double versions).

Example solution for exercise 1:

```java
public static int square(int number) {
    return number * number;
}

int result = square(5);
System.out.println(result);  // Output: 25
```

# Key Takeaways

- Methods are reusable blocks of code defined inside classes
- Methods can take parameters and return values
- Use `void` for methods that don't return a value
- Use `return` to send a value back from a method
- Method overloading allows multiple methods with the same name
- Static methods belong to the class, not instances
- Methods make code more organized and reusable

# Related Topics

- Variables and Data Types (Java Beginner #2)
- Arrays (next lesson)
- Classes (Java Intermediate #1)
