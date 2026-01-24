---
title: "Advanced Streams"
language: java
difficulty: advanced
prerequisites: ["Streams Introduction", "Lambda Expressions Introduction"]
keywords:
  [streams, parallel streams, collectors, grouping, partitioning, flatMap, advanced operations]
---

# Learning Objectives

- Use advanced stream operations
- Work with Collectors for complex aggregations
- Use groupingBy and partitioningBy
- Understand flatMap for nested structures
- Use parallel streams
- Combine multiple stream operations effectively

# Prerequisites

- Streams Introduction
- Lambda Expressions Introduction

# Introduction

Advanced streams cover complex operations like grouping, partitioning, flatMap, and parallel processing. These features enable sophisticated data processing pipelines. Understanding advanced streams helps you write efficient, declarative data processing code.

# Core Concepts

## flatMap()

Flatten nested structures:

```java
List<List<String>> nested = Arrays.asList(
    Arrays.asList("a", "b"),
    Arrays.asList("c", "d")
);

List<String> flat = nested.stream()
    .flatMap(List::stream)
    .collect(Collectors.toList());
// Output: [a, b, c, d]
```

## Grouping

Group elements by a criterion:

```java
import java.util.stream.Collectors;

List<String> words = Arrays.asList("apple", "banana", "apricot", "cherry");

// Group by first letter
Map<Character, List<String>> grouped = words.stream()
    .collect(Collectors.groupingBy(s -> s.charAt(0)));
// {a=[apple, apricot], b=[banana], c=[cherry]}
```

## Partitioning

Split into two groups:

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Partition into even and odd
Map<Boolean, List<Integer>> partitioned = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
// {false=[1, 3, 5, 7, 9], true=[2, 4, 6, 8, 10]}
```

## Advanced Collectors

```java
// Joining strings
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
String joined = names.stream()
    .collect(Collectors.joining(", "));
// Output: "Alice, Bob, Charlie"

// Counting
long count = names.stream()
    .collect(Collectors.counting());

// Summarizing statistics
IntSummaryStatistics stats = numbers.stream()
    .collect(Collectors.summarizingInt(Integer::intValue));
// Get: count, sum, min, max, average
```

## Parallel Streams

Process in parallel:

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// Sequential
int sum1 = numbers.stream()
    .mapToInt(Integer::intValue)
    .sum();

// Parallel
int sum2 = numbers.parallelStream()
    .mapToInt(Integer::intValue)
    .sum();
```

## Complex Pipelines

```java
List<Person> people = // ... list of Person objects

Map<String, Double> avgAgeByCity = people.stream()
    .filter(p -> p.getAge() >= 18)
    .collect(Collectors.groupingBy(
        Person::getCity,
        Collectors.averagingInt(Person::getAge)
    ));
```

# Common Mistakes

- **Using parallel streams unnecessarily**: Sequential is often faster for small data
- **Stateful operations in parallel**: Can cause issues
- **Not understanding flatMap**: Different from map
- **Over-complicating**: Simple operations are sometimes clearer

# Practice Exercises

1. Use flatMap to flatten a list of lists.
2. Group a list of objects by a property.
3. Partition a list into two groups based on a condition.
4. Create a complex stream pipeline with multiple operations.
5. Use parallel streams to process a large dataset.

Example solution for exercise 1:

```java
List<List<Integer>> nested = Arrays.asList(
    Arrays.asList(1, 2, 3),
    Arrays.asList(4, 5),
    Arrays.asList(6, 7, 8, 9)
);

List<Integer> flat = nested.stream()
    .flatMap(List::stream)
    .collect(Collectors.toList());
// Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

# Key Takeaways

- `flatMap()` flattens nested structures
- `groupingBy()` groups elements by a function
- `partitioningBy()` splits into two groups
- Collectors provide powerful aggregation operations
- Parallel streams enable concurrent processing
- Use parallel streams carefully - not always faster
- Complex pipelines enable sophisticated data processing

# Related Topics

- Streams Introduction (Java Intermediate #10)
- Lambda Expressions Introduction (Java Intermediate #9)
- Collections Framework (Java Intermediate #7)
