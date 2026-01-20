---
title: "Arrays"
language: java
difficulty: beginner
prerequisites: ["Variables and Data Types", "Loops"]
keywords: [arrays, indexing, length, iteration, collections, fixed size]
---

# Learning Objectives

- Create and work with arrays
- Access array elements using indexing
- Understand array length and bounds
- Loop through arrays
- Work with multi-dimensional arrays (basics)

# Prerequisites

- Variables and Data Types
- Loops

# Introduction

An array is a collection of elements of the same type stored in contiguous memory. Arrays have a fixed size that's determined when they're created. Arrays are one of the most fundamental data structures in Java and are used to store multiple values efficiently.

# Core Concepts

## Creating Arrays

You can create arrays in several ways:

```java
// Method 1: Declare and initialize
int[] numbers = {1, 2, 3, 4, 5};

// Method 2: Declare size, then assign
int[] numbers = new int[5];  // Creates array of 5 zeros
numbers[0] = 1;
numbers[1] = 2;
// ...

// Method 3: Declare and initialize separately
int[] numbers;
numbers = new int[]{1, 2, 3, 4, 5};
```

## Accessing Array Elements

You access elements using their index (starting at 0):

```java
int[] numbers = {10, 20, 30, 40, 50};

System.out.println(numbers[0]);  // Output: 10 (first element)
System.out.println(numbers[1]);  // Output: 20 (second element)
System.out.println(numbers[4]);  // Output: 50 (last element)
```

## Array Length

Use the `length` property to get the array size:

```java
int[] numbers = {1, 2, 3, 4, 5};
System.out.println(numbers.length);  // Output: 5

// Loop through array using length
for (int i = 0; i < numbers.length; i++) {
    System.out.println(numbers[i]);
}
```

## Enhanced for Loop (for-each)

The enhanced `for` loop is convenient for iterating through arrays:

```java
int[] numbers = {1, 2, 3, 4, 5};

for (int num : numbers) {
    System.out.println(num);
}
// Output: 1, 2, 3, 4, 5
```

## Modifying Arrays

You can change array elements:

```java
int[] numbers = {1, 2, 3, 4, 5};
numbers[2] = 99;  // Change third element
System.out.println(numbers[2]);  // Output: 99
```

## Array Bounds

Accessing an invalid index causes an `ArrayIndexOutOfBoundsException`:

```java
int[] numbers = {1, 2, 3};

// System.out.println(numbers[5]);  // Error! Index out of bounds
// Valid indices are 0, 1, 2 (for array of length 3)
```

## Arrays of Different Types

```java
// Array of strings
String[] names = {"Alice", "Bob", "Charlie"};

// Array of doubles
double[] prices = {19.99, 29.99, 39.99};

// Array of booleans
boolean[] flags = {true, false, true};
```

## Multi-dimensional Arrays

Arrays can have multiple dimensions:

```java
// 2D array (matrix)
int[][] matrix = {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
};

// Access elements
System.out.println(matrix[0][0]);  // Output: 1
System.out.println(matrix[1][2]);  // Output: 6

// Loop through 2D array
for (int i = 0; i < matrix.length; i++) {
    for (int j = 0; j < matrix[i].length; j++) {
        System.out.print(matrix[i][j] + " ");
    }
    System.out.println();
}
```

## Common Array Operations

```java
int[] numbers = {5, 2, 8, 1, 9};

// Find maximum (manual approach)
int max = numbers[0];
for (int num : numbers) {
    if (num > max) {
        max = num;
    }
}

// Calculate sum
int sum = 0;
for (int num : numbers) {
    sum += num;
}

// Count elements
int count = numbers.length;
```

# Common Mistakes

- **Index out of bounds**: Accessing `array[10]` when array only has 5 elements
- **Forgetting that indexing starts at 0**: First element is `array[0]`, not `array[1]`
- **Using `length()` instead of `length`**: Arrays use `length` property, not method
- **Trying to change array size**: Arrays have fixed size once created
- **Confusing array declaration syntax**: `int[] arr` vs `int arr[]` (both work, first is preferred)

# Practice Exercises

1. Create an array of 5 numbers and print each one.
2. Write a method that takes an array of numbers and returns the sum.
3. Write a method that finds the maximum value in an array.
4. Create a 2D array representing a 3x3 grid and print it.
5. Write a method that counts how many times a number appears in an array.

Example solution for exercise 2:

```java
public static int sumArray(int[] numbers) {
    int sum = 0;
    for (int num : numbers) {
        sum += num;
    }
    return sum;
}

int[] nums = {1, 2, 3, 4, 5};
int result = sumArray(nums);
System.out.println(result);  // Output: 15
```

# Key Takeaways

- Arrays store multiple values of the same type
- Arrays have fixed size determined at creation
- Access elements using index (starts at 0)
- Use `length` property to get array size
- Enhanced `for` loop is convenient for iteration
- Arrays can be multi-dimensional (2D, 3D, etc.)
- Invalid index access causes `ArrayIndexOutOfBoundsException`
- Arrays are objects in Java (reference types)

# Related Topics

- Variables and Data Types (Java Beginner #2)
- Loops (Java Beginner #6)
- Methods (Java Beginner #7)
- Collections (Java Intermediate #7)
