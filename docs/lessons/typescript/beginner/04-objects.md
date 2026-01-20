---
title: "Objects"
language: typescript
difficulty: beginner
prerequisites: ["Variables and Basic Types", "Arrays"]
keywords: [objects, properties, methods, key-value pairs, object literals, dot notation]
---

# Learning Objectives

- Create and work with objects in TypeScript
- Access object properties using dot notation and bracket notation
- Add, modify, and remove object properties
- Understand object type annotations
- Work with nested objects

# Prerequisites

- Variables and Basic Types
- Arrays

# Introduction

Objects are collections of key-value pairs. They're perfect for representing real-world entities like a person, a product, or any complex data structure. TypeScript adds type safety to objects, ensuring you use the correct property names and types.

# Core Concepts

## Creating Objects

You can create objects using object literals:

```typescript
// Object with properties
const person = {
  name: "Alice",
  age: 25,
  city: "New York",
};

// Empty object
const empty = {};

// Object with type annotation
const person: { name: string; age: number; city: string } = {
  name: "Alice",
  age: 25,
  city: "New York",
};
```

## Accessing Properties

You can access properties using dot notation or bracket notation:

```typescript
const person = {
  name: "Alice",
  age: 25,
};

// Dot notation (most common)
console.log(person.name); // Output: Alice
console.log(person.age); // Output: 25

// Bracket notation (useful for dynamic keys)
console.log(person["name"]); // Output: Alice

const key = "age";
console.log(person[key]); // Output: 25
```

## Modifying Objects

You can add, modify, and remove properties:

```typescript
const person: { name: string; age?: number } = {
  name: "Alice",
};

// Add property
person.age = 25;

// Modify property
person.name = "Bob";

// Remove property
delete person.age;
```

## Object Methods

Objects can contain functions (methods):

```typescript
const person = {
  name: "Alice",
  age: 25,
  greet: function () {
    console.log(`Hello, I'm ${this.name}`);
  },
  // Shorthand method syntax
  introduce() {
    console.log(`I'm ${this.name} and I'm ${this.age} years old`);
  },
};

person.greet(); // Output: Hello, I'm Alice
person.introduce(); // Output: I'm Alice and I'm 25 years old
```

## Type Annotations for Objects

You can define object types explicitly:

```typescript
// Inline type annotation
const person: { name: string; age: number; city: string } = {
  name: "Alice",
  age: 25,
  city: "New York",
};

// Using interface (recommended for reusable types)
interface Person {
  name: string;
  age: number;
  city: string;
}

const person: Person = {
  name: "Alice",
  age: 25,
  city: "New York",
};
```

## Optional Properties

You can make properties optional using `?`:

```typescript
interface Person {
  name: string;
  age: number;
  email?: string; // Optional property
}

const person1: Person = {
  name: "Alice",
  age: 25,
  // email is optional, so we can omit it
};

const person2: Person = {
  name: "Bob",
  age: 30,
  email: "bob@example.com",
};
```

## Nested Objects

Objects can contain other objects:

```typescript
interface Address {
  street: string;
  city: string;
  zipCode: string;
}

interface Person {
  name: string;
  age: number;
  address: Address;
}

const person: Person = {
  name: "Alice",
  age: 25,
  address: {
    street: "123 Main St",
    city: "New York",
    zipCode: "10001",
  },
};

console.log(person.address.city); // Output: New York
```

## Looping Through Objects

You can loop through object properties:

```typescript
const person = {
  name: "Alice",
  age: 25,
  city: "New York",
};

// Loop through keys
for (const key in person) {
  console.log(`${key}: ${person[key as keyof typeof person]}`);
}

// Using Object.keys()
Object.keys(person).forEach(key => {
  console.log(`${key}: ${person[key as keyof typeof person]}`);
});

// Using Object.entries()
Object.entries(person).forEach(([key, value]) => {
  console.log(`${key}: ${value}`);
});
```

# Common Mistakes

- **Accessing non-existent properties**: TypeScript will warn you if a property doesn't exist
- **Type mismatches**: Make sure property values match their types
- **Forgetting optional chaining**: Use `?.` to safely access nested properties
- **Mutating const objects**: You can modify properties of `const` objects, but can't reassign the object
- **Confusing object and array syntax**: Objects use `{}`, arrays use `[]`

# Practice Exercises

1. Create an object representing a book with title, author, and year properties.
2. Write a function that takes a person object and returns a greeting string.
3. Create an object with a method that calculates and returns the person's age in days.
4. Write a function that takes an object and returns an array of all its values.
5. Create a nested object (person with address) and write a function that formats the full address.

Example solution for exercise 1:

```typescript
interface Book {
  title: string;
  author: string;
  year: number;
}

const book: Book = {
  title: "The Great Gatsby",
  author: "F. Scott Fitzgerald",
  year: 1925,
};

console.log(book.title); // Output: The Great Gatsby
```

# Key Takeaways

- Objects are collections of key-value pairs created with `{}`
- Access properties using dot notation (`obj.property`) or brackets (`obj["property"]`)
- Objects can contain methods (functions as properties)
- Use interfaces to define object types for reusability
- Properties can be optional using `?`
- Objects can be nested (objects within objects)
- TypeScript ensures type safety for object properties

# Related Topics

- Variables and Basic Types (TypeScript Beginner #1)
- Arrays (TypeScript Beginner #3)
- Interfaces (TypeScript Intermediate #1)
- Classes (TypeScript Intermediate #2)
