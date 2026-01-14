# Development Pipeline

This document defines the standard development workflow for the Aura project, integrating Linear for task management and following a role-based development approach.

## Overview

The development pipeline follows these stages:

1. **Read Task/Story** - Understand requirements from Linear
2. **Plan Sub-tasks** - Break down into implementable pieces
3. **Create Branch** - Create feature branch from main
4. **Implement** - Each sub-task owned by dedicated role
5. **Write Tests** - Ensure code quality
6. **Code Review** - Review using appropriate roles
7. **Fix Issues** - Address review feedback
8. **Commit & Push** - Commit with proper conventions
9. **Create PR** - Open pull request for review

---

## Stage 1: Read Task/Story

### From Linear

1. **Get Task Details**

   ```bash
   # View task in Linear UI or use Linear CLI
   linear issue view <ISSUE_ID>
   ```

2. **Understand Requirements**
   - Read the issue description
   - Review acceptance criteria
   - Check linked issues/dependencies
   - Review assigned role (if any)

3. **Check Related Documentation**
   - Look for story files in `role_tasks/<role>/stories/`
   - Review architecture docs if needed
   - Check existing similar implementations

### From GitHub Issues

If using GitHub issues as backup:

```bash
# View issue
gh issue view <ISSUE_NUMBER>

# List issues
gh issue list
```

---

## Stage 2: Plan Sub-tasks

### Break Down the Task

1. **Identify Components**
   - What files need to be created/modified?
   - What layers are involved? (API, Service, Database, etc.)
   - What dependencies exist?

2. **Create Sub-tasks in Linear**

   ```bash
   # Create sub-issue in Linear
   linear issue create \
     --title "Sub-task: Implement X" \
     --parent <PARENT_ISSUE_ID> \
     --team <TEAM_NAME> \
     --assignee <YOUR_EMAIL>
   ```

3. **Assign Roles to Sub-tasks**
   - Each sub-task should have a clear owner role
   - Use role labels: `backend-engineer`, `frontend-engineer`, `security-engineer`, etc.
   - Reference role definitions: `@ai-coding-roles/roles/<role>/<role>.md`

### Sub-task Planning Template

For each sub-task, document:

- **Role**: Which AI coding role will implement this?
- **Files**: What files will be created/modified?
- **Dependencies**: What needs to be done first?
- **Tests**: What tests are needed?
- **Acceptance Criteria**: How do we know it's done?

---

## Stage 3: Create Branch

### Branch Naming Convention

**Format**: `<type>/<linear-id>-<short-description>`

**Types**:

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code improvements
- `chore/` - Maintenance tasks
- `test/` - Test additions

**Examples**:

```bash
feature/LIN-123-user-authentication
fix/LIN-456-login-bug
refactor/LIN-789-api-structure
```

### Create Branch Command

```bash
# Using Justfile command
just branch-create feature/LIN-123-user-auth

# Or manually
git checkout main
git pull origin main
git checkout -b feature/LIN-123-user-auth
```

---

## Stage 4: Implement (Role-Based)

### Role Assignment

Each sub-task should be implemented using the appropriate role:

1. **Identify the Role**
   - Check the sub-task description
   - Review `@ai-coding-roles/roles/` for available roles
   - Match role to task type (backend, frontend, security, etc.)

2. **Act as the Role**

   ```bash
   # When working on the task, reference the role
   # Example: "Act as @ai-coding-roles/roles/specialized-engineering/backend-engineer.md"
   ```

3. **Follow Role Guidelines**
   - Review the role definition file
   - Follow role-specific best practices
   - Use role-appropriate patterns and conventions

### Implementation Checklist

- [ ] Create/update files according to architecture
- [ ] Follow coding standards (SOLID, DRY, etc.)
- [ ] Add proper type hints (Python) or types (TypeScript)
- [ ] Include docstrings/comments
- [ ] Handle errors appropriately
- [ ] Log important events

---

## Stage 5: Write Tests

### Test Requirements

1. **Unit Tests**
   - Test individual functions/methods
   - Mock external dependencies
   - Cover edge cases

2. **Integration Tests**
   - Test component interactions
   - Test API endpoints
   - Test database operations

3. **Test Coverage**
   - Aim for 80%+ coverage on new code
   - Focus on business logic
   - Test error paths

### Running Tests

```bash
# Python tests
just test-py

# TypeScript tests
just test-ts

# All tests
just test
```

### Test File Structure

```
tests/
├── unit/
│   ├── test_services/
│   ├── test_core/
│   └── test_db/
├── integration/
│   ├── test_api/
│   └── test_workflows/
└── e2e/
    └── test_workflows/
```

---

## Stage 6: Code Review

### Review Process

1. **Self-Review First**

   ```bash
   # Run pre-commit hooks
   just lint

   # Run all tests
   just test

   # Check code review document
   cat CODE_REVIEW.md
   ```

2. **Role-Based Review**
   - Use appropriate roles for review
   - Backend changes: `@ai-coding-roles/roles/specialized-engineering/backend-engineer.md`
   - Security changes: `@ai-coding-roles/roles/quality-security/security-engineer.md`
   - Architecture changes: `@ai-coding-roles/roles/architecture-design/software-architect.md`

3. **Review Checklist**
   - [ ] Code follows project standards
   - [ ] Tests are comprehensive
   - [ ] Error handling is appropriate
   - [ ] Security considerations addressed
   - [ ] Performance is acceptable
   - [ ] Documentation is updated

### Automated Review

```bash
# Run code quality checks
just lint

# Run security checks
just security-check

# Generate code review
just code-review
```

---

## Stage 7: Fix Issues After Review

### Address Review Feedback

1. **Update Code**
   - Fix identified issues
   - Address security concerns
   - Improve based on suggestions

2. **Update Tests**
   - Add tests for edge cases
   - Fix failing tests
   - Improve coverage

3. **Re-run Checks**

   ```bash
   just lint
   just test
   ```

4. **Update Linear**
   - Comment on Linear issue with status
   - Mark sub-tasks as complete
   - Update parent issue progress

---

## Stage 8: Commit & Push

### Commit Message Convention

**Format**: `<type>(<scope>): <description> [LIN-<ID>]`

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `docs`: Documentation changes
- `chore`: Maintenance tasks

**Examples**:

```bash
feat(api): add user authentication endpoint [LIN-123]
fix(auth): resolve login token expiration bug [LIN-456]
refactor(services): extract workflow logic to service layer [LIN-789]
```

### Commit Process

```bash
# Stage changes
git add .

# Commit with message
git commit -m "feat(api): add user authentication endpoint [LIN-123]"

# Push to remote
git push origin feature/LIN-123-user-auth
```

### Pre-commit Hooks

Pre-commit hooks run automatically:

- Code formatting (ruff, prettier)
- Linting (ruff, eslint)
- Type checking (mypy, tsc)
- Security checks (bandit)

---

## Stage 9: Create Pull Request

### PR Creation

1. **Create PR via GitHub CLI**

   ```bash
   gh pr create \
     --title "feat: User Authentication [LIN-123]" \
     --body "Implements user authentication endpoint

   - [x] Added authentication service
   - [x] Created API endpoints
   - [x] Added tests
   - [x] Updated documentation

   Closes LIN-123"
   ```

2. **Or via GitHub UI**
   - Go to repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in PR template

### PR Template

```markdown
## Description

Brief description of changes

## Linear Issue

Closes LIN-123

## Type of Change

- [ ] Feature
- [ ] Bug fix
- [ ] Refactor
- [ ] Documentation

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project standards
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### PR Review

1. **Wait for Review**
   - Assign reviewers if needed
   - Link Linear issue in PR description
   - Update Linear issue with PR link

2. **Address Review Comments**
   - Make requested changes
   - Push updates to branch
   - Respond to comments

3. **Merge**
   - After approval, merge PR
   - Delete feature branch
   - Update Linear issue status

---

## Quick Reference Commands

### Using Justfile (Docker-Based)

All commands run inside Docker containers. Start services first with `just dev`.

```bash
# Start development environment
just dev

# Create branch (runs on host)
just branch-create <branch-name>

# Run tests (in Docker)
just test
just test-py
just test-ts

# Lint code (in Docker)
just lint
just lint-fix

# Code review (in Docker)
just code-review

# Create PR (runs on host)
just pr-create <title> <description>

# Docker utilities
just docker-shell        # Get shell in dev-tools container
just docker-exec "cmd"   # Run command in dev-tools container
just dev-logs            # View all logs
```

### Manual Git Commands

```bash
# Create and switch to branch
git checkout -b feature/LIN-123-description

# Commit changes
git add .
git commit -m "feat(scope): description [LIN-123]"

# Push branch
git push origin feature/LIN-123-description

# Create PR
gh pr create --title "Title" --body "Description"
```

---

## Linear Integration

### Linking Linear Issues

1. **In Commit Messages**

   ```bash
   git commit -m "feat(api): add endpoint [LIN-123]"
   ```

2. **In PR Description**

   ```markdown
   Closes LIN-123
   ```

3. **In Code Comments**
   ```python
   # TODO: Refactor this after LIN-456
   ```

### Linear Workflow

1. **Create Issue**

   ```bash
   linear issue create \
     --title "Feature: User Authentication" \
     --team "Engineering" \
     --assignee "me"
   ```

2. **Update Issue Status**

   ```bash
   linear issue update LIN-123 --state "In Progress"
   linear issue update LIN-123 --state "In Review"
   linear issue update LIN-123 --state "Done"
   ```

3. **Link PR to Issue**
   - Add `Closes LIN-123` in PR description
   - Linear will auto-update when PR is merged

---

## Best Practices

1. **One Issue = One Branch = One PR**
   - Keep branches focused
   - Don't mix unrelated changes

2. **Small, Incremental PRs**
   - Easier to review
   - Faster to merge
   - Lower risk

3. **Always Run Tests Before Pushing**
   - Catch issues early
   - Don't break CI

4. **Update Documentation**
   - Keep docs in sync with code
   - Update README if needed

5. **Communicate in Linear**
   - Update issue status
   - Add comments for blockers
   - Link related issues

---

## Troubleshooting

### Pre-commit Hooks Failing

```bash
# Run hooks manually to see errors
just lint

# Fix auto-fixable issues
just lint-fix

# Skip hooks (not recommended)
git commit --no-verify
```

### Tests Failing

```bash
# Run tests with verbose output
just test -v

# Run specific test file
just test tests/test_specific.py

# Debug test
just test --pdb
```

### Merge Conflicts

```bash
# Update branch from main
git checkout main
git pull origin main
git checkout feature/LIN-123-branch
git merge main

# Resolve conflicts, then
git add .
git commit -m "chore: resolve merge conflicts [LIN-123]"
```
