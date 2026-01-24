---
title: "Conditionals"
language: java
difficulty: beginner
prerequisites: ["Variables and Data Types", "Input and Output"]
keywords: [conditionals, if, else, switch, boolean, comparison, decision making]
---

# Learning Objectives

- Use `if` statements to make decisions
- Understand comparison operators
- Use `else` and `else if` for multiple conditions
- Use `switch` statements
- Write programs that respond differently based on conditions

# Prerequisites

- Variables and Data Types
- Input and Output

# Introduction

Programs need to make decisions - they need to do different things based on different conditions. In Java, we use `if`, `else`, and `switch` statements to control the flow of our program. Understanding conditionals is essential for writing useful programs.

# Core Concepts

## The if Statement

The `if` statement checks a condition and executes code only if the condition is `true`:

```java
int age = 18;

if (age >= 18) {
    System.out.println("You are an adult");
}
```

## Comparison Operators

Java provides operators to compare values:

- `==` - equal to
- `!=` - not equal to
- `<` - less than
- `>` - greater than
- `<=` - less than or equal to
- `>=` - greater than or equal to

```java
int age = 20;

if (age >= 18) {
    System.out.println("You can vote");
}

if (age < 18) {
    System.out.println("You cannot vote yet");
}

if (age == 18) {
    System.out.println("You just became an adult!");
}
```

## The else Clause

Use `else` to execute code when the condition is `false`:

```java
int age = 15;

if (age >= 18) {
    System.out.println("You are an adult");
} else {
    System.out.println("You are a minor");
}
```

## The else if Clause

Use `else if` to check multiple conditions:

```java
int score = 85;

if (score >= 90) {
    System.out.println("Grade: A");
} else if (score >= 80) {
    System.out.println("Grade: B");
} else if (score >= 70) {
    System.out.println("Grade: C");
} else if (score >= 60) {
    System.out.println("Grade: D");
} else {
    System.out.println("Grade: F");
}
```

## Logical Operators

Combine conditions using `&&` (and), `||` (or), and `!` (not):

```java
int age = 25;
boolean hasLicense = true;

// Using && (both must be true)
if (age >= 18 && hasLicense) {
    System.out.println("You can drive");
}

// Using || (at least one must be true)
if (age < 18 || age > 65) {
    System.out.println("You get a discount");
}

// Using ! (not - reverses the condition)
if (!hasLicense) {
    System.out.println("You need a license to drive");
}
```

## The switch Statement

Use `switch` for multiple conditions based on a single value:

```java
int day = 1;
String dayName;

switch (day) {
    case 1:
        dayName = "Monday";
        break;
    case 2:
        dayName = "Tuesday";
        break;
    case 3:
        dayName = "Wednesday";
        break;
    default:
        dayName = "Unknown";
}

System.out.println(dayName);
```

### Switch with Strings (Java 7+)

You can use strings in switch statements:

```java
String day = "Monday";

switch (day) {
    case "Monday":
        System.out.println("Start of the work week");
        break;
    case "Friday":
        System.out.println("End of the work week");
        break;
    case "Saturday":
    case "Sunday":
        System.out.println("Weekend!");
        break;
    default:
        System.out.println("Midweek day");
}
```

## Nested Conditionals

You can put `if` statements inside other `if` statements:

```java
int age = 20;
boolean hasLicense = true;

if (age >= 18) {
    if (hasLicense) {
        System.out.println("You can drive");
    } else {
        System.out.println("You need a license");
    }
} else {
    System.out.println("You are too young to drive");
}
```

# Common Mistakes

- **Using `=` instead of `==`**: `if (age = 18)` is assignment, use `if (age == 18)`
- **Missing curly braces**: While optional for single statements, always use them for clarity
- **Forgetting `break` in switch**: Without `break`, execution falls through to next case
- **Confusing `&&` with `||`**: `&&` means both true, `||` means at least one true
- **Comparing strings with `==`**: Use `.equals()` for string comparison

# Practice Exercises

1. Write a program that checks if a number is positive, negative, or zero.
2. Write a program that determines if a person can vote (must be 18 or older).
3. Write a program that assigns a letter grade based on a score.
4. Write a switch statement that returns the day name for a number (1-7).
5. Write a program that checks if a year is a leap year.

Example solution for exercise 1:

```java
int number = 5;

if (number > 0) {
    System.out.println("Positive");
} else if (number < 0) {
    System.out.println("Negative");
} else {
    System.out.println("Zero");
}
```

# Key Takeaways

- Use `if` to check conditions and execute code conditionally
- Use `else` for the alternative case
- Use `else if` to check multiple conditions in order
- Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Combine conditions with `&&`, `||`, and `!`
- Use `switch` for multiple conditions based on a single value
- Always use `==` for comparison, not `=` (which is assignment)
- Use `.equals()` to compare strings, not `==`

# Related Topics

- Variables and Data Types (Java Beginner #2)
- Loops (next lesson)
- Methods (Java Beginner #7)
