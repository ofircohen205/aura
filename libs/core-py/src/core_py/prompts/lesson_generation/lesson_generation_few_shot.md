# System Message

This file contains few-shot examples for lesson generation. These examples demonstrate how to generate effective lesson recommendations based on different error patterns and struggle scenarios.

# User Message

## Example 1: Type Error

**Input:**

- Edit Frequency: 12.5
- Error Logs: ["TypeError: 'NoneType' object is not callable"]
- History: ["Tried using dict.get() with default value"]

**Output:**
"Review how None values propagate through function calls. The error suggests you're trying to call a variable that is None. Check where the variable is assigned and ensure it's not None before calling it. Consider using type hints and None checks to catch these issues earlier."

## Example 2: Attribute Error

**Input:**

- Edit Frequency: 18.0
- Error Logs: ["AttributeError: 'str' object has no attribute 'append'"]
- History: []

**Output:**
"Lists and strings have different methods. The 'append' method is for lists, not strings. If you need to modify a string, consider using string concatenation, f-strings, or converting to a list first. Review Python's data type fundamentals to understand when to use lists vs strings."

## Example 3: Multiple Errors

**Input:**

- Edit Frequency: 22.0
- Error Logs: ["TypeError: unsupported operand type(s)", "NameError: name 'x' is not defined"]
- History: ["Attempted to use list comprehension"]

**Output:**
"Multiple errors suggest confusion about variable scope and type operations. Start by ensuring all variables are defined before use. Then verify the types of variables involved in operations match what the operation expects. Consider adding print statements to inspect variable types and values during debugging."

## Example 4: High Edit Frequency, No Errors

**Input:**

- Edit Frequency: 25.0
- Error Logs: []
- History: ["Refactoring code structure"]

**Output:**
"High edit frequency without errors suggests you're exploring different approaches. This is normal during refactoring. Consider breaking down the changes into smaller, testable increments. Write unit tests for each small change to ensure you're moving in the right direction."
