---
title: "Introduction to Java"
language: java
difficulty: beginner
prerequisites: []
keywords: [java, introduction, programming, syntax, main method, class, public, static, void]
---

# Learning Objectives

- Understand what Java is and why it's used
- Learn the basic structure of a Java program
- Write your first "Hello, World!" program
- Understand the main method and its purpose

# Prerequisites

- None (this is the first lesson!)

# Introduction

Java is a popular programming language used to build applications that run on computers, phones, and servers. Java programs are compiled into bytecode that runs on the Java Virtual Machine (JVM), which means Java programs can run on any device that has Java installed.

# Core Concepts

## Your First Java Program

Every Java program needs at least one class and a `main` method. Here's the classic "Hello, World!" program:

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

Let's break this down:

### The Class

```java
public class HelloWorld {
    // Your code goes here
}
```

- `public` means the class can be accessed from anywhere
- `class` is a keyword that defines a class
- `HelloWorld` is the name of the class (must match the filename: `HelloWorld.java`)
- The curly braces `{}` contain the class body

### The Main Method

```java
public static void main(String[] args) {
    // Your program code goes here
}
```

- `public` - can be accessed from anywhere
- `static` - belongs to the class, not an instance
- `void` - doesn't return a value
- `main` - the method name (required for program execution)
- `String[] args` - command-line arguments (we'll learn about this later)

### Printing Output

```java
System.out.println("Hello, World!");
```

- `System.out` - the standard output stream
- `println` - prints a line and moves to the next line
- The text in quotes is what gets printed

## Running a Java Program

1. Save your code in a file named `HelloWorld.java` (must match the class name)
2. Compile it: `javac HelloWorld.java` (creates `HelloWorld.class`)
3. Run it: `java HelloWorld` (runs the compiled program)

## More Examples

### Printing Multiple Lines

```java
public class Greeting {
    public static void main(String[] args) {
        System.out.println("Hello!");
        System.out.println("Welcome to Java programming!");
        System.out.println("Let's learn together!");
    }
}
```

Output:

```
Hello!
Welcome to Java programming!
Let's learn together!
```

### Using print() vs println()

```java
public class PrintExample {
    public static void main(String[] args) {
        System.out.print("Hello, ");
        System.out.print("World!");
        System.out.println();  // Move to next line

        System.out.println("This is on a new line");
    }
}
```

Output:

```
Hello, World!
This is on a new line
```

# Common Mistakes

- **Class name doesn't match filename**: If your class is `HelloWorld`, the file must be `HelloWorld.java`
- **Missing main method**: Every program needs a `main` method to run
- **Wrong method signature**: `main` must be exactly `public static void main(String[] args)`
- **Missing semicolons**: Java statements end with `;`
- **Mismatched curly braces**: Make sure every `{` has a matching `}`

# Practice Exercises

1. Write a program that prints your name.
2. Write a program that prints three lines: your name, your favorite programming language, and your goal.
3. Write a program that uses `print()` to print "Hello, " and then `println()` to print "World!" on the same line.
4. Create a class called `MyFirstProgram` and have it print a welcome message.

Example solution for exercise 1:

```java
public class MyName {
    public static void main(String[] args) {
        System.out.println("Alice");
    }
}
```

# Key Takeaways

- Every Java program needs a class and a `main` method
- The class name must match the filename (case-sensitive)
- Use `System.out.println()` to print output
- Java is case-sensitive: `Main` is different from `main`
- All statements end with a semicolon `;`
- Code is organized in classes and methods

# Related Topics

- Variables and Data Types (next lesson)
- Basic Operations (Java Beginner #3)
- Methods (Java Beginner #7)
