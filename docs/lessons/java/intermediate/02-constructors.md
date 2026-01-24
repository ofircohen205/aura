---
title: "Constructors"
language: java
difficulty: intermediate
prerequisites: ["Classes", "Methods"]
keywords: [constructors, initialization, constructor chaining, super, this, object creation]
---

# Learning Objectives

- Understand constructor purpose and usage
- Create default and parameterized constructors
- Use constructor chaining with `this()`
- Call parent constructors with `super()`
- Understand constructor overloading
- Initialize objects properly

# Prerequisites

- Classes
- Methods

# Introduction

Constructors are special methods that initialize objects when they're created. Understanding constructors is crucial for proper object initialization. This lesson covers constructor types, chaining, and best practices for object creation in Java.

# Core Concepts

## Default Constructor

Java provides a default constructor if you don't define one:

```java
public class Person {
    private String name;
    // Java provides: public Person() { }
}

Person p = new Person();  // Uses default constructor
```

## Parameterized Constructor

Accept parameters to initialize fields:

```java
public class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

Person person = new Person("Alice", 25);
```

## Constructor Overloading

Multiple constructors with different parameters:

```java
public class Rectangle {
    private double length;
    private double width;

    // Constructor 1: No parameters
    public Rectangle() {
        this.length = 1.0;
        this.width = 1.0;
    }

    // Constructor 2: Both dimensions
    public Rectangle(double length, double width) {
        this.length = length;
        this.width = width;
    }

    // Constructor 3: Square
    public Rectangle(double side) {
        this(side, side);  // Call constructor 2
    }
}
```

## Constructor Chaining

Call one constructor from another using `this()`:

```java
public class Student {
    private String name;
    private int age;
    private String major;

    public Student() {
        this("Unknown", 0, "Undeclared");
    }

    public Student(String name) {
        this(name, 0, "Undeclared");
    }

    public Student(String name, int age) {
        this(name, age, "Undeclared");
    }

    public Student(String name, int age, String major) {
        this.name = name;
        this.age = age;
        this.major = major;
    }
}
```

## Calling Parent Constructor

Use `super()` to call parent constructor:

```java
class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }
}

class Dog extends Animal {
    private String breed;

    public Dog(String name, String breed) {
        super(name);  // Call parent constructor
        this.breed = breed;
    }
}
```

## Constructor Rules

1. Constructor name must match class name
2. No return type (not even `void`)
3. `super()` or `this()` must be first statement (if used)
4. If no constructor defined, Java provides default
5. If constructor defined, default is not provided

# Common Mistakes

- **Giving constructor a return type**: Constructors have no return type
- **Calling `super()` or `this()` not first**: Must be first statement
- **Forgetting `super()` in subclass**: Must call parent constructor
- **Not initializing all fields**: Should initialize all important fields
- **Circular constructor calls**: `this()` calling itself causes error

# Practice Exercises

1. Create a class with a default constructor and a parameterized constructor.
2. Create a class with constructor chaining (multiple constructors calling each other).
3. Create a subclass that properly calls the parent constructor.
4. Create a class with constructor overloading for different initialization scenarios.
5. Create a class where constructors validate input parameters.

Example solution for exercise 2:

```java
public class Book {
    private String title;
    private String author;
    private int year;

    public Book() {
        this("Unknown", "Unknown", 0);
    }

    public Book(String title) {
        this(title, "Unknown", 0);
    }

    public Book(String title, String author) {
        this(title, author, 0);
    }

    public Book(String title, String author, int year) {
        this.title = title;
        this.author = author;
        this.year = year;
    }
}
```

# Key Takeaways

- Constructors initialize objects when created
- Default constructor provided if none defined
- Parameterized constructors accept initialization values
- Constructor overloading allows multiple ways to create objects
- Use `this()` for constructor chaining
- Use `super()` to call parent constructor
- `super()` or `this()` must be first statement
- Constructors have no return type

# Related Topics

- Classes (Java Intermediate #1)
- Inheritance (next lesson)
- Methods (Java Beginner #7)
