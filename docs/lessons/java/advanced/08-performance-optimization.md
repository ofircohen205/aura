---
title: "Performance Optimization"
language: java
difficulty: advanced
prerequisites: ["All previous Java lessons"]
keywords: [performance, optimization, profiling, JVM, memory, garbage collection, bottlenecks]
---

# Learning Objectives

- Profile Java applications
- Identify performance bottlenecks
- Optimize memory usage
- Understand JVM tuning basics
- Optimize algorithms and data structures
- Use appropriate collections for performance

# Prerequisites

- All previous Java lessons

# Introduction

Performance optimization is about making code run faster and use resources efficiently. However, premature optimization is wasteful. The key is to measure first, identify bottlenecks, then optimize. Understanding Java performance helps you write efficient code when it matters.

# Core Concepts

## Measure First

Always profile before optimizing:

```java
long startTime = System.currentTimeMillis();
// Code to measure
long endTime = System.currentTimeMillis();
long duration = endTime - startTime;
System.out.println("Execution time: " + duration + "ms");
```

## Choose Right Data Structures

```java
// ArrayList vs LinkedList
List<String> arrayList = new ArrayList<>();  // Fast random access
List<String> linkedList = new LinkedList<>();  // Fast insertions/deletions

// HashMap vs TreeMap
Map<String, Integer> hashMap = new HashMap<>();  // O(1) average
Map<String, Integer> treeMap = new TreeMap<>();  // O(log n), sorted
```

## String Concatenation

```java
// Slow: Creates new String each time
String result = "";
for (int i = 0; i < 1000; i++) {
    result += "a";  // Creates new String object each time!
}

// Fast: Use StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append("a");
}
String result = sb.toString();
```

## Avoid Unnecessary Object Creation

```java
// Bad: Creates new object each time
for (int i = 0; i < 1000; i++) {
    String date = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
}

// Good: Reuse object
SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
for (int i = 0; i < 1000; i++) {
    String date = formatter.format(new Date());
}
```

## Use Primitives When Possible

```java
// Slower: Uses objects
List<Integer> numbers = new ArrayList<>();
for (Integer i = 0; i < 1000; i++) {  // Autoboxing overhead
    numbers.add(i);
}

// Faster: Use primitives
int[] numbers = new int[1000];
for (int i = 0; i < 1000; i++) {
    numbers[i] = i;
}
```

## Lazy Initialization

```java
class ExpensiveObject {
    private HeavyResource resource;

    public HeavyResource getResource() {
        if (resource == null) {
            resource = new HeavyResource();  // Create only when needed
        }
        return resource;
    }
}
```

# Common Mistakes

- **Premature optimization**: Measure first, optimize second
- **Micro-optimizations**: Focus on big bottlenecks
- **Ignoring algorithms**: Better algorithm > micro-optimization
- **Not profiling**: Don't guess where time is spent
- **Sacrificing readability**: Don't make code unreadable for small gains

# Practice Exercises

1. Profile a method and identify the slowest part.
2. Optimize string concatenation in a loop.
3. Compare performance of different collection types.
4. Optimize a method that processes a large dataset.
5. Use appropriate data structures for a specific use case.

Example solution for exercise 2:

```java
// Before (slow)
String result = "";
for (String word : words) {
    result += word + " ";
}

// After (fast)
StringBuilder sb = new StringBuilder();
for (String word : words) {
    sb.append(word).append(" ");
}
String result = sb.toString();
```

# Key Takeaways

- Always measure before optimizing
- Choose appropriate data structures
- Use StringBuilder for string concatenation in loops
- Avoid unnecessary object creation
- Use primitives when possible
- Profile to find actual bottlenecks
- Optimize algorithms before micro-optimizations
- Don't sacrifice readability for small performance gains

# Related Topics

- Collections Framework (Java Intermediate #7)
- All previous Java lessons
