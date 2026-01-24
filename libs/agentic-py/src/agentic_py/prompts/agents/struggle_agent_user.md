# Context

The user is struggling with the following indicators:

**Edit Frequency**: {edit_frequency} edits per time unit

- This indicates how frequently the user is making changes
- High frequency (>10) suggests the user is stuck or trying multiple approaches
- Low frequency (<5) with errors suggests the user is blocked

**Error Logs**:
{error_logs}

**Previous Attempts/History**:
{history}

## Your Task

Please generate a personalized lesson recommendation that:

1. **Addresses the specific errors** - Focus on the actual error messages and what they indicate
2. **Uses tools proactively** - Use `retrieve_knowledge` or `retrieve_contextual_lesson` to find relevant documentation before generating the lesson
3. **Provides actionable guidance** - Give concrete steps or concepts to learn
4. **Avoids repetition** - Don't suggest things they've already tried (based on history)
5. **Matches their struggle level** - Adjust complexity based on edit frequency and error patterns
6. **References retrieved context** - Use information from tools to provide accurate, project-specific guidance

## Instructions

- **Always use tools first** if you're unsure about an error or need more context
- **Be specific** in your tool queries - better queries = better results
- **Synthesize information** from tools to create comprehensive guidance
- **Keep lessons concise** - 2-4 sentences that are immediately actionable
- **Be educational** - Explain the underlying concept, not just the fix

Generate your lesson recommendation now.
