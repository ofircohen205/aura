---
title: "Annotations"
language: java
difficulty: advanced
prerequisites: ["Classes", "Interfaces"]
keywords: [annotations, @Override, @Deprecated, custom annotations, metadata, reflection]
---

# Learning Objectives

- Understand what annotations are
- Use built-in annotations
- Create custom annotations
- Process annotations with reflection
- Understand annotation retention
- Use annotations effectively

# Prerequisites

- Classes
- Interfaces

# Introduction

Annotations provide metadata about code. They don't change program execution but provide information to compilers, tools, and frameworks. Understanding annotations is essential for working with modern Java frameworks and creating clean, declarative code.

# Core Concepts

## Built-in Annotations

### @Override

Indicates method overrides parent method:

```java
class Parent {
    public void method() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    @Override
    public void method() {
        System.out.println("Child");
    }
}
```

### @Deprecated

Marks code as deprecated:

```java
@Deprecated
public void oldMethod() {
    // Old implementation
}

@Deprecated(since = "2.0", forRemoval = true)
public void veryOldMethod() {
    // Will be removed
}
```

### @SuppressWarnings

Suppress compiler warnings:

```java
@SuppressWarnings("unchecked")
List list = new ArrayList();
```

## Creating Custom Annotations

```java
// Marker annotation (no elements)
@interface MyAnnotation {
}

// Single element annotation
@interface Author {
    String value();  // Special: if only one element named "value", can omit name
}

// Multiple elements
@interface Book {
    String title();
    String author();
    int year();
}

// Usage
@Author("John Doe")
@Book(title = "Java Guide", author = "Jane Smith", year = 2024)
class MyClass {
}
```

## Annotation Retention

Control when annotation is available:

```java
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

@Retention(RetentionPolicy.RUNTIME)  // Available at runtime
@interface RuntimeAnnotation {
}

@Retention(RetentionPolicy.SOURCE)  // Discarded by compiler
@interface SourceAnnotation {
}

@Retention(RetentionPolicy.CLASS)  // In class file, not runtime
@interface ClassAnnotation {
}
```

## Processing Annotations

```java
@Retention(RetentionPolicy.RUNTIME)
@interface Test {
    String description() default "";
}

class TestRunner {
    @Test(description = "Test method 1")
    public void test1() {
        System.out.println("Running test 1");
    }

    @Test
    public void test2() {
        System.out.println("Running test 2");
    }

    public void runTests() {
        Method[] methods = this.getClass().getMethods();
        for (Method method : methods) {
            if (method.isAnnotationPresent(Test.class)) {
                Test test = method.getAnnotation(Test.class);
                System.out.println("Running: " + test.description());
                try {
                    method.invoke(this);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
```

# Common Mistakes

- **Not using @Override**: Helps catch errors
- **Wrong retention policy**: Need RUNTIME for reflection access
- **Overusing annotations**: Don't annotate everything
- **Not understanding annotation processing**: Annotations need processors

# Practice Exercises

1. Create a custom annotation for marking test methods.
2. Use reflection to find and process annotated methods.
3. Create an annotation with multiple elements.
4. Create an annotation with default values.
5. Use built-in annotations appropriately in your code.

Example solution for exercise 1:

```java
@Retention(RetentionPolicy.RUNTIME)
@interface Test {
    String name() default "";
    boolean enabled() default true;
}

class TestSuite {
    @Test(name = "Addition Test")
    public void testAddition() {
        System.out.println("Testing addition");
    }

    @Test(name = "Subtraction Test", enabled = false)
    public void testSubtraction() {
        System.out.println("Testing subtraction");
    }
}
```

# Key Takeaways

- Annotations provide metadata about code
- Built-in annotations: @Override, @Deprecated, @SuppressWarnings
- Create custom annotations with @interface
- Retention policy controls when annotation is available
- Use reflection to process annotations at runtime
- Annotations are used extensively by frameworks
- Use annotations to add declarative metadata

# Related Topics

- Classes (Java Intermediate #1)
- Reflection (Java Advanced #5)
- Testing (covered in advanced topics)
