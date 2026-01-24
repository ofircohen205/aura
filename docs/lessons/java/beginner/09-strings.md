---
title: "Strings"
language: java
difficulty: beginner
prerequisites: ["Variables and Data Types", "Arrays"]
keywords: [strings, String class, methods, immutability, concatenation, manipulation]
---

# Learning Objectives

- Work with String objects in Java
- Use common String methods
- Understand String immutability
- Concatenate strings
- Compare strings properly

# Prerequisites

- Variables and Data Types
- Arrays

# Introduction

Strings represent sequences of characters (text) in Java. The `String` class provides many useful methods for working with text. Understanding strings is essential since most programs work with text data. In Java, strings are objects (not primitives) and are immutable (cannot be changed after creation).

# Core Concepts

## Creating Strings

You can create strings in several ways:

```java
// Method 1: String literal (most common)
String name = "Alice";

// Method 2: Using new keyword (less common)
String greeting = new String("Hello");

// Method 3: From character array
char[] chars = {'H', 'e', 'l', 'l', 'o'};
String word = new String(chars);
```

## String Concatenation

You can combine strings using the `+` operator:

```java
String firstName = "Alice";
String lastName = "Smith";
String fullName = firstName + " " + lastName;
System.out.println(fullName);  // Output: Alice Smith

// Can also concatenate with numbers
int age = 25;
String message = "I am " + age + " years old";
System.out.println(message);  // Output: I am 25 years old
```

## String Length

Use the `length()` method to get the number of characters:

```java
String text = "Hello";
System.out.println(text.length());  // Output: 5
```

## Common String Methods

### Case Conversion

```java
String text = "Hello World";

System.out.println(text.toUpperCase());  // Output: HELLO WORLD
System.out.println(text.toLowerCase());  // Output: hello world
```

### Finding and Checking

```java
String text = "Hello World";

// Check if contains substring
boolean contains = text.contains("World");
System.out.println(contains);  // Output: true

// Find index of substring
int index = text.indexOf("World");
System.out.println(index);  // Output: 6

// Check if starts/ends with
boolean starts = text.startsWith("Hello");
boolean ends = text.endsWith("World");
```

### Substrings

```java
String text = "Hello World";

// Get substring from index to end
String sub1 = text.substring(6);
System.out.println(sub1);  // Output: World

// Get substring from start to end (exclusive)
String sub2 = text.substring(0, 5);
System.out.println(sub2);  // Output: Hello
```

### Replacing

```java
String text = "Hello World";

// Replace all occurrences
String newText = text.replace("World", "Java");
System.out.println(newText);  // Output: Hello Java
```

### Splitting

```java
String text = "apple,banana,orange";
String[] fruits = text.split(",");

for (String fruit : fruits) {
    System.out.println(fruit);
}
// Output:
// apple
// banana
// orange
```

### Trimming

Remove whitespace from beginning and end:

```java
String text = "  Hello World  ";
String trimmed = text.trim();
System.out.println(trimmed);  // Output: Hello World
```

## String Immutability

Strings are immutable - you can't change them after creation:

```java
String text = "Hello";
// text[0] = 'h';  // Error! Can't modify strings

// Instead, create a new string
text = "h" + text.substring(1);
System.out.println(text);  // Output: hello
```

## Comparing Strings

**Important**: Use `.equals()` to compare string contents, not `==`:

```java
String str1 = "Hello";
String str2 = "Hello";
String str3 = new String("Hello");

// Wrong way (compares references, not content)
System.out.println(str1 == str2);   // Might be true (string pool)
System.out.println(str1 == str3);   // false (different objects)

// Correct way (compares content)
System.out.println(str1.equals(str2));  // true
System.out.println(str1.equals(str3));  // true

// Case-insensitive comparison
System.out.println("Hello".equalsIgnoreCase("hello"));  // true
```

## String Building

For many concatenations, use `StringBuilder` (more efficient):

```java
StringBuilder sb = new StringBuilder();
sb.append("Hello");
sb.append(" ");
sb.append("World");
String result = sb.toString();
System.out.println(result);  // Output: Hello World
```

# Common Mistakes

- **Using `==` to compare strings**: Always use `.equals()` for content comparison
- **Trying to modify strings directly**: Strings are immutable, create new ones
- **Forgetting that `length()` is a method**: Use `text.length()`, not `text.length`
- **Not handling null**: Check for null before calling methods
- **Inefficient concatenation in loops**: Use `StringBuilder` for many concatenations

# Practice Exercises

1. Write a method that takes a string and returns it reversed.
2. Write a method that counts how many times a character appears in a string.
3. Write a method that checks if a string is a palindrome (reads same forwards and backwards).
4. Write a method that takes a sentence and capitalizes the first letter of each word.
5. Write a method that removes all vowels from a string.

Example solution for exercise 1:

```java
public static String reverse(String text) {
    StringBuilder sb = new StringBuilder(text);
    return sb.reverse().toString();
}

String result = reverse("Hello");
System.out.println(result);  // Output: olleH
```

# Key Takeaways

- Strings are objects (reference types) in Java
- Strings are immutable - cannot be changed after creation
- Use `+` operator or `StringBuilder` for concatenation
- Always use `.equals()` to compare string content, not `==`
- Common methods: `length()`, `substring()`, `indexOf()`, `replace()`, `split()`
- Use `StringBuilder` for efficient string building in loops
- String literals are stored in the string pool

# Related Topics

- Variables and Data Types (Java Beginner #2)
- Arrays (Java Beginner #8)
- Basic Classes (next lesson)
