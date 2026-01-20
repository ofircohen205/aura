---
title: "Memory Management"
language: java
difficulty: advanced
prerequisites: ["Classes", "Collections Framework"]
keywords: [memory, garbage collection, JVM, heap, stack, memory leaks, optimization]
---

# Learning Objectives

- Understand Java memory model
- Understand heap vs stack
- Recognize memory leaks
- Understand garbage collection basics
- Optimize memory usage
- Use memory profiling tools

# Prerequisites

- Classes
- Collections Framework

# Introduction

Java manages memory automatically through garbage collection, but understanding how memory works helps you write efficient code and avoid memory leaks. Understanding memory management is essential for building applications that scale and perform well.

# Core Concepts

## Heap vs Stack

```java
// Stack: Local variables, method calls
public void method() {
    int x = 5;  // On stack
    String local = "hello";  // Reference on stack, object on heap
}

// Heap: Objects, arrays
String name = new String("Alice");  // Object on heap
int[] numbers = new int[100];  // Array on heap
```

## Garbage Collection

Automatic memory management:

```java
// Object becomes eligible for GC when no references
String str = new String("Hello");
str = null;  // Previous object can be garbage collected
str = new String("World");  // New object created
```

## Memory Leaks

Common causes:

```java
// 1. Static collections that grow
class Cache {
    private static Map<String, Object> cache = new HashMap<>();
    // Cache never cleared - memory leak!
}

// 2. Listeners not removed
class EventSource {
    private List<Listener> listeners = new ArrayList<>();
    // If listeners not removed, memory leak
}

// 3. Resources not closed
// Always use try-with-resources
try (FileReader file = new FileReader("data.txt")) {
    // File automatically closed
}
```

## Try-With-Resources

Automatic resource management:

```java
// Automatically closes resources
try (FileReader file = new FileReader("data.txt");
     BufferedReader reader = new BufferedReader(file)) {
    // Use resources
}  // Both automatically closed, even if exception occurs
```

## Weak References

Allow objects to be garbage collected:

```java
import java.lang.ref.WeakReference;

String strongRef = new String("Hello");
WeakReference<String> weakRef = new WeakReference<>(strongRef);

strongRef = null;  // Object can be GC'd
// weakRef.get() may return null if GC occurred
```

## Memory Profiling

Use tools to identify memory issues:

```java
// Add JVM options for profiling
// -XX:+PrintGCDetails
// -Xmx512m (max heap size)
// Use tools like VisualVM, JProfiler
```

# Common Mistakes

- **Memory leaks**: Not clearing collections, not removing listeners
- **Creating too many objects**: Reuse when possible
- **Not closing resources**: Use try-with-resources
- **Large object retention**: Keep references longer than needed
- **Not monitoring memory**: Use profiling tools

# Practice Exercises

1. Identify potential memory leaks in code.
2. Use try-with-resources to manage file resources.
3. Optimize code that creates many temporary objects.
4. Use appropriate collection sizes to avoid resizing.
5. Review code for unnecessary object retention.

Example solution for exercise 2:

```java
try (FileWriter writer = new FileWriter("output.txt");
     BufferedWriter bufferedWriter = new BufferedWriter(writer)) {
    bufferedWriter.write("Hello, World!");
}  // Resources automatically closed
```

# Key Takeaways

- Java manages memory automatically (garbage collection)
- Heap stores objects, stack stores local variables
- Memory leaks occur when objects aren't garbage collected
- Use try-with-resources for automatic resource management
- Monitor memory usage with profiling tools
- Avoid keeping unnecessary references
- Understand when objects become eligible for GC

# Related Topics

- Classes (Java Intermediate #1)
- Exception Handling (Java Intermediate #6)
- Performance Optimization (Java Advanced #8)
