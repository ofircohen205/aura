---
title: "Polymorphism"
language: java
difficulty: intermediate
prerequisites: ["Inheritance", "Classes"]
keywords:
  [polymorphism, method overriding, dynamic binding, runtime polymorphism, upcasting, downcasting]
---

# Learning Objectives

- Understand what polymorphism is
- Use method overriding for polymorphism
- Understand runtime vs compile-time polymorphism
- Work with upcasting and downcasting
- Use polymorphism with interfaces
- Recognize polymorphic behavior

# Prerequisites

- Inheritance
- Classes

# Introduction

Polymorphism means "many forms" - the ability of objects of different types to be treated as objects of a common type. In Java, polymorphism allows you to write code that works with the parent class but behaves differently based on the actual object type. Understanding polymorphism is essential for flexible, extensible code.

# Core Concepts

## Runtime Polymorphism

Method calls are resolved at runtime based on actual object type:

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

// Polymorphic behavior
Animal animal1 = new Dog();
Animal animal2 = new Cat();

animal1.makeSound();  // Output: Woof! (calls Dog's method)
animal2.makeSound();  // Output: Meow! (calls Cat's method)
```

## Upcasting

Treating subclass as superclass:

```java
Dog dog = new Dog("Buddy", "Labrador");
Animal animal = dog;  // Upcasting (automatic)

animal.makeSound();  // Calls Dog's makeSound() at runtime
// animal.bark();    // Error! Animal doesn't have bark()
```

## Downcasting

Treating superclass as subclass (requires cast):

```java
Animal animal = new Dog("Buddy", "Labrador");
Dog dog = (Dog) animal;  // Downcasting (explicit cast)

dog.bark();  // OK - Dog has bark() method
```

## instanceof Operator

Check object type before downcasting:

```java
Animal animal = new Dog("Buddy", "Labrador");

if (animal instanceof Dog) {
    Dog dog = (Dog) animal;
    dog.bark();
}
```

## Polymorphism with Interfaces

```java
interface Drawable {
    void draw();
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

// Polymorphic behavior
Drawable[] shapes = {new Circle(), new Rectangle()};
for (Drawable shape : shapes) {
    shape.draw();  // Calls appropriate draw() method
}
```

## Method Overriding Rules

- Method signature must match
- Return type must be compatible
- Access modifier can't be more restrictive
- Use `@Override` annotation

# Common Mistakes

- **Not using `@Override`**: Helps catch errors
- **Wrong method signature**: Override requires exact match
- **Downcasting without checking**: Use `instanceof` first
- **Confusing overriding and overloading**: Overriding replaces, overloading adds
- **Access modifier too restrictive**: Can't make override more private

# Practice Exercises

1. Create a polymorphic method that works with different animal types.
2. Use upcasting and downcasting with proper type checking.
3. Create an interface and implement it in multiple classes, then use polymorphism.
4. Create a method that accepts a parent type but calls child-specific methods.
5. Use polymorphism in a collection (array or list) of different object types.

Example solution for exercise 1:

```java
class Animal {
    public void makeSound() {
        System.out.println("Animal sound");
    }
}

class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("Woof!");
    }
}

// Polymorphic method
public static void makeAnimalSound(Animal animal) {
    animal.makeSound();  // Calls appropriate method at runtime
}

makeAnimalSound(new Dog());  // Output: Woof!
```

# Key Takeaways

- Polymorphism allows objects of different types to be treated uniformly
- Runtime polymorphism uses method overriding
- Upcasting is automatic, downcasting requires explicit cast
- Use `instanceof` before downcasting
- Polymorphism works with both inheritance and interfaces
- Method calls are resolved at runtime based on actual object type
- Polymorphism enables flexible, extensible code

# Related Topics

- Inheritance (Java Intermediate #3)
- Interfaces (next lesson)
- Classes (Java Intermediate #1)
