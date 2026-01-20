---
title: "Generics Introduction"
language: java
difficulty: intermediate
prerequisites: ["Collections Framework", "Classes"]
keywords: [generics, type parameters, type safety, generic classes, generic methods, wildcards]
---

# Learning Objectives

- Understand what generics are and why they're useful
- Create generic classes and methods
- Use generics with collections
- Understand type erasure
- Work with bounded type parameters
- Use wildcards

# Prerequisites

- Collections Framework
- Classes

# Introduction

Generics allow you to create classes, interfaces, and methods that work with different types while maintaining type safety. They eliminate the need for casting and enable compile-time type checking. Understanding generics is essential for working with the Collections Framework and writing reusable, type-safe code.

# Core Concepts

## Generic Classes

```java
class Box<T> {
    private T contents;

    public void set(T contents) {
        this.contents = contents;
    }

    public T get() {
        return contents;
    }
}

// Usage
Box<String> stringBox = new Box<>();
stringBox.set("Hello");
String value = stringBox.get();  // No cast needed

Box<Integer> intBox = new Box<>();
intBox.set(42);
Integer number = intBox.get();
```

## Generic Methods

```java
public class Utils {
    public static <T> void swap(T[] array, int i, int j) {
        T temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}

// Usage
String[] words = {"Hello", "World"};
Utils.swap(words, 0, 1);
```

## Bounded Type Parameters

Limit what types can be used:

```java
class NumberBox<T extends Number> {
    private T number;

    public NumberBox(T number) {
        this.number = number;
    }

    public double getDoubleValue() {
        return number.doubleValue();  // Can call Number methods
    }
}

// Usage
NumberBox<Integer> intBox = new NumberBox<>(42);
NumberBox<Double> doubleBox = new NumberBox<>(3.14);
// NumberBox<String> stringBox = new NumberBox<>("hello");  // Error!
```

## Wildcards

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
void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
}
```

## Generics with Collections

```java
// Type-safe collections
List<String> names = new ArrayList<>();
names.add("Alice");
String name = names.get(0);  // No cast needed

Map<String, Integer> ages = new HashMap<>();
ages.put("Alice", 25);
Integer age = ages.get("Alice");  // Type-safe
```

# Common Mistakes

- **Using raw types**: Always use generics, avoid raw types
- **Not understanding type erasure**: Generics are removed at runtime
- **Confusing extends and super**: `extends` = upper bound, `super` = lower bound
- **Overusing wildcards**: Use specific types when possible

# Practice Exercises

1. Create a generic class for a stack data structure.
2. Create a generic method that finds the maximum element in an array.
3. Create a generic class with bounded type parameters.
4. Use wildcards in a method that processes a list of numbers.
5. Create a generic utility class with multiple type parameters.

Example solution for exercise 1:

```java
class Stack<T> {
    private List<T> elements = new ArrayList<>();

    public void push(T item) {
        elements.add(item);
    }

    public T pop() {
        if (elements.isEmpty()) {
            throw new RuntimeException("Stack is empty");
        }
        return elements.remove(elements.size() - 1);
    }

    public boolean isEmpty() {
        return elements.isEmpty();
    }
}

Stack<String> stack = new Stack<>();
stack.push("First");
stack.push("Second");
System.out.println(stack.pop());  // Output: Second
```

# Key Takeaways

- Generics provide type safety without casting
- Use `<T>` syntax for type parameters
- Generic classes and methods work with multiple types
- Bounded type parameters limit what types can be used
- Wildcards provide flexibility: `?`, `? extends T`, `? super T`
- Generics are erased at runtime (type erasure)
- Always use generics with collections

# Related Topics

- Collections Framework (Java Intermediate #7)
- Classes (Java Intermediate #1)
- Advanced Generics (Java Advanced #1)
