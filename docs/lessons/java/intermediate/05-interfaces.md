---
title: "Interfaces"
language: java
difficulty: intermediate
prerequisites: ["Inheritance", "Polymorphism"]
keywords: [interfaces, implements, contract, multiple inheritance, default methods, static methods]
---

# Learning Objectives

- Understand what interfaces are and why they're used
- Create and implement interfaces
- Understand interface as contracts
- Use default methods in interfaces
- Implement multiple interfaces
- Understand interface vs abstract class

# Prerequisites

- Inheritance
- Polymorphism

# Introduction

Interfaces define contracts that classes must follow. They specify what methods a class must implement without providing implementation details. Interfaces enable polymorphism and allow Java to support a form of multiple inheritance. Understanding interfaces is essential for writing flexible, maintainable Java code.

# Core Concepts

## Basic Interface

```java
interface Drawable {
    void draw();  // Abstract method (no body)
}

class Circle implements Drawable {
    public void draw() {
        System.out.println("Drawing circle");
    }
}

class Rectangle implements Drawable {
    public void draw() {
        System.out.println("Drawing rectangle");
    }
}
```

## Multiple Interface Implementation

A class can implement multiple interfaces:

```java
interface Flyable {
    void fly();
}

interface Swimmable {
    void swim();
}

class Duck implements Flyable, Swimmable {
    public void fly() {
        System.out.println("Duck is flying");
    }

    public void swim() {
        System.out.println("Duck is swimming");
    }
}
```

## Interface Variables

Interfaces can have constants (implicitly `public static final`):

```java
interface Constants {
    double PI = 3.14159;  // public static final by default
    int MAX_SIZE = 100;
}

// Access via interface name
double area = Constants.PI * radius * radius;
```

## Default Methods (Java 8+)

Provide default implementation:

```java
interface Vehicle {
    void start();

    // Default method
    default void stop() {
        System.out.println("Vehicle stopped");
    }
}

class Car implements Vehicle {
    public void start() {
        System.out.println("Car started");
    }
    // stop() uses default implementation
}
```

## Static Methods in Interfaces (Java 8+)

```java
interface MathUtils {
    static double add(double a, double b) {
        return a + b;
    }
}

// Call via interface name
double result = MathUtils.add(5.0, 3.0);
```

## Interface Inheritance

Interfaces can extend other interfaces:

```java
interface Animal {
    void eat();
}

interface Mammal extends Animal {
    void breathe();
}

class Dog implements Mammal {
    public void eat() {
        System.out.println("Dog is eating");
    }

    public void breathe() {
        System.out.println("Dog is breathing");
    }
}
```

## Interface as Type

Use interfaces as reference types:

```java
interface Shape {
    double area();
}

class Circle implements Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    public double area() {
        return Math.PI * radius * radius;
    }
}

// Use interface as type
Shape shape = new Circle(5.0);
double area = shape.area();
```

# Common Mistakes

- **Forgetting to implement all methods**: Must implement all abstract methods
- **Wrong access modifier**: Interface methods are public by default
- **Confusing interface and class**: Interfaces define contracts, classes implement them
- **Not using interfaces for polymorphism**: Interfaces enable flexible design

# Practice Exercises

1. Create an interface for a payment system and implement it in multiple classes.
2. Create a class that implements multiple interfaces.
3. Create an interface with default methods.
4. Use an interface as a reference type in a method parameter.
5. Create an interface hierarchy (interface extending another interface).

Example solution for exercise 1:

```java
interface Payment {
    void processPayment(double amount);
    boolean isSuccessful();
}

class CreditCardPayment implements Payment {
    private boolean success = false;

    public void processPayment(double amount) {
        System.out.println("Processing credit card payment: $" + amount);
        success = true;
    }

    public boolean isSuccessful() {
        return success;
    }
}

class PayPalPayment implements Payment {
    private boolean success = false;

    public void processPayment(double amount) {
        System.out.println("Processing PayPal payment: $" + amount);
        success = true;
    }

    public boolean isSuccessful() {
        return success;
    }
}
```

# Key Takeaways

- Interfaces define contracts (what, not how)
- Classes implement interfaces using `implements`
- A class can implement multiple interfaces
- Interface methods are public and abstract by default
- Default methods provide implementation (Java 8+)
- Static methods can be in interfaces (Java 8+)
- Interfaces can extend other interfaces
- Use interfaces for polymorphism and flexible design

# Related Topics

- Inheritance (Java Intermediate #3)
- Polymorphism (Java Intermediate #4)
- Abstract Classes (Java Intermediate #6)
