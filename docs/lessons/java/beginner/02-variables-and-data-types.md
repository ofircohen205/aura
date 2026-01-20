---
title: "Variables and Data Types"
language: java
difficulty: beginner
prerequisites: ["Introduction to Java"]
keywords:
  [
    variables,
    data types,
    primitive types,
    int,
    double,
    String,
    boolean,
    declaration,
    initialization,
  ]
---

# Learning Objectives

- Understand Java's primitive data types
- Declare and initialize variables
- Work with the String type
- Understand the difference between primitive types and reference types
- Use type casting when needed

# Prerequisites

- Introduction to Java

# Introduction

Variables are containers that store data in your program. Java is a statically-typed language, which means you must declare the type of each variable before using it. Java has two categories of data types: primitive types (like int, double) and reference types (like String, arrays, objects).

# Core Concepts

## Primitive Data Types

Java has eight primitive data types:

### Integer Types

```java
// int - 32-bit integer (most common)
int age = 25;
int count = 0;
int temperature = -5;

// long - 64-bit integer (for large numbers)
long population = 8000000000L;  // Note the 'L' suffix

// short - 16-bit integer (rarely used)
short smallNumber = 100;

// byte - 8-bit integer (rarely used)
byte tinyNumber = 127;
```

### Floating-Point Types

```java
// double - 64-bit floating point (most common)
double price = 19.99;
double pi = 3.14159;

// float - 32-bit floating point (less precise)
float height = 1.75f;  // Note the 'f' suffix
```

### Other Primitive Types

```java
// char - single character
char grade = 'A';
char firstLetter = 'Z';

// boolean - true or false
boolean isStudent = true;
boolean isGraduated = false;
```

## Reference Types

### String

`String` is a reference type (not primitive) but is used so commonly it's worth mentioning here:

```java
String name = "Alice";
String greeting = "Hello, World!";
String empty = "";  // Empty string
```

## Variable Declaration and Initialization

You can declare and initialize variables in different ways:

```java
// Declaration and initialization in one line
int age = 25;

// Declaration first, initialization later
int count;
count = 10;

// Multiple variables of same type
int x = 5, y = 10, z = 15;
```

## Type Casting

Sometimes you need to convert between types:

```java
// Implicit casting (automatic - smaller to larger)
int small = 5;
double large = small;  // int automatically converts to double

// Explicit casting (manual - larger to smaller)
double price = 19.99;
int rounded = (int) price;  // Casts to int, loses decimal part
System.out.println(rounded);  // Output: 19

// Casting between compatible types
char letter = 'A';
int ascii = (int) letter;
System.out.println(ascii);  // Output: 65
```

## Constants

Use `final` keyword to create constants (values that can't change):

```java
final int MAX_SIZE = 100;
final double PI = 3.14159;
final String COMPANY_NAME = "MyCompany";

// MAX_SIZE = 200;  // Error! Cannot modify final variable
```

## Variable Naming Rules

- Must start with a letter, underscore, or dollar sign
- Can contain letters, digits, underscores, and dollar signs
- Cannot be a Java keyword (like `int`, `class`, `public`)
- Are case-sensitive (`age` and `Age` are different)
- Use camelCase for variable names (e.g., `studentName`)

```java
// Good variable names
int studentAge = 20;
String firstName = "Alice";
boolean isEnrolled = true;

// Bad variable names (avoid these)
// int 2students;  // Can't start with number
// int student-age;  // Can't use hyphens
// int class;  // 'class' is a keyword
```

# Common Mistakes

- **Forgetting to initialize variables**: Local variables must be initialized before use
- **Using wrong type**: `int price = 19.99;` is wrong (use `double`)
- **Forgetting 'L' or 'f' suffixes**: `long big = 1000000000;` should be `1000000000L`
- **Case sensitivity**: `String` is different from `string` (Java is case-sensitive)
- **Trying to modify final variables**: `final` variables are constants

# Practice Exercises

1. Declare variables for a person's name (String), age (int), height (double), and student status (boolean).
2. Create a constant for the maximum number of students (100).
3. Write code that converts a double (19.99) to an int and prints the result.
4. Declare and initialize three integer variables in one statement.
5. Create a char variable with your first initial and print its ASCII value.

Example solution for exercise 1:

```java
String name = "Alice";
int age = 25;
double height = 1.65;
boolean isStudent = true;

System.out.println("Name: " + name);
System.out.println("Age: " + age);
System.out.println("Height: " + height);
System.out.println("Is Student: " + isStudent);
```

# Key Takeaways

- Java has 8 primitive types: `byte`, `short`, `int`, `long`, `float`, `double`, `char`, `boolean`
- `String` is a reference type, not primitive
- Variables must be declared with their type before use
- Use `final` to create constants
- Type casting converts between compatible types
- Java is case-sensitive and statically-typed
- Use camelCase for variable names

# Related Topics

- Introduction to Java (Java Beginner #1)
- Basic Operations (next lesson)
- Input and Output (Java Beginner #4)
