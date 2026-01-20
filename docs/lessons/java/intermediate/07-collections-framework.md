---
title: "Collections Framework"
language: java
difficulty: intermediate
prerequisites: ["Arrays", "Interfaces"]
keywords: [collections, ArrayList, HashMap, Set, List, Map, generics, iterators]
---

# Learning Objectives

- Understand the Java Collections Framework
- Work with List, Set, and Map interfaces
- Use ArrayList, HashSet, HashMap
- Understand when to use each collection type
- Use iterators to traverse collections
- Work with generics in collections

# Prerequisites

- Arrays
- Interfaces

# Introduction

The Collections Framework provides a set of classes and interfaces for storing and manipulating groups of objects. It's more powerful and flexible than arrays. Understanding collections is essential for working with data in Java applications.

# Core Concepts

## List Interface

Ordered collection that allows duplicates:

```java
import java.util.ArrayList;
import java.util.List;

List<String> names = new ArrayList<>();
names.add("Alice");
names.add("Bob");
names.add("Alice");  // Duplicates allowed

System.out.println(names.get(0));  // Output: Alice
System.out.println(names.size());  // Output: 3
```

## Set Interface

Collection that doesn't allow duplicates:

```java
import java.util.HashSet;
import java.util.Set;

Set<String> uniqueNames = new HashSet<>();
uniqueNames.add("Alice");
uniqueNames.add("Bob");
uniqueNames.add("Alice");  // Duplicate ignored

System.out.println(uniqueNames.size());  // Output: 2
```

## Map Interface

Key-value pairs:

```java
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> ages = new HashMap<>();
ages.put("Alice", 25);
ages.put("Bob", 30);

System.out.println(ages.get("Alice"));  // Output: 25
System.out.println(ages.containsKey("Bob"));  // Output: true
```

## Common List Operations

```java
List<String> list = new ArrayList<>();

// Add elements
list.add("Apple");
list.add("Banana");
list.add(0, "Orange");  // Insert at index

// Access elements
String first = list.get(0);
int index = list.indexOf("Banana");

// Remove elements
list.remove("Apple");
list.remove(0);

// Iterate
for (String item : list) {
    System.out.println(item);
}
```

## Common Map Operations

```java
Map<String, Integer> map = new HashMap<>();

// Add/update
map.put("Alice", 25);
map.put("Bob", 30);

// Get value
Integer age = map.get("Alice");

// Check existence
boolean hasKey = map.containsKey("Alice");
boolean hasValue = map.containsValue(25);

// Iterate
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

## Iterators

```java
List<String> list = new ArrayList<>();
list.add("Apple");
list.add("Banana");

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String item = iterator.next();
    System.out.println(item);
}
```

## Generics with Collections

```java
// Without generics (old way, not recommended)
List list = new ArrayList();
list.add("Hello");
String str = (String) list.get(0);  // Need cast

// With generics (type-safe)
List<String> list = new ArrayList<>();
list.add("Hello");
String str = list.get(0);  // No cast needed
```

# Common Mistakes

- **Not using generics**: Always use generics for type safety
- **Using wrong collection type**: List vs Set vs Map
- **Modifying collection while iterating**: Use Iterator.remove()
- **Not checking null**: Map.get() returns null if key doesn't exist
- **Confusing List and Set**: List allows duplicates, Set doesn't

# Practice Exercises

1. Create an ArrayList of integers and find the sum of all numbers.
2. Create a HashSet to store unique email addresses.
3. Create a HashMap that maps student names to their grades.
4. Iterate through a Map and print all key-value pairs.
5. Remove duplicates from a List using a Set.

Example solution for exercise 1:

```java
List<Integer> numbers = new ArrayList<>();
numbers.add(10);
numbers.add(20);
numbers.add(30);

int sum = 0;
for (int num : numbers) {
    sum += num;
}
System.out.println("Sum: " + sum);  // Output: Sum: 60
```

# Key Takeaways

- Collections Framework provides data structures
- List: Ordered, allows duplicates (ArrayList, LinkedList)
- Set: No duplicates (HashSet, TreeSet)
- Map: Key-value pairs (HashMap, TreeMap)
- Always use generics for type safety
- Use iterators to traverse collections
- Choose the right collection type for your needs
- Collections are more flexible than arrays

# Related Topics

- Arrays (Java Beginner #8)
- Interfaces (Java Intermediate #5)
- Generics (Java Advanced #1)
