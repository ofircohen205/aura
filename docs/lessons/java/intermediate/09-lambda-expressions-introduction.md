---
title: "Lambda Expressions Introduction"
language: java
difficulty: intermediate
prerequisites: ["Interfaces", "Collections Framework"]
keywords: [lambda expressions, functional interfaces, method references, anonymous classes, Java 8]
---

# Learning Objectives

- Understand what lambda expressions are
- Write lambda expressions
- Work with functional interfaces
- Use method references
- Replace anonymous classes with lambdas
- Use lambdas with collections

# Prerequisites

- Interfaces
- Collections Framework

# Introduction

Lambda expressions (introduced in Java 8) provide a concise way to represent anonymous functions. They enable functional programming style in Java and make code more readable, especially when working with collections. Understanding lambdas is essential for modern Java development.

# Core Concepts

## Basic Lambda Syntax

```java
// Old way: Anonymous class
Runnable r1 = new Runnable() {
    public void run() {
        System.out.println("Hello");
    }
};

// Lambda expression (equivalent)
Runnable r2 = () -> System.out.println("Hello");

// Execute
r1.run();
r2.run();
```

## Functional Interfaces

Interfaces with exactly one abstract method:

```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// Use lambda
Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> a * b;

System.out.println(add.calculate(5, 3));  // Output: 8
```

## Lambda with Parameters

```java
// Single parameter (parentheses optional)
Function<String, Integer> length = s -> s.length();

// Multiple parameters (parentheses required)
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;

// No parameters
Supplier<String> greeting = () -> "Hello, World!";
```

## Lambda with Collections

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Old way: Enhanced for loop
for (String name : names) {
    System.out.println(name);
}

// Lambda way: forEach
names.forEach(name -> System.out.println(name));

// Method reference (even shorter)
names.forEach(System.out::println);
```

## Method References

Shorthand for lambdas that call existing methods:

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Lambda
names.forEach(s -> System.out.println(s));

// Method reference
names.forEach(System.out::println);

// Static method reference
List<Integer> numbers = Arrays.asList(1, 2, 3);
numbers.stream().map(String::valueOf);  // Integer::valueOf
```

## Common Functional Interfaces

```java
import java.util.function.*;

// Predicate: boolean test(T t)
Predicate<String> isEmpty = s -> s.isEmpty();

// Function: R apply(T t)
Function<String, Integer> length = String::length;

// Consumer: void accept(T t)
Consumer<String> printer = System.out::println;

// Supplier: T get()
Supplier<String> generator = () -> "Hello";

// BiFunction: R apply(T t, U u)
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
```

# Common Mistakes

- **Wrong syntax**: `(a, b) -> a + b` not `(a, b) => a + b`
- **Using non-functional interfaces**: Must have exactly one abstract method
- **Not understanding method references**: Use `::` syntax
- **Overusing lambdas**: Sometimes a regular method is clearer

# Practice Exercises

1. Convert an anonymous class to a lambda expression.
2. Use lambda with forEach to print all elements of a list.
3. Create a Predicate lambda to filter a list of numbers.
4. Use method reference instead of lambda where possible.
5. Create a custom functional interface and use it with a lambda.

Example solution for exercise 2:

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
names.forEach(name -> System.out.println(name));

// Or with method reference
names.forEach(System.out::println);
```

# Key Takeaways

- Lambda expressions provide concise syntax for anonymous functions
- Syntax: `(parameters) -> expression` or `(parameters) -> { statements }`
- Work with functional interfaces (one abstract method)
- Method references are shorthand: `Class::method` or `object::method`
- Common functional interfaces: Predicate, Function, Consumer, Supplier
- Lambdas make collection operations more readable
- Introduced in Java 8 for functional programming style

# Related Topics

- Interfaces (Java Intermediate #5)
- Collections Framework (Java Intermediate #7)
- Streams (next lesson)
