---
title: "Loops"
language: typescript
difficulty: beginner
prerequisites: ["Arrays", "Conditionals"]
keywords: [loops, for, while, iteration, forEach, map, filter, break, continue]
---

# Learning Objectives

- Use `for` loops to repeat code
- Use `while` loops for conditional repetition
- Loop through arrays using different methods
- Use `break` and `continue` to control loops
- Understand when to use different loop types

# Prerequisites

- Arrays
- Conditionals

# Introduction

Loops allow you to repeat code multiple times without writing it over and over. TypeScript provides several types of loops: `for` loops, `while` loops, and array methods like `forEach()`, `map()`, and `filter()`. Choosing the right loop type makes your code more readable and efficient.

# Core Concepts

## The for Loop

Use `for` loops when you know how many times to repeat:

```typescript
// Count from 0 to 4
for (let i = 0; i < 5; i++) {
  console.log(i);
}
// Output: 0, 1, 2, 3, 4
```

The `for` loop has three parts:

- Initialization: `let i = 0` (runs once at start)
- Condition: `i < 5` (checked before each iteration)
- Increment: `i++` (runs after each iteration)

## The for...of Loop

Use `for...of` to loop through arrays (recommended):

```typescript
const fruits = ["apple", "banana", "orange"];

for (const fruit of fruits) {
  console.log(fruit);
}
// Output: apple, banana, orange
```

## The for...in Loop

Use `for...in` to loop through object properties:

```typescript
const person = { name: "Alice", age: 25, city: "NYC" };

for (const key in person) {
  console.log(`${key}: ${person[key as keyof typeof person]}`);
}
// Output: name: Alice, age: 25, city: NYC
```

## The while Loop

Use `while` loops when you want to repeat until a condition is false:

```typescript
let count = 0;

while (count < 5) {
  console.log(count);
  count++; // Important: update the counter!
}
// Output: 0, 1, 2, 3, 4
```

## The do...while Loop

Similar to `while`, but executes at least once:

```typescript
let count = 0;

do {
  console.log(count);
  count++;
} while (count < 5);
```

## Array Methods for Looping

### forEach()

Executes a function for each array element:

```typescript
const numbers = [1, 2, 3, 4, 5];

numbers.forEach((num, index) => {
  console.log(`Index ${index}: ${num}`);
});
```

### map()

Creates a new array by transforming each element:

```typescript
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(num => num * 2);
console.log(doubled); // Output: [2, 4, 6, 8, 10]
```

### filter()

Creates a new array with elements that pass a test:

```typescript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const evens = numbers.filter(num => num % 2 === 0);
console.log(evens); // Output: [2, 4, 6, 8, 10]
```

## Controlling Loops

### break - Exit the Loop

```typescript
for (let i = 0; i < 10; i++) {
  if (i === 5) {
    break; // Exit the loop when i is 5
  }
  console.log(i);
}
// Output: 0, 1, 2, 3, 4
```

### continue - Skip to Next Iteration

```typescript
for (let i = 0; i < 10; i++) {
  if (i % 2 === 0) {
    continue; // Skip even numbers
  }
  console.log(i);
}
// Output: 1, 3, 5, 7, 9
```

## Nested Loops

You can put loops inside other loops:

```typescript
// Print a multiplication table
for (let i = 1; i <= 3; i++) {
  for (let j = 1; j <= 3; j++) {
    console.log(`${i} x ${j} = ${i * j}`);
  }
  console.log(); // Empty line
}
```

# Common Mistakes

- **Infinite while loops**: Forgetting to update the condition variable
- **Off-by-one errors**: `i < 5` gives 0-4, not 1-5
- **Modifying array while iterating**: Can cause unexpected behavior
- **Using `for...in` on arrays**: Use `for...of` instead for arrays
- **Confusing `map()` and `forEach()`**: `map()` returns new array, `forEach()` doesn't

# Practice Exercises

1. Write a loop that prints all even numbers from 0 to 20.
2. Write a function that calculates the sum of numbers in an array.
3. Write a loop that prints a countdown from 10 to 1, then "Blast off!".
4. Use `map()` to create an array of squares from an array of numbers.
5. Use `filter()` to get all numbers greater than 5 from an array.

Example solution for exercise 2:

```typescript
function sumArray(numbers: number[]): number {
  let sum = 0;
  for (const num of numbers) {
    sum += num;
  }
  return sum;
}

const result = sumArray([1, 2, 3, 4, 5]);
console.log(result); // Output: 15
```

# Key Takeaways

- Use `for` loops when you know how many times to repeat
- Use `for...of` to loop through arrays (recommended)
- Use `while` loops when repeating until a condition is met
- Array methods: `forEach()`, `map()`, `filter()` provide functional approaches
- Use `break` to exit a loop early
- Use `continue` to skip to the next iteration
- Always update the condition in `while` loops to avoid infinite loops

# Related Topics

- Arrays (TypeScript Beginner #3)
- Conditionals (TypeScript Beginner #5)
- Functions (TypeScript Beginner #2)
