---
title: "Testing Patterns"
language: python
difficulty: advanced
prerequisites: ["Functions", "Error Handling", "Object-Oriented Programming Basics"]
keywords: [testing, pytest, unittest, fixtures, mocking, test patterns, TDD, test coverage]
---

# Learning Objectives

- Write effective unit tests
- Use pytest for testing
- Create and use fixtures
- Mock external dependencies
- Understand test patterns and best practices
- Write integration tests
- Understand test coverage

# Prerequisites

- Functions
- Error Handling
- Object-Oriented Programming Basics

# Introduction

Testing is essential for maintaining code quality. Good tests catch bugs early, document expected behavior, and enable confident refactoring. Understanding testing patterns helps you write comprehensive, maintainable test suites. This lesson covers pytest, the most popular Python testing framework.

# Core Concepts

## Basic pytest Tests

```python
# test_math.py
def test_add():
    assert 2 + 2 == 4

def test_multiply():
    assert 3 * 4 == 12

# Run with: pytest test_math.py
```

## Test Functions

Test functions should start with `test_`:

```python
def test_divide():
    result = 10 / 2
    assert result == 5

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        10 / 0
```

## Fixtures

Reusable test setup:

```python
import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_sum(sample_data):
    assert sum(sample_data) == 15

def test_length(sample_data):
    assert len(sample_data) == 5
```

## Parametrized Tests

Test multiple inputs:

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

## Mocking

Mock external dependencies:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    mock_obj = Mock()
    mock_obj.method.return_value = "mocked"

    assert mock_obj.method() == "mocked"

# Mock external function
@patch('module.external_function')
def test_with_patch(mock_func):
    mock_func.return_value = "mocked"
    result = my_function()
    assert result == "mocked"
```

## Testing Classes

```python
class TestCalculator:
    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_subtract(self):
        calc = Calculator()
        assert calc.subtract(5, 3) == 2
```

## Test Organization

```python
# tests/test_user.py
class TestUser:
    def test_create_user(self):
        user = User("Alice", 25)
        assert user.name == "Alice"
        assert user.age == 25

    def test_user_validation(self):
        with pytest.raises(ValueError):
            User("", 25)  # Empty name should raise error
```

## Coverage

Measure test coverage:

```bash
pip install pytest-cov
pytest --cov=my_module tests/
```

# Common Mistakes

- **Testing implementation details**: Test behavior, not implementation
- **Not testing edge cases**: Test boundaries, empty inputs, None values
- **Over-mocking**: Don't mock everything - test real behavior when possible
- **Not cleaning up**: Use fixtures to ensure proper setup/teardown
- **Ignoring test failures**: Fix failing tests, don't ignore them

# Practice Exercises

1. Write tests for a function that calculates the area of a rectangle.
2. Create a fixture that sets up test data and use it in multiple tests.
3. Write parametrized tests for a function with multiple test cases.
4. Mock an external API call in a test.
5. Write tests that check both success and error cases.

Example solution for exercise 1:

```python
def calculate_area(length, width):
    if length <= 0 or width <= 0:
        raise ValueError("Length and width must be positive")
    return length * width

def test_calculate_area():
    assert calculate_area(5, 3) == 15

def test_calculate_area_negative():
    with pytest.raises(ValueError):
        calculate_area(-5, 3)
```

# Key Takeaways

- Write tests for all functions and classes
- Use pytest for modern Python testing
- Fixtures provide reusable test setup
- Parametrize tests to test multiple cases
- Mock external dependencies
- Test both success and error cases
- Measure test coverage
- Tests should be fast, isolated, and repeatable

# Related Topics

- Functions (Python Beginner #6)
- Error Handling (Python Intermediate #3)
- Object-Oriented Programming Basics (Python Intermediate #6)
