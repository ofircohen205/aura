---
title: "Exception Handling"
language: java
difficulty: intermediate
prerequisites: ["Methods", "Classes"]
keywords: [exceptions, try, catch, finally, throw, throws, checked exceptions, unchecked exceptions]
---

# Learning Objectives

- Handle exceptions with try-catch-finally
- Understand checked vs unchecked exceptions
- Create and throw custom exceptions
- Use `throws` clause
- Handle multiple exception types
- Understand exception hierarchy

# Prerequisites

- Methods
- Classes

# Introduction

Exception handling allows your program to respond gracefully to errors and unexpected situations. Java has a robust exception handling mechanism with checked and unchecked exceptions. Understanding exception handling is essential for writing robust, production-ready Java applications.

# Core Concepts

## Basic Exception Handling

```java
try {
    // Code that might throw an exception
    int result = 10 / 0;
} catch (ArithmeticException e) {
    // Handle the exception
    System.out.println("Division by zero: " + e.getMessage());
}
```

## Multiple Catch Blocks

Handle different exceptions differently:

```java
try {
    // Code that might throw different exceptions
    int[] numbers = {1, 2, 3};
    System.out.println(numbers[10]);
} catch (ArrayIndexOutOfBoundsException e) {
    System.out.println("Array index out of bounds");
} catch (Exception e) {
    System.out.println("General exception: " + e.getMessage());
}
```

## Finally Block

Code that always executes:

```java
try {
    // Some code
} catch (Exception e) {
    // Handle exception
} finally {
    // This always runs, even if exception occurs
    System.out.println("Cleanup code");
}
```

## Checked vs Unchecked Exceptions

### Checked Exceptions

Must be handled or declared:

```java
// Checked exception - must handle or declare
public void readFile() throws IOException {
    FileReader file = new FileReader("data.txt");
    // ...
}
```

### Unchecked Exceptions

Runtime exceptions, don't need to be declared:

```java
// Unchecked exception - no need to declare
public void divide(int a, int b) {
    if (b == 0) {
        throw new ArithmeticException("Division by zero");
    }
    return a / b;
}
```

## Throwing Exceptions

```java
public void validateAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Age cannot be negative");
    }
    if (age > 150) {
        throw new IllegalArgumentException("Age seems unrealistic");
    }
}
```

## Custom Exceptions

Create your own exception classes:

```java
class InvalidEmailException extends Exception {
    public InvalidEmailException(String message) {
        super(message);
    }
}

class AgeException extends RuntimeException {
    public AgeException(String message) {
        super(message);
    }
}

// Usage
public void setEmail(String email) throws InvalidEmailException {
    if (!email.contains("@")) {
        throw new InvalidEmailException("Invalid email format");
    }
    // ...
}
```

## Exception Hierarchy

```java
// All exceptions extend Throwable
// - Error: Serious problems (don't catch)
// - Exception: Problems that can be caught
//   - RuntimeException: Unchecked exceptions
//   - Other: Checked exceptions
```

# Common Mistakes

- **Catching too broad**: Catch specific exceptions when possible
- **Swallowing exceptions**: At least log exceptions, don't ignore them
- **Not using finally**: Use finally for cleanup code
- **Wrong exception type**: Use appropriate exception types
- **Not handling checked exceptions**: Must handle or declare

# Practice Exercises

1. Write code that handles FileNotFoundException when reading a file.
2. Create a custom exception class and use it in a validation method.
3. Write a method that throws a checked exception and handle it in the caller.
4. Use try-catch-finally to ensure a resource is properly closed.
5. Create a method that handles multiple different exception types.

Example solution for exercise 2:

```java
class ValidationException extends Exception {
    public ValidationException(String message) {
        super(message);
    }
}

public void validateUser(String name, int age) throws ValidationException {
    if (name == null || name.isEmpty()) {
        throw new ValidationException("Name cannot be empty");
    }
    if (age < 0) {
        throw new ValidationException("Age cannot be negative");
    }
}

// Usage
try {
    validateUser("", -5);
} catch (ValidationException e) {
    System.out.println("Validation error: " + e.getMessage());
}
```

# Key Takeaways

- Use try-catch to handle exceptions
- Finally block always executes (for cleanup)
- Checked exceptions must be handled or declared with `throws`
- Unchecked exceptions (RuntimeException) don't need declaration
- Create custom exceptions for domain-specific errors
- Catch specific exceptions before general ones
- Don't swallow exceptions - handle or log them
- Use finally for resource cleanup

# Related Topics

- Methods (Java Beginner #7)
- Classes (Java Intermediate #1)
- File I/O (covered in advanced topics)
