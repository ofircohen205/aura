---
title: "Classes"
language: java
difficulty: intermediate
prerequisites: ["Basic Classes", "Methods"]
keywords:
  [classes, constructors, this, access modifiers, encapsulation, object-oriented programming]
---

# Learning Objectives

- Create well-structured classes
- Use constructors effectively
- Understand access modifiers (public, private, protected)
- Implement encapsulation
- Use the `this` keyword
- Create multiple constructors

# Prerequisites

- Basic Classes
- Methods

# Introduction

Classes are the foundation of object-oriented programming in Java. While you learned the basics earlier, intermediate classes cover constructors, access modifiers, and proper encapsulation. Understanding these concepts is essential for writing maintainable, secure Java code.

# Core Concepts

## Constructors

Special methods that initialize objects:

```java
public class Person {
    private String name;
    private int age;

    // Default constructor (no parameters)
    public Person() {
        this.name = "Unknown";
        this.age = 0;
    }

    // Parameterized constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Constructor chaining
    public Person(String name) {
        this(name, 0);  // Calls other constructor
    }
}
```

## The `this` Keyword

Refers to the current object:

```java
public class Person {
    private String name;

    public Person(String name) {
        this.name = name;  // this.name refers to instance variable
    }

    public void setName(String name) {
        this.name = name;  // Distinguish parameter from field
    }
}
```

## Access Modifiers

Control visibility of class members:

```java
public class BankAccount {
    public double balance;        // Accessible everywhere
    private String accountNumber; // Only in this class
    protected String owner;       // In this class and subclasses

    // No modifier (package-private) - accessible in same package
    String internalId;
}
```

## Encapsulation

Hide implementation details:

```java
public class BankAccount {
    private double balance;  // Private - can't access directly

    // Public methods to access/modify
    public double getBalance() {
        return balance;
    }

    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }

    public void withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
        }
    }
}
```

## Multiple Constructors

```java
public class Rectangle {
    private double length;
    private double width;

    // Constructor 1: No parameters
    public Rectangle() {
        this(1.0, 1.0);  // Call other constructor
    }

    // Constructor 2: Both parameters
    public Rectangle(double length, double width) {
        this.length = length;
        this.width = width;
    }

    // Constructor 3: Square (same length and width)
    public Rectangle(double side) {
        this(side, side);  // Call constructor 2
    }
}
```

## Static Members

Belong to the class, not instances:

```java
public class MathUtils {
    // Static variable
    public static final double PI = 3.14159;

    // Static method
    public static double circleArea(double radius) {
        return PI * radius * radius;
    }
}

// Use without creating instance
double area = MathUtils.circleArea(5.0);
```

# Common Mistakes

- **Not using `this` when needed**: Can cause shadowing issues
- **Public fields**: Should use private fields with getters/setters
- **Forgetting to initialize**: Fields have default values but should be explicit
- **Not using constructors**: Should initialize objects properly
- **Access modifier confusion**: Understand public, private, protected, package-private

# Practice Exercises

1. Create a class with private fields and public getters/setters.
2. Create a class with multiple constructors using constructor chaining.
3. Create a class with both instance and static members.
4. Implement proper encapsulation for a Student class.
5. Create a utility class with only static methods.

Example solution for exercise 1:

```java
public class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        if (age >= 0) {
            this.age = age;
        }
    }
}
```

# Key Takeaways

- Constructors initialize objects
- Use `this` to refer to current object
- Access modifiers control visibility: public, private, protected
- Encapsulation hides implementation details
- Use private fields with public getters/setters
- Multiple constructors enable flexible object creation
- Static members belong to the class, not instances
- Proper encapsulation improves maintainability and security

# Related Topics

- Basic Classes (Java Beginner #10)
- Inheritance (next lesson)
- Polymorphism (Java Intermediate #4)
