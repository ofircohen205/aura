---
title: "Advanced Generics"
language: java
difficulty: advanced
prerequisites: ["Generics Introduction", "Collections Framework"]
keywords: [generics, wildcards, bounded types, type erasure, generic methods, PECS principle]
---

# Learning Objectives

- Master wildcard usage
- Understand bounded wildcards (extends, super)
- Work with multiple type parameters
- Understand type erasure
- Apply PECS principle (Producer Extends, Consumer Super)
- Create complex generic utilities

# Prerequisites

- Generics Introduction
- Collections Framework

# Introduction

Advanced generics cover wildcards, bounded types, and understanding how Java's type erasure works. These concepts enable you to write more flexible generic code while maintaining type safety. Understanding advanced generics is essential for working with complex generic APIs and creating reusable libraries.

# Core Concepts

## Wildcard Types

```java
// Unbounded wildcard
void printList(List<?> list) {
    for (Object item : list) {
        System.out.println(item);
    }
}

// Upper bounded wildcard
void processNumbers(List<? extends Number> numbers) {
    for (Number num : numbers) {
        System.out.println(num.doubleValue());
    }
}

// Lower bounded wildcard
void addIntegers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
}
```

## PECS Principle

Producer Extends, Consumer Super:

```java
// Producer (read from) - use extends
public static <T> void copy(List<? extends T> src, List<? super T> dest) {
    for (T item : src) {
        dest.add(item);
    }
}

// Consumer (write to) - use super
List<Number> numbers = new ArrayList<>();
List<Integer> integers = Arrays.asList(1, 2, 3);
copy(integers, numbers);  // OK
```

## Multiple Type Parameters

```java
class Pair<T, U> {
    private T first;
    private U second;

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    public T getFirst() { return first; }
    public U getSecond() { return second; }
}

Pair<String, Integer> pair = new Pair<>("Alice", 25);
```

## Type Erasure

Generics are removed at runtime:

```java
// At compile time
List<String> strings = new ArrayList<>();
List<Integer> integers = new ArrayList<>();

// At runtime (after erasure)
// Both are just List (raw type)
// This is why you can't do: if (list instanceof List<String>)
```

## Generic Methods with Wildcards

```java
public static <T extends Comparable<? super T>> T max(List<? extends T> list) {
    if (list.isEmpty()) {
        throw new IllegalArgumentException("List is empty");
    }
    T max = list.get(0);
    for (T item : list) {
        if (item.compareTo(max) > 0) {
            max = item;
        }
    }
    return max;
}
```

# Common Mistakes

- **Confusing extends and super**: `extends` = upper bound, `super` = lower bound
- **Not understanding PECS**: Use extends for producers, super for consumers
- **Trying to use instanceof with generics**: Doesn't work due to type erasure
- **Raw types**: Avoid using raw types, always use generics

# Practice Exercises

1. Create a method that copies elements using PECS principle.
2. Create a generic method that finds maximum using bounded wildcards.
3. Create a class with multiple type parameters.
4. Use upper and lower bounded wildcards in method parameters.
5. Create a utility class with advanced generic methods.

Example solution for exercise 1:

```java
public static <T> void copy(List<? extends T> src, List<? super T> dest) {
    dest.addAll(src);
}

List<Integer> integers = Arrays.asList(1, 2, 3);
List<Number> numbers = new ArrayList<>();
copy(integers, numbers);  // OK - Integer extends Number
```

# Key Takeaways

- Wildcards provide flexibility: `?`, `? extends T`, `? super T`
- PECS: Producer Extends, Consumer Super
- Upper bound (`extends`) for reading
- Lower bound (`super`) for writing
- Type erasure removes generics at runtime
- Multiple type parameters enable complex types
- Advanced generics enable flexible, type-safe APIs

# Related Topics

- Generics Introduction (Java Intermediate #8)
- Collections Framework (Java Intermediate #7)
- Streams (Java Intermediate #10)
