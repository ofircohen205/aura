---
title: "Loops"
language: java
difficulty: beginner
prerequisites: ["Conditionals", "Arrays"]
keywords: [loops, for, while, do-while, iteration, break, continue, repetition]
---

# Learning Objectives

- Use `for` loops to repeat code a specific number of times
- Use `while` loops to repeat code while a condition is true
- Use `do-while` loops
- Understand when to use different loop types
- Control loops with `break` and `continue`

# Prerequisites

- Conditionals
- Arrays (basic understanding helpful)

# Introduction

Loops allow you to repeat code multiple times without writing it over and over. Java provides three types of loops: `for`, `while`, and `do-while`. Understanding loops is essential for processing collections of data and repeating operations.

# Core Concepts

## The for Loop

Use `for` loops when you know how many times to repeat:

```java
// Count from 0 to 4
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}
// Output: 0, 1, 2, 3, 4
```

The `for` loop has three parts:

- Initialization: `int i = 0` (runs once at start)
- Condition: `i < 5` (checked before each iteration)
- Update: `i++` (runs after each iteration)

## Enhanced for Loop (for-each)

Use the enhanced `for` loop to iterate through arrays and collections:

```java
int[] numbers = {1, 2, 3, 4, 5};

for (int num : numbers) {
    System.out.println(num);
}
// Output: 1, 2, 3, 4, 5
```

## The while Loop

Use `while` loops when you want to repeat until a condition is false:

```java
int count = 0;

while (count < 5) {
    System.out.println(count);
    count++;  // Important: update the counter!
}
// Output: 0, 1, 2, 3, 4
```

## The do-while Loop

Similar to `while`, but executes at least once:

```java
int count = 0;

do {
    System.out.println(count);
    count++;
} while (count < 5);
// Output: 0, 1, 2, 3, 4
```

## Controlling Loops

### break - Exit the Loop

```java
for (int i = 0; i < 10; i++) {
    if (i == 5) {
        break;  // Exit the loop when i is 5
    }
    System.out.println(i);
}
// Output: 0, 1, 2, 3, 4
```

### continue - Skip to Next Iteration

```java
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) {
        continue;  // Skip even numbers
    }
    System.out.println(i);
}
// Output: 1, 3, 5, 7, 9
```

## Nested Loops

You can put loops inside other loops:

```java
// Print a multiplication table
for (int i = 1; i <= 3; i++) {
    for (int j = 1; j <= 3; j++) {
        System.out.print(i + " x " + j + " = " + (i * j) + "  ");
    }
    System.out.println();  // New line
}
```

# Common Mistakes

- **Infinite while loops**: Forgetting to update the condition variable
- **Off-by-one errors**: `i < 5` gives 0-4, not 1-5
- **Using `=` instead of `==` in conditions**: `while (count = 5)` is wrong
- **Modifying loop variable inside enhanced for**: Can cause unexpected behavior
- **Forgetting `break` in switch inside loop**: Can cause fall-through issues

# Practice Exercises

1. Write a loop that prints all even numbers from 0 to 20.
2. Write a program that calculates the sum of numbers from 1 to 100.
3. Write a loop that prints a countdown from 10 to 1, then "Blast off!".
4. Write a program that finds the factorial of a number (5! = 5 × 4 × 3 × 2 × 1 = 120).
5. Use an enhanced for loop to print all elements of an array.

Example solution for exercise 2:

```java
int sum = 0;

for (int i = 1; i <= 100; i++) {
    sum += i;
}

System.out.println("The sum is: " + sum);  // Output: The sum is: 5050
```

# Key Takeaways

- Use `for` loops when you know how many times to repeat
- Use `while` loops when repeating until a condition is met
- Use `do-while` when you need to execute at least once
- Enhanced `for` loop is convenient for arrays and collections
- Always update the condition in `while` loops to avoid infinite loops
- Use `break` to exit a loop early
- Use `continue` to skip to the next iteration
- Loops can be nested (loop inside a loop)

# Related Topics

- Conditionals (Java Beginner #5)
- Methods (next lesson)
- Arrays (Java Beginner #8)
