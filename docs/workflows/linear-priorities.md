# Linear Issue Priorities and Assignees

This guide explains how priorities and assignees are used in the Aura project.

## Priority Levels

Linear supports the following priority levels (numeric values):

- **1 - Urgent**: Critical issues that need immediate attention
- **2 - High**: Important features or bugs that should be prioritized
- **3 - Normal**: Standard priority for most tasks (default)
- **4 - Low**: Nice-to-have features or non-critical improvements

## Priority Guidelines

### Urgent (1)

- Production outages
- Critical security vulnerabilities
- Data loss or corruption issues
- Blocking issues preventing core functionality

### High (2)

- Core features needed for MVP
- Security-related features (authentication, authorization)
- Critical dependencies for other work
- High-impact bugs affecting many users

### Normal (3)

- Standard feature development
- UI/UX improvements
- Documentation updates
- Non-critical bug fixes
- Enhancement requests

### Low (4)

- Nice-to-have features
- Performance optimizations (non-critical)
- Code cleanup and refactoring (non-blocking)
- Future considerations

## Current Issue Priorities

### High Priority (2)

- **AURA-6**: Implement LangGraph Workflows - Core intelligence layer
- **AURA-7**: Setup RAG Pipeline - Required for lesson generation
- **AURA-9**: Implement Authentication - Security critical before production

### Normal Priority (3)

- **AURA-8**: Configure CI/CD Pipelines - Important but not blocking
- **AURA-10**: Enhance Web Dashboard - Depends on backend completion
- **AURA-11**: Enhance VSCode Extension - Depends on backend workflows
- **AURA-12**: Implement CLI Guardian Pre-commit Hooks - Nice to have

## Assignees

Issues are typically assigned to:

- **"me"** or your user ID - For issues you're working on
- Specific team members - For issues assigned to others
- Unassigned - For issues in backlog waiting for assignment

## Setting Priority and Assignee

### Via Justfile

```bash
# Create issue with priority and assignee
just linear-template feature "Title" "aura-dev" "High" "me"
```

### Via Linear MCP Tools

```python
# Priority: 1=Urgent, 2=High, 3=Normal, 4=Low
# Assignee: "me", user email, or user ID

mcp_Linear_create_issue(
    title="Feature Title",
    team="aura-dev",
    project="aura",
    priority=2,  # High
    assignee="me"
)
```

### Via Linear UI

1. Open the issue in Linear
2. Click the priority dropdown (top right)
3. Select priority level
4. Click assignee field
5. Select team member or "Unassigned"

## Best Practices

1. **Set priority when creating issues** - Don't leave everything as Normal
2. **Update priority as context changes** - Priorities can change over time
3. **Assign issues when starting work** - Helps track who's working on what
4. **Review priorities regularly** - Ensure they reflect current project needs
5. **Use High sparingly** - Reserve for truly important work

## Priority Matrix

| Impact | Urgency | Priority              |
| ------ | ------- | --------------------- |
| High   | High    | Urgent (1)            |
| High   | Low     | High (2)              |
| Low    | High    | High (2)              |
| Low    | Low     | Normal (3) or Low (4) |

## Related Documentation

- `docs/workflows/linear-automation.md` - Automation guide
- `docs/workflows/linear-integration.md` - Linear usage guide
- `docs/workflows/development-pipeline.md` - Development workflow
