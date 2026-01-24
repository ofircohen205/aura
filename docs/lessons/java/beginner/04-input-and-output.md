---
title: "Input and Output"
language: java
difficulty: beginner
prerequisites: ["Variables and Data Types", "Basic Operations"]
keywords: [input, output, Scanner, System.out, reading input, displaying output, console]
---

# Learning Objectives

- Use `System.out.println()` to display output
- Use `Scanner` to read user input
- Understand how to read different types of input
- Format output properly
- Handle input errors

# Prerequisites

- Variables and Data Types
- Basic Operations

# Introduction

So far, we've worked with values defined in code. Real programs need to interact with users - they display information and get input. In Java, we use `System.out` for output and `Scanner` for input. Understanding I/O is essential for building interactive programs.

# Core Concepts

## Displaying Output

### System.out.println()

The most common way to display output:

```java
System.out.println("Hello, World!");
System.out.println(42);
System.out.println(3.14);

// Output:
// Hello, World!
// 42
// 3.14
```

### System.out.print()

Prints without moving to a new line:

```java
System.out.print("Hello, ");
System.out.print("World!");
System.out.println();  // Move to next line

// Output: Hello, World!
```

### Formatting Output

You can combine strings and variables:

```java
String name = "Alice";
int age = 25;

System.out.println("My name is " + name + " and I am " + age + " years old");
// Output: My name is Alice and I am 25 years old
```

## Reading Input with Scanner

### Setting Up Scanner

First, import `Scanner` and create an instance:

```java
import java.util.Scanner;

public class InputExample {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Use scanner here

        scanner.close();  // Close when done
    }
}
```

### Reading Different Types

```java
Scanner scanner = new Scanner(System.in);

// Read a string
System.out.print("Enter your name: ");
String name = scanner.nextLine();
System.out.println("Hello, " + name);

// Read an integer
System.out.print("Enter your age: ");
int age = scanner.nextInt();
System.out.println("You are " + age + " years old");

// Read a double
System.out.print("Enter your height: ");
double height = scanner.nextDouble();
System.out.println("Your height is " + height);

scanner.close();
```

### Common Scanner Methods

- `nextLine()` - reads a line of text (String)
- `nextInt()` - reads an integer
- `nextDouble()` - reads a double
- `nextFloat()` - reads a float
- `nextBoolean()` - reads a boolean
- `next()` - reads a single word (String)

## Complete Example

Here's a complete program that gets and displays user information:

```java
import java.util.Scanner;

public class UserInfo {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("What is your name? ");
        String name = scanner.nextLine();

        System.out.print("How old are you? ");
        int age = scanner.nextInt();

        System.out.print("What is your height in meters? ");
        double height = scanner.nextDouble();

        System.out.println("\nHello, " + name + "!");
        System.out.println("You are " + age + " years old");
        System.out.println("Your height is " + height + " meters");
        System.out.println("Next year you'll be " + (age + 1) + " years old");

        scanner.close();
    }
}
```

## Handling Input Issues

### The nextLine() Problem

There's a common issue when mixing `nextInt()`/`nextDouble()` with `nextLine()`:

```java
Scanner scanner = new Scanner(System.in);

System.out.print("Enter a number: ");
int num = scanner.nextInt();  // Reads number but leaves newline

System.out.print("Enter your name: ");
String name = scanner.nextLine();  // Reads the leftover newline!

// Solution: consume the newline
scanner.nextLine();  // Consume the leftover newline
String name = scanner.nextLine();  // Now this works
```

### Better Solution

Read everything as strings, then convert:

```java
Scanner scanner = new Scanner(System.in);

System.out.print("Enter a number: ");
int num = Integer.parseInt(scanner.nextLine());

System.out.print("Enter your name: ");
String name = scanner.nextLine();  // Works correctly now
```

# Common Mistakes

- **Forgetting to import Scanner**: Must have `import java.util.Scanner;`
- **Not closing Scanner**: Always call `scanner.close()` when done
- **Mixing nextInt() and nextLine()**: Causes the newline problem
- **Not handling input errors**: User might enter wrong type
- **Forgetting quotes in println()**: `System.out.println(Hello)` is wrong, use `System.out.println("Hello")`

# Practice Exercises

1. Write a program that asks for the user's name and greets them.
2. Write a program that asks for two numbers and displays their sum.
3. Write a program that asks for the user's age and tells them how old they'll be in 10 years.
4. Write a program that asks for the radius of a circle and calculates and displays its area.
5. Write a program that asks for a person's first and last name, then displays their full name.

Example solution for exercise 2:

```java
import java.util.Scanner;

public class AddNumbers {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter the first number: ");
        double num1 = scanner.nextDouble();

        System.out.print("Enter the second number: ");
        double num2 = scanner.nextDouble();

        double sum = num1 + num2;
        System.out.println("The sum is: " + sum);

        scanner.close();
    }
}
```

# Key Takeaways

- Use `System.out.println()` to display output
- Use `System.out.print()` to print without a newline
- Import `Scanner` from `java.util` to read input
- Use appropriate Scanner methods: `nextLine()`, `nextInt()`, `nextDouble()`
- Always close the Scanner when done
- Be careful when mixing `nextInt()`/`nextDouble()` with `nextLine()`
- Read as strings and convert when possible to avoid issues

# Related Topics

- Variables and Data Types (Java Beginner #2)
- Basic Operations (Java Beginner #3)
- Conditionals (next lesson)
