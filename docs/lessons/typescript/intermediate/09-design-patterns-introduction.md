---
title: "Design Patterns Introduction"
language: typescript
difficulty: intermediate
prerequisites: ["Classes", "Interfaces", "Generics Introduction"]
keywords: [design patterns, singleton, factory, observer, strategy, patterns, best practices]
---

# Learning Objectives

- Understand common design patterns in TypeScript
- Implement Singleton pattern
- Implement Factory pattern
- Implement Observer pattern
- Understand when to use patterns
- Recognize pattern trade-offs

# Prerequisites

- Classes
- Interfaces
- Generics Introduction

# Introduction

Design patterns are reusable solutions to common programming problems. In TypeScript, patterns are enhanced with type safety. Understanding design patterns helps you write more maintainable, flexible code. However, use patterns when they solve real problems, not just because they exist.

# Core Concepts

## Singleton Pattern

Ensure only one instance exists:

```typescript
class Singleton {
  private static instance: Singleton;

  private constructor() {} // Private constructor

  static getInstance(): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton();
    }
    return Singleton.instance;
  }
}

const instance1 = Singleton.getInstance();
const instance2 = Singleton.getInstance();
console.log(instance1 === instance2); // Output: true
```

## Factory Pattern

Create objects without specifying exact class:

```typescript
interface Animal {
  speak(): void;
}

class Dog implements Animal {
  speak() {
    console.log("Woof!");
  }
}

class Cat implements Animal {
  speak() {
    console.log("Meow!");
  }
}

class AnimalFactory {
  static create(type: "dog" | "cat"): Animal {
    switch (type) {
      case "dog":
        return new Dog();
      case "cat":
        return new Cat();
    }
  }
}

const dog = AnimalFactory.create("dog");
dog.speak(); // Output: Woof!
```

## Observer Pattern

Notify multiple objects of changes:

```typescript
interface Observer {
  update(data: string): void;
}

class Subject {
  private observers: Observer[] = [];

  attach(observer: Observer): void {
    this.observers.push(observer);
  }

  notify(data: string): void {
    this.observers.forEach(observer => observer.update(data));
  }
}

class ConcreteObserver implements Observer {
  constructor(private name: string) {}

  update(data: string): void {
    console.log(`${this.name} received: ${data}`);
  }
}

const subject = new Subject();
const observer1 = new ConcreteObserver("Observer 1");
const observer2 = new ConcreteObserver("Observer 2");

subject.attach(observer1);
subject.attach(observer2);
subject.notify("Event occurred");
```

## Strategy Pattern

Make algorithms interchangeable:

```typescript
interface PaymentStrategy {
  pay(amount: number): void;
}

class CreditCardPayment implements PaymentStrategy {
  pay(amount: number): void {
    console.log(`Paid $${amount} with credit card`);
  }
}

class PayPalPayment implements PaymentStrategy {
  pay(amount: number): void {
    console.log(`Paid $${amount} with PayPal`);
  }
}

class PaymentProcessor {
  constructor(private strategy: PaymentStrategy) {}

  processPayment(amount: number): void {
    this.strategy.pay(amount);
  }

  setStrategy(strategy: PaymentStrategy): void {
    this.strategy = strategy;
  }
}

const processor = new PaymentProcessor(new CreditCardPayment());
processor.processPayment(100);
processor.setStrategy(new PayPalPayment());
processor.processPayment(50);
```

# Common Mistakes

- **Overusing patterns**: Don't force patterns where they're not needed
- **Making code too complex**: Simple code is often better
- **Not understanding trade-offs**: Patterns have costs
- **Following patterns blindly**: Adapt to your needs
- **Premature pattern application**: Use when you have the problem

# Practice Exercises

1. Implement a Singleton for a configuration manager.
2. Create a Factory that creates different types of vehicles.
3. Implement an Observer pattern for an event system.
4. Create a Strategy pattern for sorting algorithms.
5. Combine patterns (e.g., Factory with Strategy).

Example solution for exercise 1:

```typescript
class ConfigManager {
  private static instance: ConfigManager;
  private config: Record<string, any> = {};

  private constructor() {}

  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  set(key: string, value: any): void {
    this.config[key] = value;
  }

  get(key: string): any {
    return this.config[key];
  }
}

const config = ConfigManager.getInstance();
config.set("theme", "dark");
```

# Key Takeaways

- Design patterns are reusable solutions to common problems
- Singleton ensures only one instance exists
- Factory creates objects without specifying exact class
- Observer notifies multiple objects of changes
- Strategy makes algorithms interchangeable
- Use patterns when they solve real problems
- TypeScript adds type safety to patterns
- Don't overuse patterns - simplicity is often better

# Related Topics

- Classes (TypeScript Intermediate #2)
- Interfaces (TypeScript Intermediate #1)
- Generics Introduction (TypeScript Intermediate #7)
