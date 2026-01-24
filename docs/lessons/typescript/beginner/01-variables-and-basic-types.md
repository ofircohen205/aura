---
title: "Variables and Basic Types"
language: typescript
difficulty: beginner
prerequisites: []
keywords: [variables, types, let, const, number, string, boolean, type annotations, declarations]
---

# Learning Objectives

- Understand how to declare variables in TypeScript
- Learn about TypeScript's basic types: number, string, and boolean
- Practice using `let` and `const` for variable declarations
- Learn how to add type annotations to variables

# Prerequisites

- None (this is the first lesson!)

# Introduction

Variables are containers that store data in your program. TypeScript adds type safety to JavaScript, which means you can specify what type of data a variable should hold. This helps catch errors before your code runs and makes your code easier to understand.

# Core Concepts

## Declaring Variables

In TypeScript, you declare variables using `let` or `const`:

### Using `let`

Use `let` when you need to change the value later.

```typescript
let age = 25;
age = 26; // This is allowed

let name = "Alice";
name = "Bob"; // This is allowed
```

### Using `const`

Use `const` when the value won't change (constant).

```typescript
const pi = 3.14159;
// pi = 3.14;  // Error! Cannot reassign a const

const greeting = "Hello";
// greeting = "Hi";  // Error! Cannot reassign a const
```

## Basic Types

TypeScript has several basic types. Here are the most common ones:

### number

Represents both integers and floating-point numbers.

```typescript
let age: number = 25;
let price: number = 19.99;
let temperature: number = -5;
```

### string

Represents text. Can use single quotes, double quotes, or backticks.

```typescript
let name: string = "Alice";
let greeting: string = "Hello";
let message: string = `Welcome, ${name}!`; // Template literal
```

### boolean

Represents true or false values.

```typescript
let isStudent: boolean = true;
let isGraduated: boolean = false;
```

## Type Annotations

You can explicitly specify the type of a variable using type annotations:

```typescript
// Explicit type annotation
let age: number = 25;
let name: string = "Alice";
let isActive: boolean = true;

// TypeScript can also infer types (type inference)
let age = 25; // TypeScript knows this is a number
let name = "Alice"; // TypeScript knows this is a string
```

## Type Inference

TypeScript is smart enough to figure out the type from the value you assign:

```typescript
let age = 25; // TypeScript infers: number
let name = "Alice"; // TypeScript infers: string
let isStudent = true; // TypeScript infers: boolean
```

## Template Literals

You can create strings with embedded expressions using backticks and `${}`:

```typescript
let name = "Alice";
let age = 25;

// Template literal
let message = `My name is ${name} and I am ${age} years old`;
console.log(message); // Output: My name is Alice and I am 25 years old

// You can also do calculations inside
let result = `Next year I'll be ${age + 1} years old`;
```

# Common Mistakes

- **Using `var` instead of `let` or `const`**: Modern TypeScript/JavaScript uses `let` and `const`
- **Trying to change a `const` variable**: `const` means constant - you can't reassign it
- **Mixing types incorrectly**: TypeScript will catch type errors, like `let age: number = "25"` (string assigned to number)
- **Forgetting quotes for strings**: `let name = Alice` is wrong, use `let name = "Alice"`
- **Using lowercase true/false**: TypeScript uses `true` and `false` (lowercase, unlike Python)

# Practice Exercises

1. Declare a variable called `myName` using `const` and assign it your name as a string.
2. Declare a variable called `myAge` using `let` and assign it your age as a number.
3. Declare a constant called `isStudent` and assign it `true` or `false`.
4. Create a template literal that combines your name and age into a message.
5. Try to reassign a `const` variable and see what error TypeScript gives you.

Example solution:

```typescript
// Exercise 1
const myName: string = "Alice";

// Exercise 2
let myAge: number = 25;

// Exercise 3
const isStudent: boolean = true;

// Exercise 4
let message = `My name is ${myName} and I am ${myAge} years old`;
console.log(message);

// Exercise 5
// const pi = 3.14;
// pi = 3.14159;  // Error: Cannot assign to 'pi' because it is a constant
```

# Key Takeaways

- Use `let` for variables that can change, `const` for constants
- TypeScript has basic types: `number`, `string`, and `boolean`
- You can add type annotations explicitly: `let age: number = 25`
- TypeScript can infer types automatically from the value
- Use template literals (backticks) for strings with embedded expressions
- TypeScript helps catch type errors before your code runs

# Related Topics

- Functions (TypeScript Beginner #2)
- Arrays (TypeScript Beginner #3)
- Basic Type System (TypeScript Beginner #7)
