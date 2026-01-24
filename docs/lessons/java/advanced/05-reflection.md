---
title: "Reflection"
language: java
difficulty: advanced
prerequisites: ["Classes", "Interfaces"]
keywords: [reflection, Class, Method, Field, introspection, dynamic code, metadata]
---

# Learning Objectives

- Understand what reflection is
- Get class information at runtime
- Access and invoke methods dynamically
- Access and modify fields
- Understand when to use reflection
- Recognize reflection limitations

# Prerequisites

- Classes
- Interfaces

# Introduction

Reflection allows you to inspect and manipulate classes, methods, and fields at runtime. It enables dynamic code execution and is used by frameworks and libraries. However, reflection should be used sparingly as it has performance costs and reduces type safety.

# Core Concepts

## Getting Class Information

```java
// Get Class object
Class<?> clazz = String.class;
// Or
Class<?> clazz2 = "hello".getClass();
// Or
Class<?> clazz3 = Class.forName("java.lang.String");

// Get class name
String className = clazz.getName();
System.out.println(className);  // Output: java.lang.String
```

## Getting Methods

```java
Class<?> clazz = Person.class;

// Get all public methods
Method[] methods = clazz.getMethods();

// Get specific method
try {
    Method method = clazz.getMethod("getName");
    System.out.println("Method: " + method.getName());
} catch (NoSuchMethodException e) {
    e.printStackTrace();
}
```

## Invoking Methods

```java
class Person {
    private String name;

    public Person(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}

Person person = new Person("Alice");

// Get and invoke method
try {
    Method getNameMethod = Person.class.getMethod("getName");
    String name = (String) getNameMethod.invoke(person);
    System.out.println(name);  // Output: Alice
} catch (Exception e) {
    e.printStackTrace();
}
```

## Accessing Fields

```java
class Person {
    private String name;
    public int age;
}

Person person = new Person();
person.age = 25;

// Get public field
try {
    Field ageField = Person.class.getField("age");
    int age = ageField.getInt(person);
    System.out.println(age);  // Output: 25
} catch (Exception e) {
    e.printStackTrace();
}

// Access private field
try {
    Field nameField = Person.class.getDeclaredField("name");
    nameField.setAccessible(true);  // Bypass access control
    nameField.set(person, "Bob");
    String name = (String) nameField.get(person);
    System.out.println(name);  // Output: Bob
} catch (Exception e) {
    e.printStackTrace();
}
```

## Creating Instances

```java
try {
    Class<?> clazz = Class.forName("java.util.ArrayList");
    Object instance = clazz.getDeclaredConstructor().newInstance();
    List<?> list = (List<?>) instance;
    System.out.println(list.getClass().getName());  // Output: java.util.ArrayList
} catch (Exception e) {
    e.printStackTrace();
}
```

# Common Mistakes

- **Performance concerns**: Reflection is slower than direct calls
- **Security issues**: Can bypass access controls
- **Type safety**: Loses compile-time type checking
- **Overusing reflection**: Use only when necessary
- **Not handling exceptions**: Reflection methods throw checked exceptions

# Practice Exercises

1. Use reflection to get all methods of a class.
2. Use reflection to invoke a method on an object.
3. Use reflection to access and modify a private field.
4. Use reflection to create an instance of a class.
5. Create a utility method that uses reflection to copy properties between objects.

Example solution for exercise 2:

```java
class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}

Calculator calc = new Calculator();
try {
    Method addMethod = Calculator.class.getMethod("add", int.class, int.class);
    int result = (Integer) addMethod.invoke(calc, 5, 3);
    System.out.println("Result: " + result);  // Output: Result: 8
} catch (Exception e) {
    e.printStackTrace();
}
```

# Key Takeaways

- Reflection allows runtime inspection and manipulation
- Get Class object using `.class`, `getClass()`, or `Class.forName()`
- Can get methods, fields, and constructors
- Can invoke methods and access fields dynamically
- Can create instances dynamically
- Reflection has performance costs
- Use sparingly - frameworks use it, application code usually shouldn't
- Bypasses access controls (can access private members)

# Related Topics

- Classes (Java Intermediate #1)
- Interfaces (Java Intermediate #5)
- Annotations (Java Advanced #6)
