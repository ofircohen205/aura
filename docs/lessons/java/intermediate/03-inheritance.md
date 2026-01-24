---
title: "Inheritance"
language: java
difficulty: intermediate
prerequisites: ["Classes", "Constructors"]
keywords: [inheritance, extends, super, method overriding, is-a relationship, code reuse]
---

# Learning Objectives

- Understand inheritance and its benefits
- Create subclasses using `extends`
- Override methods in subclasses
- Use `super` to access parent class members
- Understand the inheritance hierarchy
- Recognize when to use inheritance

# Prerequisites

- Classes
- Constructors

# Introduction

Inheritance allows you to create new classes based on existing classes. A child class (subclass) inherits attributes and methods from a parent class (superclass), enabling code reuse and creating an "is-a" relationship. Understanding inheritance is fundamental to object-oriented programming in Java.

# Core Concepts

## Basic Inheritance

A subclass extends a superclass:

```java
// Parent class (superclass)
class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    public void eat() {
        System.out.println(name + " is eating");
    }
}

// Child class (subclass)
class Dog extends Animal {
    private String breed;

    public Dog(String name, String breed) {
        super(name);  // Call parent constructor
        this.breed = breed;
    }

    public void bark() {
        System.out.println(name + " is barking");
    }
}

// Usage
Dog dog = new Dog("Buddy", "Labrador");
dog.eat();   // Inherited method
dog.bark();  // Own method
```

## Method Overriding

Subclasses can override parent methods:

```java
class Animal {
    public void makeSound() {
        System.out.println("Some animal sound");
    }
}

class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}

class Cat extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Meow!");
    }
}
```

## The `super` Keyword

Access parent class members:

```java
class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    public void display() {
        System.out.println("Animal: " + name);
    }
}

class Dog extends Animal {
    private String breed;

    public Dog(String name, String breed) {
        super(name);  // Call parent constructor
        this.breed = breed;
    }

    @Override
    public void display() {
        super.display();  // Call parent method
        System.out.println("Breed: " + breed);
    }
}
```

## Access Modifiers and Inheritance

```java
class Parent {
    public String publicField;      // Accessible everywhere
    protected String protectedField; // Accessible in subclasses
    private String privateField;     // Not accessible in subclasses
}

class Child extends Parent {
    public void accessFields() {
        publicField = "OK";      // OK
        protectedField = "OK";   // OK
        // privateField = "OK";  // Error! Not accessible
    }
}
```

## The `final` Keyword

Prevent inheritance or overriding:

```java
// Class cannot be extended
final class UtilityClass {
    // ...
}

class Parent {
    // Method cannot be overridden
    public final void importantMethod() {
        // ...
    }
}
```

## Inheritance Hierarchy

Classes can form hierarchies:

```java
class Animal { }
class Mammal extends Animal { }
class Dog extends Mammal { }
class Cat extends Mammal { }
```

# Common Mistakes

- **Forgetting `super()`**: Must call parent constructor
- **Wrong access modifiers**: `private` members not accessible in subclasses
- **Not using `@Override`**: Annotation helps catch errors
- **Overusing inheritance**: Not everything needs inheritance
- **Deep hierarchies**: Too many levels make code hard to understand

# Practice Exercises

1. Create a class hierarchy: Vehicle -> Car, Motorcycle.
2. Override a method in a subclass and use `super` to call parent method.
3. Create a three-level inheritance hierarchy.
4. Use `final` to prevent a method from being overridden.
5. Create subclasses that properly call parent constructors.

Example solution for exercise 1:

```java
class Vehicle {
    protected String make;
    protected String model;

    public Vehicle(String make, String model) {
        this.make = make;
        this.model = model;
    }

    public void start() {
        System.out.println("Vehicle started");
    }
}

class Car extends Vehicle {
    private int doors;

    public Car(String make, String model, int doors) {
        super(make, model);
        this.doors = doors;
    }

    @Override
    public void start() {
        System.out.println("Car started");
    }
}
```

# Key Takeaways

- Inheritance enables code reuse through "is-a" relationship
- Use `extends` keyword to create subclasses
- Subclasses inherit all non-private members
- Override methods to provide specialized behavior
- Use `super` to access parent class members
- Use `super()` to call parent constructor
- `final` prevents inheritance or method overriding
- Inheritance represents specialization

# Related Topics

- Classes (Java Intermediate #1)
- Constructors (Java Intermediate #2)
- Polymorphism (next lesson)
