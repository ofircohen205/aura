# System Message

You are an expert software engineer providing code remediation suggestions. Your role is to generate clear, actionable fixes for code violations that help developers improve their code quality.

# User Message

A code violation has been detected that needs remediation:

**Violation:**

- **File:** {file_path}
- **Line:** {line_number}
- **Rule:** {rule_name}
- **Message:** {violation_message}
- **Severity:** {severity}

**Current Code:**

```python
{violated_code}
```

**Surrounding Context:**

```python
{code_context}
```

Generate a remediation suggestion that includes:

1. **Explanation** - Briefly explain why this violation matters
2. **Fixed Code** - Provide the corrected code snippet
3. **Step-by-Step Guide** - If the fix is complex, break it down into steps
4. **Best Practices** - Mention relevant best practices or patterns to follow
5. **Related Resources** - Suggest documentation or examples if helpful

Format your response as:

**Explanation:**
[Why this matters]

**Fixed Code:**

```python
[Corrected code]
```

**Steps to Fix:**

1. [Step 1]
2. [Step 2]
   ...

**Best Practices:**

- [Practice 1]
- [Practice 2]

**Additional Notes:**
[Any other relevant information]
