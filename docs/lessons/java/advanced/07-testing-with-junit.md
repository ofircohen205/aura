---
title: "Testing with JUnit"
language: java
difficulty: advanced
prerequisites: ["Exception Handling", "Classes"]
keywords: [testing, JUnit, unit tests, assertions, test fixtures, mocking, test coverage]
---

# Learning Objectives

- Write unit tests with JUnit
- Use assertions effectively
- Set up test fixtures
- Test exceptions
- Use parameterized tests
- Understand test best practices

# Prerequisites

- Exception Handling
- Classes

# Introduction

Testing is essential for maintaining code quality. JUnit is the standard testing framework for Java. Understanding JUnit helps you write comprehensive test suites that catch bugs early and enable confident refactoring. Good tests document expected behavior and serve as examples.

# Core Concepts

## Basic Test

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    @Test
    void testAdd() {
        Calculator calc = new Calculator();
        int result = calc.add(5, 3);
        assertEquals(8, result);
    }
}
```

## Assertions

```java
@Test
void testAssertions() {
    assertEquals(5, 5);           // Equal
    assertNotEquals(5, 3);        // Not equal
    assertTrue(5 > 3);            // True condition
    assertFalse(5 < 3);           // False condition
    assertNull(null);             // Null check
    assertNotNull("hello");       // Not null
    assertSame(obj1, obj1);       // Same object reference
    assertNotSame(obj1, obj2);    // Different references
}
```

## Test Fixtures

Setup and teardown:

```java
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;

class UserServiceTest {
    private UserService userService;

    @BeforeEach
    void setUp() {
        userService = new UserService();
        // Setup before each test
    }

    @AfterEach
    void tearDown() {
        // Cleanup after each test
    }

    @Test
    void testCreateUser() {
        User user = userService.createUser("Alice", 25);
        assertNotNull(user);
        assertEquals("Alice", user.getName());
    }
}
```

## Testing Exceptions

```java
@Test
void testException() {
    Calculator calc = new Calculator();

    assertThrows(ArithmeticException.class, () -> {
        calc.divide(10, 0);
    });
}

@Test
void testExceptionMessage() {
    Exception exception = assertThrows(IllegalArgumentException.class, () -> {
        validateAge(-5);
    });

    assertEquals("Age cannot be negative", exception.getMessage());
}
```

## Parameterized Tests

Test multiple inputs:

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@ParameterizedTest
@ValueSource(ints = {2, 4, 6, 8})
void testIsEven(int number) {
    assertTrue(number % 2 == 0);
}
```

# Common Mistakes

- **Testing implementation details**: Test behavior, not implementation
- **Not testing edge cases**: Test boundaries, null, empty
- **Not cleaning up**: Use @AfterEach for cleanup
- **Ignoring test failures**: Fix failing tests
- **Not using descriptive test names**: Test names should describe what's tested

# Practice Exercises

1. Write tests for a Calculator class with add, subtract, multiply, divide methods.
2. Write tests that check exception throwing.
3. Use @BeforeEach to set up test data.
4. Write parameterized tests for a validation function.
5. Write tests for both success and failure cases.

Example solution for exercise 1:

```java
class CalculatorTest {
    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    @Test
    void testAdd() {
        assertEquals(8, calculator.add(5, 3));
    }

    @Test
    void testDivideByZero() {
        assertThrows(ArithmeticException.class, () -> {
            calculator.divide(10, 0);
        });
    }
}
```

# Key Takeaways

- JUnit is the standard Java testing framework
- Use @Test to mark test methods
- Use assertions to verify expected behavior
- @BeforeEach and @AfterEach for setup/teardown
- Test exceptions with assertThrows
- Use parameterized tests for multiple inputs
- Write tests for all methods and edge cases
- Tests should be fast, isolated, and repeatable

# Related Topics

- Exception Handling (Java Intermediate #6)
- Classes (Java Intermediate #1)
- Best Practices (covered in this lesson)
