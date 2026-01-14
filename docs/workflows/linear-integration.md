# Linear Integration Guide

This guide explains how to use Linear for project management in the Aura project.

## Setup

### 1. Linear Workspace

The project uses Linear for task management. Access the workspace at: https://linear.app

### 2. Team Structure

- **Team**: Ofircohen
- **Projects**: Create projects for major features/epics
- **Labels**: Use role-based labels (backend-engineer, frontend-engineer, etc.)

## Creating Issues

### From Command Line (MCP)

```bash
# Create issue using Linear MCP tools
# In Cursor, use: "Create Linear issue for..."
```

### From Linear UI

1. Go to Linear workspace
2. Click "New Issue"
3. Fill in:
   - **Title**: Clear, descriptive title
   - **Description**: Detailed description with acceptance criteria
   - **Team**: Select appropriate team
   - **Labels**: Add role labels
   - **Assignee**: Assign to yourself or team member

## Issue Naming Convention

**Format**: `<Type>: <Description>`

**Types**:

- `Feature:` - New features
- `Fix:` - Bug fixes
- `Refactor:` - Code improvements
- `Chore:` - Maintenance tasks
- `Docs:` - Documentation updates

**Examples**:

- `Feature: User Authentication`
- `Fix: Login Token Expiration`
- `Refactor: API Structure`

## Linking Issues to Code

### In Commit Messages

```bash
git commit -m "feat(api): add authentication endpoint [LIN-123]"
```

### In PR Descriptions

```markdown
Closes LIN-123
```

### In Code Comments

```python
# TODO: Refactor this after LIN-456
# See LIN-789 for context
```

## Issue Workflow States

1. **Backlog** - Not started
2. **Todo** - Ready to start
3. **In Progress** - Currently working on
4. **In Review** - PR created, awaiting review
5. **Done** - Merged and deployed

## Sub-tasks

### Creating Sub-tasks

Break down large issues into sub-tasks:

1. Create parent issue
2. Create sub-issues linked to parent
3. Assign roles to each sub-task
4. Track progress on parent issue

### Sub-task Template

- **Title**: `Sub-task: <Description>`
- **Parent**: Link to parent issue
- **Role**: Assign appropriate role label
- **Acceptance Criteria**: Clear completion criteria

## Role-Based Labels

Use labels to indicate which role should work on an issue:

- `backend-engineer` - Backend/API work
- `frontend-engineer` - Frontend/UI work
- `security-engineer` - Security-related work
- `qa-engineer` - Testing/QA work
- `devops-engineer` - Infrastructure/CI/CD work
- `software-architect` - Architecture decisions

## Projects

Create Linear projects for:

- **Epics**: Large features spanning multiple issues
- **Sprints**: Time-boxed development cycles
- **Releases**: Version releases

## Automation

### GitHub Integration

Linear can automatically:

- Create Linear issues from GitHub issues
- Update Linear status when PRs are created/merged
- Link commits to Linear issues

### Setup GitHub Integration

1. Go to Linear Settings → Integrations
2. Connect GitHub repository
3. Configure sync rules
4. Enable automatic linking

## Best Practices

1. **One Issue = One Branch = One PR**
   - Keep issues focused
   - Don't mix unrelated changes

2. **Update Status Regularly**
   - Move to "In Progress" when starting
   - Move to "In Review" when PR is ready
   - Move to "Done" when merged

3. **Use Comments**
   - Add comments for blockers
   - Update progress in comments
   - Link related issues

4. **Break Down Large Issues**
   - Create sub-tasks for complex features
   - Make sub-tasks independently completable

5. **Link Related Issues**
   - Use "Blocks" for dependencies
   - Use "Related" for connected work
   - Use "Duplicate" for duplicates

## Commands Reference

### View Issue

```bash
# In Cursor, use Linear MCP tools
# Or use Linear CLI if installed
linear issue view LIN-123
```

### Update Issue Status

```bash
# Move to In Progress
linear issue update LIN-123 --state "In Progress"

# Move to In Review
linear issue update LIN-123 --state "In Review"

# Move to Done
linear issue update LIN-123 --state "Done"
```

### Create Comment

```bash
# Add comment to issue
linear issue comment LIN-123 "Working on this now"
```

## Troubleshooting

### Issue Not Found

- Check issue ID format (LIN-123)
- Verify you have access to the workspace
- Check if issue was deleted/archived

### Can't Update Status

- Verify you have permissions
- Check if issue is in correct project
- Ensure status transition is valid

### GitHub Not Syncing

- Check integration settings
- Verify repository connection
- Review sync rules configuration
