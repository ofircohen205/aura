---
title: "Conditionals"
language: typescript
difficulty: beginner
prerequisites: ["Variables and Basic Types", "Functions"]
keywords: [conditionals, if, else, ternary operator, switch, boolean logic, decision making]
---

# Learning Objectives

- Use `if`, `else`, and `else if` statements
- Understand comparison operators
- Use the ternary operator for simple conditionals
- Use `switch` statements for multiple conditions
- Write programs that make decisions based on conditions

# Prerequisites

- Variables and Basic Types
- Functions

# Introduction

Programs need to make decisions - they need to do different things based on different conditions. TypeScript provides several ways to handle conditional logic: `if/else` statements, ternary operators, and `switch` statements. Understanding conditionals is essential for writing useful programs.

# Core Concepts

## The if Statement

The `if` statement executes code only if a condition is true:

```typescript
const age = 18;

if (age >= 18) {
  console.log("You are an adult");
}
```

## Comparison Operators

TypeScript provides operators to compare values:

- `==` - equal to (loose equality, not recommended)
- `===` - strictly equal to (recommended)
- `!=` - not equal to (loose)
- `!==` - strictly not equal to (recommended)
- `<` - less than
- `>` - greater than
- `<=` - less than or equal to
- `>=` - greater than or equal to

```typescript
const age = 20;

if (age >= 18) {
  console.log("You can vote");
}

if (age < 18) {
  console.log("You cannot vote yet");
}

if (age === 18) {
  console.log("You just became an adult!");
}
```

## The else Clause

Use `else` to execute code when the condition is false:

```typescript
const age = 15;

if (age >= 18) {
  console.log("You are an adult");
} else {
  console.log("You are a minor");
}
```

## The else if Clause

Use `else if` to check multiple conditions:

```typescript
const score = 85;

if (score >= 90) {
  console.log("Grade: A");
} else if (score >= 80) {
  console.log("Grade: B");
} else if (score >= 70) {
  console.log("Grade: C");
} else if (score >= 60) {
  console.log("Grade: D");
} else {
  console.log("Grade: F");
}
```

## Logical Operators

Combine conditions using `&&` (and), `||` (or), and `!` (not):

```typescript
const age = 25;
const hasLicense = true;

// Using && (both must be true)
if (age >= 18 && hasLicense) {
  console.log("You can drive");
}

// Using || (at least one must be true)
if (age < 18 || age > 65) {
  console.log("You get a discount");
}

// Using ! (not - reverses the condition)
if (!hasLicense) {
  console.log("You need a license to drive");
}
```

## Ternary Operator

The ternary operator provides a shorthand for simple if/else:

```typescript
const age = 20;
const message = age >= 18 ? "Adult" : "Minor";
console.log(message); // Output: Adult

// Equivalent to:
let message2: string;
if (age >= 18) {
  message2 = "Adult";
} else {
  message2 = "Minor";
}
```

## Switch Statement

Use `switch` for multiple conditions based on a single value:

```typescript
const day = "Monday";

switch (day) {
  case "Monday":
    console.log("Start of the work week");
    break;
  case "Friday":
    console.log("End of the work week");
    break;
  case "Saturday":
  case "Sunday":
    console.log("Weekend!");
    break;
  default:
    console.log("Midweek day");
}
```

## Type Guards

TypeScript can narrow types based on conditions:

```typescript
function processValue(value: string | number) {
  if (typeof value === "string") {
    // TypeScript knows value is string here
    console.log(value.toUpperCase());
  } else {
    // TypeScript knows value is number here
    console.log(value * 2);
  }
}
```

# Common Mistakes

- **Using `=` instead of `===`**: `if (age = 18)` is assignment, use `if (age === 18)`
- **Forgetting `break` in switch**: Without `break`, execution falls through to next case
- **Using `==` instead of `===`**: Always use strict equality (`===`) in TypeScript
- **Confusing `&&` with `||`**: `&&` means both true, `||` means at least one true
- **Not handling all cases**: Make sure to handle all possible conditions

# Practice Exercises

1. Write a function that checks if a number is positive, negative, or zero.
2. Write a function that determines if a person can vote (must be 18 or older).
3. Write a function that assigns a letter grade based on a score.
4. Use a ternary operator to assign "Even" or "Odd" based on a number.
5. Write a switch statement that returns the day of the week name for a number (1-7).

Example solution for exercise 1:

```typescript
function checkNumber(num: number): string {
  if (num > 0) {
    return "Positive";
  } else if (num < 0) {
    return "Negative";
  } else {
    return "Zero";
  }
}

console.log(checkNumber(5)); // Output: Positive
console.log(checkNumber(-3)); // Output: Negative
console.log(checkNumber(0)); // Output: Zero
```

# Key Takeaways

- Use `if/else` for conditional execution
- Always use `===` for equality checks (strict equality)
- Use `else if` to check multiple conditions
- Combine conditions with `&&`, `||`, and `!`
- Use ternary operator for simple if/else: `condition ? value1 : value2`
- Use `switch` for multiple conditions based on a single value
- TypeScript can narrow types based on conditions (type guards)

# Related Topics

- Variables and Basic Types (TypeScript Beginner #1)
- Functions (TypeScript Beginner #2)
- Loops (next lesson)
