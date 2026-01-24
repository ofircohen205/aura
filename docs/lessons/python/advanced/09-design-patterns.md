---
title: "Design Patterns"
language: python
difficulty: advanced
prerequisites: ["Object-Oriented Programming Basics", "Inheritance", "Decorators"]
keywords: [design patterns, singleton, factory, observer, strategy, patterns, best practices]
---

# Learning Objectives

- Understand common design patterns
- Implement Singleton pattern
- Implement Factory pattern
- Implement Observer pattern
- Understand when to use patterns
- Recognize pattern trade-offs

# Prerequisites

- Object-Oriented Programming Basics
- Inheritance
- Decorators

# Introduction

Design patterns are reusable solutions to common programming problems. They provide templates for solving recurring design challenges. Understanding design patterns helps you write more maintainable, flexible code. However, don't force patterns - use them when they solve real problems.

# Core Concepts

## Singleton Pattern

Ensure only one instance exists:

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Usage
obj1 = Singleton()
obj2 = Singleton()
print(obj1 is obj2)  # Output: True
```

## Factory Pattern

Create objects without specifying exact class:

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

def animal_factory(animal_type):
    animals = {
        "dog": Dog,
        "cat": Cat
    }
    return animals.get(animal_type, Animal)()

# Usage
dog = animal_factory("dog")
print(dog.speak())  # Output: Woof!
```

## Observer Pattern

Notify multiple objects of changes:

```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer:
    def update(self, event):
        print(f"Received event: {event}")

# Usage
subject = Subject()
observer1 = Observer()
observer2 = Observer()

subject.attach(observer1)
subject.attach(observer2)
subject.notify("Something happened")
```

## Strategy Pattern

Define family of algorithms, make them interchangeable:

```python
class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} with credit card"

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        return f"Paid ${amount} with PayPal"

class PaymentProcessor:
    def __init__(self, strategy):
        self.strategy = strategy

    def process_payment(self, amount):
        return self.strategy.pay(amount)

# Usage
processor = PaymentProcessor(CreditCardPayment())
result = processor.process_payment(100)
```

## Decorator Pattern

Add behavior to objects dynamically:

```python
class Component:
    def operation(self):
        return "Component"

class Decorator(Component):
    def __init__(self, component):
        self.component = component

    def operation(self):
        return f"Decorator({self.component.operation()})"

# Usage
component = Component()
decorated = Decorator(component)
print(decorated.operation())  # Output: Decorator(Component)
```

# Common Mistakes

- **Overusing patterns**: Don't force patterns where they're not needed
- **Making code too complex**: Simple code is often better than "patterned" code
- **Not understanding trade-offs**: Patterns have costs and benefits
- **Following patterns blindly**: Adapt patterns to your needs
- **Premature pattern application**: Use patterns when you have the problem, not before

# Practice Exercises

1. Implement a Singleton pattern for a configuration manager.
2. Create a Factory that creates different types of vehicles.
3. Implement an Observer pattern for an event system.
4. Create a Strategy pattern for sorting algorithms.
5. Use the Decorator pattern to add logging to functions.

Example solution for exercise 1:

```python
class ConfigManager:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set(self, key, value):
        self._config[key] = value

    def get(self, key):
        return self._config.get(key)

config1 = ConfigManager()
config2 = ConfigManager()
print(config1 is config2)  # True
```

# Key Takeaways

- Design patterns are reusable solutions to common problems
- Singleton ensures only one instance exists
- Factory creates objects without specifying exact class
- Observer notifies multiple objects of changes
- Strategy makes algorithms interchangeable
- Don't overuse patterns - use when they solve real problems
- Patterns have trade-offs - understand them before using

# Related Topics

- Object-Oriented Programming Basics (Python Intermediate #6)
- Inheritance (Python Intermediate #7)
- Decorators (Python Advanced #1)
