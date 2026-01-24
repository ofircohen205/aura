---
title: "Array Methods"
language: typescript
difficulty: intermediate
prerequisites: ["Arrays", "Functions"]
keywords: [array methods, map, filter, reduce, forEach, find, some, every, functional programming]
---

# Learning Objectives

- Master array transformation methods (map, filter, reduce)
- Use array iteration methods (forEach, for...of)
- Work with array search methods (find, findIndex, includes)
- Use array testing methods (some, every)
- Chain array methods together
- Understand when to use each method

# Prerequisites

- Arrays
- Functions

# Introduction

TypeScript arrays come with powerful methods for transforming, filtering, and processing data. Understanding these methods enables you to write more functional, expressive code. These methods are essential for data manipulation in modern TypeScript applications.

# Core Concepts

## map() - Transform Elements

Creates a new array by transforming each element:

```typescript
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log(doubled); // Output: [2, 4, 6, 8, 10]

// With type annotations
const numbers: number[] = [1, 2, 3];
const strings: string[] = numbers.map(n => n.toString());
```

## filter() - Keep Matching Elements

Creates a new array with elements that pass a test:

```typescript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const evens = numbers.filter(n => n % 2 === 0);
console.log(evens); // Output: [2, 4, 6, 8, 10]

// Filter objects
interface Person {
  name: string;
  age: number;
}

const people: Person[] = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 17 },
  { name: "Charlie", age: 30 },
];

const adults = people.filter(p => p.age >= 18);
console.log(adults); // Output: [{ name: "Alice", age: 25 }, { name: "Charlie", age: 30 }]
```

## reduce() - Combine to Single Value

Reduces array to a single value:

```typescript
const numbers = [1, 2, 3, 4, 5];

// Sum
const sum = numbers.reduce((acc, num) => acc + num, 0);
console.log(sum); // Output: 15

// Find maximum
const max = numbers.reduce((acc, num) => (num > acc ? num : acc), numbers[0]);
console.log(max); // Output: 5

// Build object
const words = ["apple", "banana", "apple", "orange"];
const counts = words.reduce(
  (acc, word) => {
    acc[word] = (acc[word] || 0) + 1;
    return acc;
  },
  {} as Record<string, number>
);
console.log(counts); // Output: { apple: 2, banana: 1, orange: 1 }
```

## forEach() - Execute for Each Element

Executes a function for each element (doesn't return new array):

```typescript
const numbers = [1, 2, 3];

numbers.forEach((num, index) => {
  console.log(`Index ${index}: ${num}`);
});
// Output:
// Index 0: 1
// Index 1: 2
// Index 2: 3
```

## find() and findIndex()

Find first matching element:

```typescript
interface Person {
  name: string;
  age: number;
}

const people: Person[] = [
  { name: "Alice", age: 25 },
  { name: "Bob", age: 30 },
  { name: "Charlie", age: 25 },
];

// Find first person aged 25
const person = people.find(p => p.age === 25);
console.log(person); // Output: { name: "Alice", age: 25 }

// Find index
const index = people.findIndex(p => p.age === 30);
console.log(index); // Output: 1
```

## some() and every()

Test if elements meet condition:

```typescript
const numbers = [1, 2, 3, 4, 5];

// Check if any number is even
const hasEven = numbers.some(n => n % 2 === 0);
console.log(hasEven); // Output: true

// Check if all numbers are positive
const allPositive = numbers.every(n => n > 0);
console.log(allPositive); // Output: true
```

## Chaining Methods

Chain multiple methods together:

```typescript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const result = numbers
  .filter(n => n % 2 === 0) // [2, 4, 6, 8, 10]
  .map(n => n ** 2) // [4, 16, 36, 64, 100]
  .reduce((acc, n) => acc + n, 0); // 220

console.log(result); // Output: 220
```

## Other Useful Methods

```typescript
const numbers = [1, 2, 3, 4, 5];

// includes() - check if array contains value
console.log(numbers.includes(3)); // true

// indexOf() - find index of value
console.log(numbers.indexOf(3)); // 2

// slice() - get subset
console.log(numbers.slice(1, 4)); // [2, 3, 4]

// concat() - combine arrays
const more = numbers.concat([6, 7, 8]);
console.log(more); // [1, 2, 3, 4, 5, 6, 7, 8]

// flat() - flatten nested arrays
const nested = [[1, 2], [3, 4], [5]];
console.log(nested.flat()); // [1, 2, 3, 4, 5]
```

# Common Mistakes

- **Using `forEach` when you need a new array**: Use `map` instead
- **Mutating array in `forEach`**: Prefer `map` for transformations
- **Not providing initial value to `reduce`**: Can cause errors with empty arrays
- **Confusing `some` and `every`**: `some` = at least one, `every` = all
- **Not chaining when you could**: Chaining is more readable

# Practice Exercises

1. Use `map()` to convert an array of temperatures from Celsius to Fahrenheit.
2. Use `filter()` to get all users over 18 from an array of user objects.
3. Use `reduce()` to calculate the average of numbers in an array.
4. Chain methods to find the sum of squares of even numbers.
5. Use `find()` to locate a specific object in an array by a property value.

Example solution for exercise 3:

```typescript
function average(numbers: number[]): number {
  if (numbers.length === 0) return 0;
  const sum = numbers.reduce((acc, n) => acc + n, 0);
  return sum / numbers.length;
}

const result = average([10, 20, 30, 40]);
console.log(result); // Output: 25
```

# Key Takeaways

- `map()` transforms each element into a new array
- `filter()` keeps elements that pass a test
- `reduce()` combines elements into a single value
- `forEach()` executes a function for each element (no return)
- `find()` returns first matching element, `findIndex()` returns index
- `some()` checks if any element passes test, `every()` checks if all pass
- Methods can be chained for complex transformations
- These methods don't mutate the original array

# Related Topics

- Arrays (TypeScript Beginner #3)
- Functions (TypeScript Beginner #2)
- Functional Programming (covered in this lesson)
