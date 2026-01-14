# Development Pipeline Summary

## Quick Start

The development pipeline follows these 9 stages:

1. **Read Task** → 2. **Plan Sub-tasks** → 3. **Create Branch** → 4. **Implement** → 5. **Write Tests** → 6. **Code Review** → 7. **Fix Issues** → 8. **Commit & Push** → 9. **Create PR**

## Key Commands

### Branch Management

```bash
# Create feature branch
just branch-create feature/OFI-123-description

# Check current branch
just branch

# Pull latest from main
just pull-main
```

### Testing

```bash
# Run all tests
just test

# Run Python tests only
just test-py

# Run TypeScript tests only
just test-ts
```

### Code Quality

```bash
# Run all linting
just lint

# Auto-fix linting issues
just lint-fix

# Run code review checks
just code-review

# Run security checks
just security-check
```

### Git Workflow

```bash
# Commit with message
just commit "feat(api): add endpoint [OFI-123]"

# Push current branch
just push

# Create PR
just pr-create "Title" "Description"
```

## Linear Integration

### Issue Format

- **Issue ID**: `OFI-123` (format: `<TEAM>-<NUMBER>`)
- **Branch**: `feature/OFI-123-description`
- **Commit**: `feat(scope): description [OFI-123]`
- **PR**: `Closes OFI-123`

### Workflow States

1. **Backlog** → 2. **Todo** → 3. **In Progress** → 4. **In Review** → 5. **Done**

## Role-Based Development

Each task should be implemented using the appropriate role:

- **Backend**: `@ai-coding-roles/roles/specialized-engineering/backend-engineer.md`
- **Frontend**: `@ai-coding-roles/roles/specialized-engineering/frontend-engineer.md`
- **Security**: `@ai-coding-roles/roles/quality-security/security-engineer.md`
- **QA**: `@ai-coding-roles/roles/quality-security/qa-engineer.md`
- **DevOps**: `@ai-coding-roles/roles/infrastructure-operations/devops-engineer.md`
- **Architect**: `@ai-coding-roles/roles/architecture-design/software-architect.md`

## Documentation

- **Full Pipeline**: `docs/workflows/development-pipeline.md`
- **Linear Guide**: `docs/workflows/linear-integration.md`
- **Git Workflow**: `docs/workflows/development-workflows.md`
- **PR Template**: `.github/pull_request_template.md`

## Example Workflow

```bash
# 1. Read task in Linear (OFI-123)
# 2. Plan sub-tasks
# 3. Create branch
just branch-create feature/OFI-123-user-auth

# 4. Implement (using appropriate role)
# ... make changes ...

# 5. Write tests
just test

# 6. Code review
just code-review

# 7. Fix issues (if any)
just lint-fix
just test

# 8. Commit & push
just commit "feat(auth): add user authentication [OFI-123]"
just push

# 9. Create PR
just pr-create "feat: User Authentication [OFI-123]" "Implements user auth endpoint. Closes OFI-123"
```

## Best Practices

1. ✅ One issue = One branch = One PR
2. ✅ Small, incremental PRs
3. ✅ Always run tests before pushing
4. ✅ Update Linear issue status regularly
5. ✅ Use role-based development
6. ✅ Follow commit message conventions
7. ✅ Link Linear issues in commits and PRs
