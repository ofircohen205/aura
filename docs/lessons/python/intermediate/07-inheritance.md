---
title: "Inheritance"
language: python
difficulty: intermediate
prerequisites: ["Object-Oriented Programming Basics"]
keywords: [inheritance, super, parent class, child class, method overriding, is-a relationship]
---

# Learning Objectives

- Understand what inheritance is and why it's useful
- Create child classes that inherit from parent classes
- Override methods in child classes
- Use `super()` to call parent class methods
- Understand the inheritance hierarchy
- Recognize when to use inheritance

# Prerequisites

- Object-Oriented Programming Basics

# Introduction

Inheritance allows you to create new classes based on existing classes. A child class (subclass) inherits attributes and methods from a parent class (superclass), allowing you to reuse code and create specialized versions of classes. Inheritance is a fundamental OOP concept that promotes code reuse and organization.

# Core Concepts

## Basic Inheritance

A child class inherits from a parent class:

```python
# Parent class (base class)
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def speak(self):
        return "Some generic animal sound"

    def info(self):
        return f"{self.name} is {self.age} years old"

# Child class (derived class)
class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

# Usage
dog = Dog("Buddy", 3)
cat = Cat("Whiskers", 2)

print(dog.info())    # Output: Buddy is 3 years old (inherited)
print(dog.speak())   # Output: Woof! (overridden)
print(cat.speak())   # Output: Meow! (overridden)
```

## Method Overriding

Child classes can override (replace) parent methods:

```python
class Shape:
    def area(self):
        return 0

    def perimeter(self):
        return 0

class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):  # Override parent method
        return self.length * self.width

    def perimeter(self):  # Override parent method
        return 2 * (self.length + self.width)

rect = Rectangle(5, 3)
print(rect.area())  # Output: 15 (uses overridden method)
```

## Using `super()`

Call parent class methods using `super()`:

```python
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # Call parent __init__
        self.breed = breed  # Add new attribute

    def info(self):
        return f"{self.name} is a {self.breed} and is {self.age} years old"

dog = Dog("Buddy", 3, "Golden Retriever")
print(dog.info())  # Output: Buddy is a Golden Retriever and is 3 years old
```

## Multiple Levels of Inheritance

Classes can inherit from classes that inherit from other classes:

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Mammal(Animal):
    def __init__(self, name, warm_blooded=True):
        super().__init__(name)
        self.warm_blooded = warm_blooded

class Dog(Mammal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

dog = Dog("Buddy", "Labrador")
print(dog.name)  # From Animal
print(dog.warm_blooded)  # From Mammal
print(dog.breed)  # From Dog
```

## The `isinstance()` Function

Check if an object is an instance of a class:

```python
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()
print(isinstance(dog, Dog))    # Output: True
print(isinstance(dog, Animal)) # Output: True (Dog is a subclass)
```

## Abstract Base Classes (Concept)

Parent classes that define structure but not implementation:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass  # Must be implemented by child classes

class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):  # Must implement this
        return self.length * self.width

# shape = Shape()  # Error! Can't instantiate abstract class
rect = Rectangle(5, 3)  # OK
```

# Common Mistakes

- **Forgetting to call `super().__init__()`**: Parent initialization might be skipped
- **Circular inheritance**: Class A inherits B, B inherits A (impossible)
- **Overusing inheritance**: Not everything needs inheritance - composition might be better
- **Deep inheritance hierarchies**: Too many levels make code hard to understand
- **Not understanding "is-a" relationship**: Inheritance means "is a kind of"

# Practice Exercises

1. Create a `Vehicle` class and `Car` and `Motorcycle` classes that inherit from it.
2. Create a `Person` class and `Student` and `Teacher` classes that inherit from it.
3. Override a method in a child class and use `super()` to also call the parent method.
4. Create a three-level inheritance hierarchy (e.g., Animal -> Mammal -> Dog).
5. Use `isinstance()` to check object types in an inheritance hierarchy.

Example solution for exercise 1:

```python
class Vehicle:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def start(self):
        return "Vehicle started"

class Car(Vehicle):
    def start(self):
        return f"{self.make} {self.model} car started"

class Motorcycle(Vehicle):
    def start(self):
        return f"{self.make} {self.model} motorcycle started"

car = Car("Toyota", "Camry", 2020)
print(car.start())  # Output: Toyota Camry car started
```

# Key Takeaways

- Inheritance allows child classes to inherit from parent classes
- Child classes can override parent methods
- Use `super()` to call parent class methods
- Inheritance represents an "is-a" relationship
- Use `isinstance()` to check if object is instance of class
- Don't overuse inheritance - prefer composition when appropriate
- Inheritance promotes code reuse and organization

# Related Topics

- Object-Oriented Programming Basics (Python Intermediate #6)
- Polymorphism (covered in advanced topics)
- Multiple Inheritance (Python Advanced #6)
