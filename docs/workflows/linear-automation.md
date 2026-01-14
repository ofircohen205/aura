# Linear Automation Guide

This guide explains how to use the Linear automation scripts and workflows.

## Linear Issue Templates

Templates are available in `scripts/linear-templates/`:

- **feature-template.md** - For new features
- **bug-template.md** - For bug reports
- **refactor-template.md** - For refactoring tasks

### Creating Issues from Templates

```bash
# Using Justfile command (with priority and assignee)
just linear-template feature "Implement user authentication" "aura-dev" "High" "me"

# Priority options: Urgent (1), High (2), Normal (3), Low (4)
# Assignee: User email, name, or "me" for yourself

# Or directly with script
bash scripts/create-linear-issue.sh feature "Implement user authentication" "aura-dev" "aura" "High" "me"
```

## Branch Creation with Linear Linking

Create a branch that's automatically linked to a Linear issue:

```bash
# Using Justfile command
just branch-linear AURA-123 "implement feature"

# Or directly with script
bash scripts/branch-with-linear.sh AURA-123 "implement feature"
```

This will:

1. Create a branch named `feature/AURA-123-implement-feature`
2. Ensure you're on the latest main branch
3. Check out the new branch
4. Provide next steps for committing and creating PRs

## PR Creation with Linear Linking

Create a PR that automatically links to a Linear issue:

```bash
# Using Justfile command
just pr-linear "Implement feature" "Description of changes" AURA-123
```

This will:

1. Create a PR with the specified title and description
2. Add a "Closes AURA-123" line to the PR body
3. Include a link to view the issue in Linear

## GitHub Actions Integration

The `.github/workflows/linear-sync.yml` workflow automatically:

1. **Extracts Linear Issue ID** from:
   - PR body (looks for `AURA-XXX` pattern)
   - Branch name (if not found in PR body)

2. **Comments on PR** with a link to the Linear issue

3. **Updates Linear Status** (requires `LINEAR_API_KEY` secret):
   - When PR is opened → Sets issue to "In Review"
   - When PR is merged → Sets issue to "Done"
   - When PR is closed → Sets issue back to "In Progress"

### Setting Up Linear API Key

To enable automatic status updates:

1. Get your Linear API key from: https://linear.app/settings/api
2. Add it to GitHub Secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add new secret: `LINEAR_API_KEY`
   - Paste your Linear API key

### Manual Status Updates

If you don't have a Linear API key set up, the workflow will still:

- Extract and display the issue ID
- Comment on the PR with a link
- Provide instructions for manual status updates

## Workflow Examples

### Complete Workflow

```bash
# 1. Create Linear issue (manually in Linear or using template)
# Issue ID: AURA-123

# 2. Create branch linked to issue
just branch-linear AURA-123 "implement authentication"

# 3. Make changes and commit
git add .
just commit "feat(auth): add JWT authentication [AURA-123]"

# 4. Push branch
just push

# 5. Create PR linked to issue
just pr-linear "Implement JWT Authentication" "Adds JWT-based authentication system" AURA-123
```

## Best Practices

1. **Always link branches to Linear issues** - Use `branch-linear` instead of `branch-create`
2. **Include issue ID in commit messages** - Format: `feat(scope): description [AURA-123]`
3. **Use PR template** - The template includes a section for Linear issue linking
4. **Update issue status manually if needed** - If automation isn't working, update status in Linear UI

## Troubleshooting

### Issue ID not found in PR

The workflow looks for `AURA-XXX` pattern in:

1. PR body (first occurrence)
2. Branch name (if not in PR body)

Make sure your PR body includes: `Closes AURA-123` or your branch is named `feature/AURA-123-description`

### Linear API key not working

1. Verify the key is correct in GitHub Secrets
2. Check Linear API key permissions
3. Review GitHub Actions logs for error messages

### Branch name format

Branch names should follow: `feature/AURA-123-description` or `fix/AURA-123-description`

The script automatically:

- Normalizes issue IDs (handles with or without AURA- prefix)
- Converts spaces to hyphens
- Creates appropriate branch name
