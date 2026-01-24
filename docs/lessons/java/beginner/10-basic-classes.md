---
title: "Basic Classes"
language: java
difficulty: beginner
prerequisites: ["Methods", "Variables and Data Types"]
keywords: [classes, objects, instances, fields, methods, encapsulation, OOP basics]
---

# Learning Objectives

- Understand what classes and objects are
- Create simple classes with fields and methods
- Create objects (instances) from classes
- Access object fields and methods
- Understand the relationship between classes and objects

# Prerequisites

- Methods
- Variables and Data Types

# Introduction

Java is an object-oriented programming language. Everything in Java is organized into classes. A class is like a blueprint that defines what an object will have (fields/variables) and what it can do (methods). Understanding classes is fundamental to Java programming.

# Core Concepts

## What is a Class?

A class is a template or blueprint for creating objects. It defines:

- **Fields** (variables) - data the object stores
- **Methods** (functions) - actions the object can perform

## Creating a Simple Class

```java
public class Person {
    // Fields (instance variables)
    String name;
    int age;

    // Method
    public void introduce() {
        System.out.println("Hi, I'm " + name + " and I'm " + age + " years old");
    }
}
```

## Creating Objects

You create objects (instances) from a class using the `new` keyword:

```java
// Create an object
Person person1 = new Person();

// Set field values
person1.name = "Alice";
person1.age = 25;

// Call methods
person1.introduce();  // Output: Hi, I'm Alice and I'm 25 years old
```

## Multiple Objects

You can create multiple objects from the same class:

```java
Person person1 = new Person();
person1.name = "Alice";
person1.age = 25;

Person person2 = new Person();
person2.name = "Bob";
person2.age = 30;

person1.introduce();  // Output: Hi, I'm Alice and I'm 25 years old
person2.introduce();  // Output: Hi, I'm Bob and I'm 30 years old
```

## Methods in Classes

Methods can use the object's fields:

```java
public class Rectangle {
    double length;
    double width;

    // Method that uses fields
    public double calculateArea() {
        return length * width;
    }

    public void displayInfo() {
        System.out.println("Length: " + length + ", Width: " + width);
        System.out.println("Area: " + calculateArea());
    }
}

// Usage
Rectangle rect = new Rectangle();
rect.length = 5.0;
rect.width = 3.0;
rect.displayInfo();
```

## The main Method

Every Java program needs a `main` method as the entry point:

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

## Complete Example

```java
public class Student {
    // Fields
    String name;
    int age;
    String major;

    // Method to set information
    public void setInfo(String n, int a, String m) {
        name = n;
        age = a;
        major = m;
    }

    // Method to display information
    public void displayInfo() {
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
        System.out.println("Major: " + major);
    }

    // Main method to test the class
    public static void main(String[] args) {
        Student student1 = new Student();
        student1.setInfo("Alice", 20, "Computer Science");
        student1.displayInfo();
    }
}
```

# Common Mistakes

- **Forgetting `new` keyword**: `Person p = Person();` is wrong, use `new Person()`
- **Accessing fields/methods before creating object**: Must create object first
- **Confusing class and object**: Class is blueprint, object is instance
- **Not initializing fields**: Fields have default values (0, null, false) but should be set explicitly
- **Missing `public static void main`**: Every program needs a main method

# Practice Exercises

1. Create a `Book` class with title, author, and year fields, and a method to display the book info.
2. Create a `Circle` class with a radius field and methods to calculate area and circumference.
3. Create a `Car` class with make, model, and year fields, and a method to display car details.
4. Create multiple objects from the same class and demonstrate they're independent.
5. Add a method to the `Person` class that calculates and returns the person's age in days.

Example solution for exercise 1:

```java
public class Book {
    String title;
    String author;
    int year;

    public void displayInfo() {
        System.out.println("Title: " + title);
        System.out.println("Author: " + author);
        System.out.println("Year: " + year);
    }

    public static void main(String[] args) {
        Book book = new Book();
        book.title = "The Great Gatsby";
        book.author = "F. Scott Fitzgerald";
        book.year = 1925;
        book.displayInfo();
    }
}
```

# Key Takeaways

- A class is a blueprint for creating objects
- Objects are instances created from a class using `new`
- Classes contain fields (data) and methods (behavior)
- Each object has its own copy of the fields
- Methods can access and use the object's fields
- Every Java program needs a `main` method
- Classes enable code organization and reusability

# Related Topics

- Methods (Java Beginner #7)
- Classes (Java Intermediate #1 - more advanced)
- Constructors (Java Intermediate #2)
- Inheritance (Java Intermediate #3)
