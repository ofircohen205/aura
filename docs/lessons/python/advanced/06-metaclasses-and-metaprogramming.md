---
title: "Metaclasses and Metaprogramming"
language: python
difficulty: advanced
prerequisites: ["Object-Oriented Programming Basics", "Decorators"]
keywords:
  [metaclasses, metaprogramming, __new__, __init_subclass__, class creation, dynamic classes]
---

# Learning Objectives

- Understand what metaclasses are
- Create custom metaclasses
- Understand the class creation process
- Use `__init_subclass__` for simpler metaprogramming
- Understand when to use metaclasses
- Apply metaprogramming patterns

# Prerequisites

- Object-Oriented Programming Basics
- Decorators

# Introduction

Metaclasses are classes whose instances are classes themselves. They control how classes are created, allowing you to modify class creation behavior. While advanced, understanding metaclasses unlocks powerful metaprogramming capabilities. However, they should be used sparingly - simpler alternatives often exist.

# Core Concepts

## What are Metaclasses?

In Python, everything is an object, including classes. Classes are instances of metaclasses (by default, `type`):

```python
class MyClass:
    pass

print(type(MyClass))  # Output: <class 'type'>
print(type(type))     # Output: <class 'type'>
```

## Creating Classes with type()

The `type()` function can create classes dynamically:

```python
# Traditional class definition
class Person:
    name = "Alice"

# Equivalent using type()
Person = type('Person', (), {'name': 'Alice'})

person = Person()
print(person.name)  # Output: Alice
```

## Custom Metaclass

Create a metaclass by inheriting from `type`:

```python
class MyMeta(type):
    def __new__(cls, name, bases, attrs):
        # Modify class creation
        attrs['created_by'] = 'MyMeta'
        return super().__new__(cls, name, bases, attrs)

class MyClass(metaclass=MyMeta):
    pass

print(MyClass.created_by)  # Output: MyMeta
```

## **init_subclass** (Simpler Alternative)

Python 3.6+ provides a simpler way:

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registry = []
        print(f"{cls.__name__} was subclassed")

class Child(Base):
    pass
# Output: Child was subclassed

print(Child.registry)  # Output: []
```

## Practical Example: Singleton Pattern

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    pass

obj1 = Singleton()
obj2 = Singleton()
print(obj1 is obj2)  # Output: True (same instance)
```

## Practical Example: Auto-registration

```python
class PluginMeta(type):
    registry = {}

    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if name != 'Plugin':
            cls.registry[name] = new_class
        return new_class

class Plugin(metaclass=PluginMeta):
    pass

class MyPlugin(Plugin):
    pass

class AnotherPlugin(Plugin):
    pass

print(PluginMeta.registry)
# Output: {'MyPlugin': <class '__main__.MyPlugin'>, ...}
```

# Common Mistakes

- **Overusing metaclasses**: Most problems don't need them
- **Making code too complex**: Prefer simpler solutions when possible
- **Not understanding the class creation process**: Know when `__new__` vs `__init__` runs
- **Confusing metaclass and inheritance**: Metaclasses control class creation, not behavior
- **Performance concerns**: Metaclasses add overhead

# Practice Exercises

1. Create a metaclass that adds a `version` attribute to all classes.
2. Create a metaclass that enforces that all methods have docstrings.
3. Use `__init_subclass__` to automatically register subclasses.
4. Create a metaclass that prevents instantiation of abstract classes.
5. Create a simple plugin system using metaclasses.

Example solution for exercise 1:

```python
class VersionMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs['version'] = '1.0.0'
        return super().__new__(cls, name, bases, attrs)

class MyClass(metaclass=VersionMeta):
    pass

print(MyClass.version)  # Output: 1.0.0
```

# Key Takeaways

- Metaclasses are classes that create classes
- Default metaclass is `type`
- Metaclasses control class creation, not instance creation
- `__init_subclass__` is simpler for many use cases
- Use metaclasses sparingly - they add complexity
- Metaclasses enable powerful metaprogramming patterns
- Most problems can be solved without metaclasses

# Related Topics

- Object-Oriented Programming Basics (Python Intermediate #6)
- Decorators (Python Advanced #1)
- Design Patterns (covered in advanced topics)
