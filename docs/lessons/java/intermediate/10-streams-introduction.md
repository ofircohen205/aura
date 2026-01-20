---
title: "Streams Introduction"
language: java
difficulty: intermediate
prerequisites: ["Lambda Expressions Introduction", "Collections Framework"]
keywords: [streams, functional programming, map, filter, reduce, collect, pipeline, Java 8]
---

# Learning Objectives

- Understand what streams are
- Create and use streams
- Use stream operations (map, filter, reduce)
- Chain stream operations into pipelines
- Collect stream results
- Understand intermediate vs terminal operations

# Prerequisites

- Lambda Expressions Introduction
- Collections Framework

# Introduction

Streams (introduced in Java 8) provide a functional approach to processing collections of data. They enable declarative, pipeline-style operations that are often more readable than imperative loops. Understanding streams is essential for modern Java development.

# Core Concepts

## Creating Streams

```java
import java.util.stream.Stream;
import java.util.Arrays;
import java.util.List;

List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// From collection
Stream<String> stream1 = names.stream();

// From array
String[] array = {"a", "b", "c"};
Stream<String> stream2 = Arrays.stream(array);

// From values
Stream<String> stream3 = Stream.of("a", "b", "c");
```

## map() - Transform Elements

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// Transform to uppercase
List<String> upper = names.stream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());
// Output: [ALICE, BOB, CHARLIE]

// Transform to lengths
List<Integer> lengths = names.stream()
    .map(String::length)
    .collect(Collectors.toList());
// Output: [5, 3, 7]
```

## filter() - Keep Matching Elements

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Keep only even numbers
List<Integer> evens = numbers.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
// Output: [2, 4, 6, 8, 10]
```

## reduce() - Combine to Single Value

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// Sum all numbers
int sum = numbers.stream()
    .reduce(0, (a, b) -> a + b);
// Output: 15

// Or use method reference
int sum2 = numbers.stream()
    .reduce(0, Integer::sum);
```

## Pipeline Operations

Chain multiple operations:

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

List<String> result = names.stream()
    .filter(name -> name.length() > 3)      // Keep long names
    .map(String::toUpperCase)                // Convert to uppercase
    .sorted()                                // Sort alphabetically
    .collect(Collectors.toList());
// Output: [ALICE, CHARLIE, DAVID]
```

## Terminal Operations

Operations that produce a result:

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// Collect to list
List<Integer> list = numbers.stream().collect(Collectors.toList());

// Count elements
long count = numbers.stream().count();

// Find first
Optional<Integer> first = numbers.stream().findFirst();

// Check if any match
boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);

// Check if all match
boolean allPositive = numbers.stream().allMatch(n -> n > 0);
```

## Intermediate vs Terminal

```java
// Intermediate operations (lazy - don't execute until terminal)
Stream<String> stream = names.stream()
    .filter(s -> s.length() > 3)  // Intermediate
    .map(String::toUpperCase);     // Intermediate

// Terminal operation (triggers execution)
List<String> result = stream.collect(Collectors.toList());  // Terminal
```

# Common Mistakes

- **Forgetting terminal operation**: Streams are lazy, need terminal op
- **Reusing streams**: Streams can only be used once
- **Not understanding lazy evaluation**: Operations don't execute until terminal
- **Overusing streams**: Simple loops are sometimes clearer

# Practice Exercises

1. Use streams to find the sum of all even numbers in a list.
2. Use streams to convert a list of strings to their lengths.
3. Use streams to filter and transform a list of objects.
4. Chain multiple stream operations to process data.
5. Use streams to find the maximum value in a list.

Example solution for exercise 1:

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

int sum = numbers.stream()
    .filter(n -> n % 2 == 0)
    .reduce(0, Integer::sum);

System.out.println("Sum of evens: " + sum);  // Output: Sum of evens: 30
```

# Key Takeaways

- Streams provide functional approach to data processing
- Create streams from collections, arrays, or values
- `map()` transforms elements
- `filter()` keeps matching elements
- `reduce()` combines to single value
- Operations can be chained into pipelines
- Intermediate operations are lazy
- Terminal operations trigger execution
- Use `collect()` to gather results

# Related Topics

- Lambda Expressions Introduction (Java Intermediate #9)
- Collections Framework (Java Intermediate #7)
- Advanced Streams (Java Advanced #2)
