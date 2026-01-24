---
title: "Object-Oriented Programming Basics"
language: python
difficulty: intermediate
prerequisites: ["Functions", "Modules and Packages"]
keywords: [classes, objects, instances, methods, attributes, encapsulation, self]
---

# Learning Objectives

- Understand classes and objects
- Create classes with attributes and methods
- Understand the `self` parameter
- Create and use objects (instances)
- Understand encapsulation basics
- Work with instance and class attributes

# Prerequisites

- Functions
- Modules and Packages

# Introduction

Object-Oriented Programming (OOP) is a programming paradigm that organizes code around objects and classes. Python supports OOP, allowing you to create reusable, organized code. Understanding OOP is essential for building larger applications.

# Core Concepts

## What are Classes and Objects?

- **Class**: A blueprint or template for creating objects
- **Object (Instance)**: A specific instance created from a class

```python
# Define a class
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says Woof!"

# Create objects (instances)
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(dog1.bark())  # Output: Buddy says Woof!
print(dog2.bark())  # Output: Max says Woof!
```

## The `__init__` Method

The constructor method that runs when an object is created:

```python
class Person:
    def __init__(self, name, age):
        self.name = name  # Instance attribute
        self.age = age    # Instance attribute
        print(f"{name} created!")

person = Person("Alice", 25)  # Output: Alice created!
```

## The `self` Parameter

`self` refers to the instance of the class:

```python
class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        # self.length and self.width refer to this instance's attributes
        return self.length * self.width

    def perimeter(self):
        return 2 * (self.length + self.width)

rect = Rectangle(5, 3)
print(rect.area())  # Output: 15
```

## Instance Attributes

Attributes that belong to each instance:

```python
class Student:
    def __init__(self, name, student_id):
        self.name = name
        self.student_id = student_id
        self.grades = []  # Each student has their own grades list

    def add_grade(self, grade):
        self.grades.append(grade)

    def average(self):
        if self.grades:
            return sum(self.grades) / len(self.grades)
        return 0

student1 = Student("Alice", "S001")
student2 = Student("Bob", "S002")

student1.add_grade(85)
student1.add_grade(90)
student2.add_grade(75)

print(student1.average())  # Output: 87.5
print(student2.average())  # Output: 75.0
```

## Class Attributes

Attributes shared by all instances:

```python
class Dog:
    species = "Canis familiaris"  # Class attribute (shared)

    def __init__(self, name, age):
        self.name = name  # Instance attribute
        self.age = age    # Instance attribute

dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(dog1.species)  # Output: Canis familiaris
print(dog2.species)  # Output: Canis familiaris
print(Dog.species)   # Output: Canis familiaris (can access via class)
```

## Methods

Functions defined inside a class:

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            return self.balance
        else:
            return "Insufficient funds"

    def get_balance(self):
        return self.balance

account = BankAccount("Alice", 100)
account.deposit(50)
print(account.get_balance())  # Output: 150
account.withdraw(30)
print(account.get_balance())  # Output: 120
```

## Encapsulation

Controlling access to attributes (basic level):

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self._age = age  # Convention: _ means "internal use"

    def get_age(self):
        return self._age

    def set_age(self, age):
        if age > 0:
            self._age = age
        else:
            print("Age must be positive")

person = Person("Alice", 25)
print(person.get_age())  # Output: 25
person.set_age(30)
print(person.get_age())  # Output: 30
```

# Common Mistakes

- **Forgetting `self`**: Methods must have `self` as first parameter
- **Not calling `__init__`**: Use class name to create instances: `Person()`
- **Confusing class and instance attributes**: Class attributes are shared, instance attributes are unique
- **Modifying mutable class attributes**: Can affect all instances unexpectedly
- **Not understanding `self`**: `self` refers to the specific instance

# Practice Exercises

1. Create a `Book` class with title, author, and year attributes, and a method to display book info.
2. Create a `Circle` class with a radius attribute and methods to calculate area and circumference.
3. Create a `Car` class with make, model, year, and speed. Add methods to accelerate and brake.
4. Create a `Student` class that tracks grades and calculates average.
5. Create a class with both instance and class attributes, and demonstrate the difference.

Example solution for exercise 1:

```python
class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def display_info(self):
        print(f"{self.title} by {self.author} ({self.year})")

book = Book("The Great Gatsby", "F. Scott Fitzgerald", 1925)
book.display_info()
```

# Key Takeaways

- Classes are blueprints for creating objects
- Objects are instances created from classes
- `__init__` is the constructor that initializes objects
- `self` refers to the instance (must be first parameter in methods)
- Instance attributes belong to each object
- Class attributes are shared by all instances
- Methods are functions defined inside classes
- Encapsulation controls access to data

# Related Topics

- Functions (Python Beginner #6)
- Inheritance (Python Intermediate #7)
- Polymorphism (covered in advanced topics)
