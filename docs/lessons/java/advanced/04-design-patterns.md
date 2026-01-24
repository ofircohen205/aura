---
title: "Design Patterns"
language: java
difficulty: advanced
prerequisites: ["Inheritance", "Interfaces", "Polymorphism"]
keywords: [design patterns, singleton, factory, observer, strategy, patterns, best practices]
---

# Learning Objectives

- Understand common design patterns in Java
- Implement Singleton pattern
- Implement Factory pattern
- Implement Observer pattern
- Understand when to use patterns
- Recognize pattern trade-offs

# Prerequisites

- Inheritance
- Interfaces
- Polymorphism

# Introduction

Design patterns are reusable solutions to common programming problems. In Java, patterns leverage OOP features like inheritance, interfaces, and polymorphism. Understanding design patterns helps you write more maintainable, flexible code. However, use patterns when they solve real problems.

# Core Concepts

## Singleton Pattern

Ensure only one instance exists:

```java
class Singleton {
    private static Singleton instance;

    private Singleton() {}  // Private constructor

    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}

// Thread-safe version
class ThreadSafeSingleton {
    private static volatile ThreadSafeSingleton instance;

    private ThreadSafeSingleton() {}

    public static ThreadSafeSingleton getInstance() {
        if (instance == null) {
            synchronized (ThreadSafeSingleton.class) {
                if (instance == null) {
                    instance = new ThreadSafeSingleton();
                }
            }
        }
        return instance;
    }
}
```

## Factory Pattern

Create objects without specifying exact class:

```java
interface Animal {
    void makeSound();
}

class Dog implements Animal {
    public void makeSound() {
        System.out.println("Woof!");
    }
}

class Cat implements Animal {
    public void makeSound() {
        System.out.println("Meow!");
    }
}

class AnimalFactory {
    public static Animal create(String type) {
        switch (type.toLowerCase()) {
            case "dog":
                return new Dog();
            case "cat":
                return new Cat();
            default:
                throw new IllegalArgumentException("Unknown animal type");
        }
    }
}

Animal animal = AnimalFactory.create("dog");
animal.makeSound();
```

## Observer Pattern

Notify multiple objects of changes:

```java
import java.util.ArrayList;
import java.util.List;

interface Observer {
    void update(String event);
}

class Subject {
    private List<Observer> observers = new ArrayList<>();

    public void attach(Observer observer) {
        observers.add(observer);
    }

    public void notifyObservers(String event) {
        for (Observer observer : observers) {
            observer.update(event);
        }
    }
}

class ConcreteObserver implements Observer {
    private String name;

    public ConcreteObserver(String name) {
        this.name = name;
    }

    public void update(String event) {
        System.out.println(name + " received: " + event);
    }
}
```

## Strategy Pattern

Make algorithms interchangeable:

```java
interface PaymentStrategy {
    void pay(double amount);
}

class CreditCardPayment implements PaymentStrategy {
    public void pay(double amount) {
        System.out.println("Paid $" + amount + " with credit card");
    }
}

class PayPalPayment implements PaymentStrategy {
    public void pay(double amount) {
        System.out.println("Paid $" + amount + " with PayPal");
    }
}

class PaymentProcessor {
    private PaymentStrategy strategy;

    public PaymentProcessor(PaymentStrategy strategy) {
        this.strategy = strategy;
    }

    public void processPayment(double amount) {
        strategy.pay(amount);
    }

    public void setStrategy(PaymentStrategy strategy) {
        this.strategy = strategy;
    }
}
```

# Common Mistakes

- **Overusing patterns**: Don't force patterns where not needed
- **Making code too complex**: Simple solutions are often better
- **Not understanding trade-offs**: Patterns have costs
- **Following patterns blindly**: Adapt to your needs

# Practice Exercises

1. Implement a Singleton for a configuration manager.
2. Create a Factory that produces different types of vehicles.
3. Implement an Observer pattern for an event system.
4. Create a Strategy pattern for sorting algorithms.
5. Combine patterns (e.g., Factory with Strategy).

Example solution for exercise 1:

```java
class ConfigManager {
    private static ConfigManager instance;
    private Properties config;

    private ConfigManager() {
        config = new Properties();
        // Load configuration
    }

    public static synchronized ConfigManager getInstance() {
        if (instance == null) {
            instance = new ConfigManager();
        }
        return instance;
    }

    public String getProperty(String key) {
        return config.getProperty(key);
    }
}
```

# Key Takeaways

- Design patterns are reusable solutions to common problems
- Singleton ensures only one instance exists
- Factory creates objects without specifying exact class
- Observer notifies multiple objects of changes
- Strategy makes algorithms interchangeable
- Use patterns when they solve real problems
- Don't overuse patterns - simplicity is often better
- Patterns have trade-offs - understand them

# Related Topics

- Inheritance (Java Intermediate #3)
- Interfaces (Java Intermediate #5)
- Polymorphism (Java Intermediate #4)
