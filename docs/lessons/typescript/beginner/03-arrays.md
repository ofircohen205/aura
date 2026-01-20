---
title: "Arrays"
language: typescript
difficulty: beginner
prerequisites: ["Variables and Basic Types", "Functions"]
keywords: [arrays, lists, indexing, methods, push, pop, map, filter, iteration]
---

# Learning Objectives

- Create and work with arrays in TypeScript
- Access array elements using indexing
- Use array methods like `push()`, `pop()`, `map()`, and `filter()`
- Understand array type annotations
- Loop through arrays

# Prerequisites

- Variables and Basic Types
- Functions

# Introduction

Arrays are ordered collections of items. In TypeScript, arrays can hold multiple values of the same type (or a union of types). Arrays are one of the most commonly used data structures, and TypeScript provides type safety to ensure you're working with the correct types.

# Core Concepts

## Creating Arrays

You can create arrays in several ways:

```typescript
// Array of numbers
const numbers: number[] = [1, 2, 3, 4, 5];

// Array of strings
const fruits: string[] = ["apple", "banana", "orange"];

// Using Array generic syntax
const numbers: Array<number> = [1, 2, 3, 4, 5];

// Empty array
const empty: number[] = [];

// TypeScript can infer types
const numbers = [1, 2, 3]; // TypeScript knows this is number[]
```

## Accessing Array Elements

You access elements using their index (starting at 0):

```typescript
const fruits = ["apple", "banana", "orange"];

console.log(fruits[0]); // Output: apple
console.log(fruits[1]); // Output: banana
console.log(fruits[2]); // Output: orange
```

## Array Methods

### Adding and Removing Elements

```typescript
const fruits: string[] = ["apple", "banana"];

// Add to the end
fruits.push("orange");
console.log(fruits); // Output: ["apple", "banana", "orange"]

// Remove from the end
const last = fruits.pop();
console.log(last); // Output: orange
console.log(fruits); // Output: ["apple", "banana"]

// Add to the beginning
fruits.unshift("grape");
console.log(fruits); // Output: ["grape", "apple", "banana"]

// Remove from the beginning
const first = fruits.shift();
console.log(first); // Output: grape
```

### Finding Elements

```typescript
const numbers = [1, 2, 3, 4, 5];

// Find index
const index = numbers.indexOf(3);
console.log(index); // Output: 2

// Check if element exists
const hasThree = numbers.includes(3);
console.log(hasThree); // Output: true

// Find element (returns first match)
const found = numbers.find(n => n > 3);
console.log(found); // Output: 4
```

### Transforming Arrays

```typescript
const numbers = [1, 2, 3, 4, 5];

// map() - transform each element
const doubled = numbers.map(n => n * 2);
console.log(doubled); // Output: [2, 4, 6, 8, 10]

// filter() - keep elements that match condition
const evens = numbers.filter(n => n % 2 === 0);
console.log(evens); // Output: [2, 4]

// reduce() - combine elements into single value
const sum = numbers.reduce((acc, n) => acc + n, 0);
console.log(sum); // Output: 15
```

### Other Useful Methods

```typescript
const fruits = ["apple", "banana", "orange"];

// Get length
console.log(fruits.length); // Output: 3

// Join into string
const joined = fruits.join(", ");
console.log(joined); // Output: apple, banana, orange

// Slice (get subset)
const subset = fruits.slice(1, 3);
console.log(subset); // Output: ["banana", "orange"]

// Reverse (modifies original)
fruits.reverse();
console.log(fruits); // Output: ["orange", "banana", "apple"]
```

## Looping Through Arrays

You can loop through arrays in several ways:

```typescript
const fruits = ["apple", "banana", "orange"];

// for loop
for (let i = 0; i < fruits.length; i++) {
  console.log(fruits[i]);
}

// for...of loop (recommended)
for (const fruit of fruits) {
  console.log(fruit);
}

// forEach method
fruits.forEach((fruit, index) => {
  console.log(`${index}: ${fruit}`);
});
```

## Array Type Annotations

TypeScript helps ensure type safety:

```typescript
// Array of numbers
const numbers: number[] = [1, 2, 3];
// numbers.push("hello");  // Error! Can't add string to number array

// Array of mixed types (union type)
const mixed: (string | number)[] = ["hello", 42, "world", 100];

// Array of objects
interface Person {
  name: string;
  age: number;
}

const people: Person[] = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 30 },
];
```

# Common Mistakes

- **Index out of bounds**: Accessing `array[10]` when array only has 5 elements
- **Forgetting that indexing starts at 0**: First element is `array[0]`
- **Mutating arrays unintentionally**: Some methods modify the original array
- **Type mismatches**: TypeScript will catch type errors
- **Confusing `map()` and `forEach()`**: `map()` returns new array, `forEach()` doesn't return anything

# Practice Exercises

1. Create an array of numbers and write a function that returns the sum of all numbers.
2. Write a function that takes an array of strings and returns a new array with all strings in uppercase.
3. Write a function that filters out all even numbers from an array.
4. Write a function that finds the maximum value in an array of numbers.
5. Create an array of objects (people with name and age) and find all people over 18.

Example solution for exercise 1:

```typescript
function sumArray(numbers: number[]): number {
  return numbers.reduce((acc, n) => acc + n, 0);
}

const result = sumArray([1, 2, 3, 4, 5]);
console.log(result); // Output: 15
```

# Key Takeaways

- Arrays are typed collections: `number[]`, `string[]`, etc.
- Access elements using index: `array[0]`
- Common methods: `push()`, `pop()`, `map()`, `filter()`, `reduce()`
- Use `for...of` or `forEach()` to loop through arrays
- TypeScript ensures type safety for array operations
- `map()` and `filter()` return new arrays, they don't modify the original

# Related Topics

- Variables and Basic Types (TypeScript Beginner #1)
- Functions (TypeScript Beginner #2)
- Objects (next lesson)
- Array Methods (covered in this lesson)
