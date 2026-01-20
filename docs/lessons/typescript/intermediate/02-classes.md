---
title: "Classes"
language: typescript
difficulty: intermediate
prerequisites: ["Interfaces", "Objects"]
keywords:
  [classes, inheritance, constructors, access modifiers, static, abstract classes, implements]
---

# Learning Objectives

- Create classes with TypeScript
- Understand access modifiers (public, private, protected)
- Use constructors and super()
- Implement interfaces in classes
- Create abstract classes
- Understand static members
- Work with inheritance

# Prerequisites

- Interfaces
- Objects

# Introduction

Classes in TypeScript are similar to JavaScript classes but with type safety. TypeScript adds access modifiers, interfaces, and better inheritance support. Understanding classes is essential for object-oriented programming in TypeScript.

# Core Concepts

## Basic Class

```typescript
class Person {
  name: string;
  age: number;

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
  }

  greet(): void {
    console.log(`Hello, I'm ${this.name}`);
  }
}

const person = new Person("Alice", 25);
person.greet(); // Output: Hello, I'm Alice
```

## Access Modifiers

Control visibility of class members:

```typescript
class BankAccount {
  public balance: number; // Accessible everywhere
  private accountNumber: string; // Only accessible in this class
  protected owner: string; // Accessible in this class and subclasses

  constructor(accountNumber: string, owner: string) {
    this.accountNumber = accountNumber;
    this.owner = owner;
    this.balance = 0;
  }

  public deposit(amount: number): void {
    this.balance += amount;
  }

  private validateAmount(amount: number): boolean {
    return amount > 0;
  }
}

const account = new BankAccount("12345", "Alice");
account.balance = 100; // OK - public
// account.accountNumber;  // Error - private
```

## Inheritance

Classes can extend other classes:

```typescript
class Animal {
  constructor(public name: string) {}

  move(distance: number = 0): void {
    console.log(`${this.name} moved ${distance}m`);
  }
}

class Dog extends Animal {
  constructor(
    name: string,
    public breed: string
  ) {
    super(name); // Call parent constructor
  }

  bark(): void {
    console.log("Woof!");
  }
}

const dog = new Dog("Buddy", "Labrador");
dog.move(10); // Inherited method
dog.bark(); // Own method
```

## Implementing Interfaces

Classes can implement interfaces:

```typescript
interface Drawable {
  draw(): void;
}

class Circle implements Drawable {
  constructor(private radius: number) {}

  draw(): void {
    console.log(`Drawing circle with radius ${this.radius}`);
  }
}

class Rectangle implements Drawable {
  constructor(
    private width: number,
    private height: number
  ) {}

  draw(): void {
    console.log(`Drawing rectangle ${this.width}x${this.height}`);
  }
}
```

## Abstract Classes

Cannot be instantiated directly:

```typescript
abstract class Shape {
  abstract area(): number; // Must be implemented by subclasses

  display(): void {
    console.log(`Area: ${this.area()}`);
  }
}

class Rectangle extends Shape {
  constructor(
    private width: number,
    private height: number
  ) {
    super();
  }

  area(): number {
    // Must implement abstract method
    return this.width * this.height;
  }
}

// const shape = new Shape();  // Error! Cannot instantiate abstract class
const rect = new Rectangle(5, 3);
rect.display(); // Output: Area: 15
```

## Static Members

Belong to the class, not instances:

```typescript
class MathUtils {
  static PI = 3.14159;

  static add(a: number, b: number): number {
    return a + b;
  }
}

console.log(MathUtils.PI); // Access via class
console.log(MathUtils.add(5, 3)); // Output: 8

// No need to create instance
```

## Getters and Setters

```typescript
class Person {
  private _age: number = 0;

  get age(): number {
    return this._age;
  }

  set age(value: number) {
    if (value >= 0) {
      this._age = value;
    } else {
      throw new Error("Age cannot be negative");
    }
  }
}

const person = new Person();
person.age = 25; // Uses setter
console.log(person.age); // Uses getter - Output: 25
```

# Common Mistakes

- **Forgetting `super()` in derived classes**: Must call parent constructor
- **Using `this` before `super()`**: `super()` must be called first
- **Confusing access modifiers**: `private` vs `protected` vs `public`
- **Trying to instantiate abstract classes**: They're meant to be extended
- **Not implementing abstract methods**: Subclasses must implement them

# Practice Exercises

1. Create a class hierarchy (Animal -> Dog, Cat) with inheritance.
2. Create a class that implements an interface.
3. Create an abstract class with abstract methods.
4. Create a class with private, protected, and public members.
5. Create a class with static methods and properties.

Example solution for exercise 1:

```typescript
class Animal {
  constructor(public name: string) {}

  speak(): void {
    console.log("Some animal sound");
  }
}

class Dog extends Animal {
  speak(): void {
    console.log("Woof!");
  }
}

class Cat extends Animal {
  speak(): void {
    console.log("Meow!");
  }
}

const dog = new Dog("Buddy");
dog.speak(); // Output: Woof!
```

# Key Takeaways

- Classes provide object-oriented programming in TypeScript
- Access modifiers control visibility: `public`, `private`, `protected`
- Use `extends` for inheritance, `super()` to call parent constructor
- Classes can `implements` interfaces
- Abstract classes cannot be instantiated, must be extended
- Static members belong to the class, not instances
- Getters and setters provide controlled access to properties
- TypeScript adds type safety to JavaScript classes

# Related Topics

- Interfaces (TypeScript Intermediate #1)
- Inheritance (covered in this lesson)
- Generics (TypeScript Advanced #1)
