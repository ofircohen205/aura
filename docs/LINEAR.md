# Linear Integration Guide

This guide explains how to use Linear for project management in the Aura project, including setup, automation, priorities, and best practices.

## Table of Contents

1. [Setup](#setup)
2. [Project Overview](#project-overview)
3. [Creating Issues](#creating-issues)
4. [Issue Priorities and Assignees](#issue-priorities-and-assignees)
5. [Automation](#automation)
6. [Linking Issues to Code](#linking-issues-to-code)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Setup

### Linear Workspace

The project uses Linear for task management. Access the workspace at: https://linear.app

### Team Structure

- **Team**: Ofircohen
- **Projects**: Create projects for major features/epics
- **Labels**: Use role-based labels (backend-engineer, frontend-engineer, etc.)

### Project Created: Aura

**Project ID**: `59b932cb-bd81-4890-bd7d-5c4c5617a34c`  
**URL**: https://linear.app/ofircohen/project/aura-65ac108335af

## Project Overview

Aura is an AI-powered code analysis and learning platform that helps developers improve their coding skills through intelligent feedback, struggle detection, and personalized lessons.

### Key Features

1. **Struggle Detection Workflow** - Analyzes edit patterns to detect developer struggles
2. **Code Audit Workflow** - Performs static analysis and violation checking
3. **Event Ingestion** - Collects and processes development events
4. **RESTful API** - Well-structured API with proper error handling
5. **Web Dashboard** - Next.js dashboard for visualization
6. **VSCode Integration** - Extension for IDE integration
7. **CLI Tool** - Command-line interface for local analysis

### Labels Created

**Role-based labels:**

- `backend-engineer` - Backend/API development tasks
- `frontend-engineer` - Frontend/web development tasks
- `security-engineer` - Security-related tasks
- `devops-engineer` - Infrastructure and CI/CD tasks
- `qa-engineer` - Testing and quality assurance
- `software-architect` - Architecture decisions
- `ml-engineer` - Machine learning and AI tasks

**Component labels:**

- `backend` - Backend development
- `frontend` - Frontend development
- `cli` - CLI development
- `vscode` - VSCode extension
- `ml` - Machine learning
- `infrastructure` - Infrastructure tasks

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

### Issue Naming Convention

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

### Issue Structure

Each issue should include:

1. **Objective** - Clear goal statement
2. **Background** - Context and rationale
3. **Requirements** - Detailed checklist of tasks
4. **Technical Details** - Architecture and implementation notes
5. **Dependencies** - Prerequisites and related work
6. **Acceptance Criteria** - Definition of done
7. **Related Files** - Code locations and documentation
8. **Story Reference** - Links to detailed story documents

### Linear Issue Templates

Templates are available in `scripts/linear-templates/`:

- **feature-template.md** - For new features
- **bug-template.md** - For bug reports
- **refactor-template.md** - For refactoring tasks

**Creating Issues from Templates:**

```bash
# Using Justfile command (with priority and assignee)
just linear-template feature "Implement user authentication" "aura-dev" "High" "me"

# Priority options: Urgent (1), High (2), Normal (3), Low (4)
# Assignee: User email, name, or "me" for yourself

# Or directly with script
bash scripts/create-linear-issue.sh feature "Implement user authentication" "aura-dev" "aura" "High" "me"
```

## Issue Priorities and Assignees

### Priority Levels

Linear supports the following priority levels (numeric values):

- **1 - Urgent**: Critical issues that need immediate attention
- **2 - High**: Important features or bugs that should be prioritized
- **3 - Normal**: Standard priority for most tasks (default)
- **4 - Low**: Nice-to-have features or non-critical improvements

### Priority Guidelines

**Urgent (1):**

- Production outages
- Critical security vulnerabilities
- Data loss or corruption issues
- Blocking issues preventing core functionality

**High (2):**

- Core features needed for MVP
- Security-related features (authentication, authorization)
- Critical dependencies for other work
- High-impact bugs affecting many users

**Normal (3):**

- Standard feature development
- UI/UX improvements
- Documentation updates
- Non-critical bug fixes
- Enhancement requests

**Low (4):**

- Nice-to-have features
- Performance optimizations (non-critical)
- Code cleanup and refactoring (non-blocking)
- Future considerations

### Priority Matrix

| Impact | Urgency | Priority              |
| ------ | ------- | --------------------- |
| High   | High    | Urgent (1)            |
| High   | Low     | High (2)              |
| Low    | High    | High (2)              |
| Low    | Low     | Normal (3) or Low (4) |

### Assignees

Issues are typically assigned to:

- **"me"** or your user ID - For issues you're working on
- Specific team members - For issues assigned to others
- Unassigned - For issues in backlog waiting for assignment

### Setting Priority and Assignee

**Via Justfile:**

```bash
# Create issue with priority and assignee
just linear-template feature "Title" "aura-dev" "High" "me"
```

**Via Linear MCP Tools:**

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

**Via Linear UI:**

1. Open the issue in Linear
2. Click the priority dropdown (top right)
3. Select priority level
4. Click assignee field
5. Select team member or "Unassigned"

## Automation

### Branch Creation with Linear Linking

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

### PR Creation with Linear Linking

Create a PR that automatically links to a Linear issue:

```bash
# Using Justfile command
just pr-linear "Implement feature" "Description of changes" AURA-123
```

This will:

1. Create a PR with the specified title and description
2. Add a "Closes AURA-123" line to the PR body
3. Include a link to view the issue in Linear

### GitHub Actions Integration

The `.github/workflows/linear-sync.yml` workflow automatically:

1. **Extracts Linear Issue ID** from:
   - PR body (looks for `AURA-XXX` pattern)
   - Branch name (if not found in PR body)

2. **Comments on PR** with a link to the Linear issue

3. **Updates Linear Status** (requires `LINEAR_API_KEY` secret):
   - When PR is opened → Sets issue to "In Review"
   - When PR is merged → Sets issue to "Done"
   - When PR is closed → Sets issue back to "In Progress"

**Setting Up Linear API Key:**

1. Get your Linear API key from: https://linear.app/settings/api
2. Add it to GitHub Secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add new secret: `LINEAR_API_KEY`
   - Paste your Linear API key

**Manual Status Updates:**

If you don't have a Linear API key set up, the workflow will still:

- Extract and display the issue ID
- Comment on the PR with a link
- Provide instructions for manual status updates

### GitHub Integration

Linear can automatically:

- Create Linear issues from GitHub issues
- Update Linear status when PRs are created/merged
- Link commits to Linear issues

**Setup GitHub Integration:**

1. Go to Linear Settings → Integrations
2. Connect GitHub repository
3. Configure sync rules
4. Enable automatic linking

## Linking Issues to Code

### In Commit Messages

```bash
git commit -m "feat(api): add authentication endpoint [AURA-123]"
```

### In PR Descriptions

```markdown
Closes AURA-123
```

### In Code Comments

```python
# TODO: Refactor this after AURA-456
# See AURA-789 for context
```

### Branch Naming

Use Linear issue IDs in branch names:

```bash
feature/AURA-123-implement-feature
fix/AURA-456-login-bug
refactor/AURA-789-api-structure
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

## Projects

Create Linear projects for:

- **Epics**: Large features spanning multiple issues
- **Sprints**: Time-boxed development cycles
- **Releases**: Version releases

## Commands Reference

### View Issue

```bash
# In Cursor, use Linear MCP tools
# Or use Linear CLI if installed
linear issue view AURA-123
```

### Update Issue Status

```bash
# Move to In Progress
linear issue update AURA-123 --state "In Progress"

# Move to In Review
linear issue update AURA-123 --state "In Review"

# Move to Done
linear issue update AURA-123 --state "Done"
```

### Create Comment

```bash
# Add comment to issue
linear issue comment AURA-123 "Working on this now"
```

## Workflow Examples

### Complete Workflow

```bash
# 1. Create Linear issue (manually in Linear or using template)
# Issue ID: AURA-123

# 2. Create branch linked to issue
just branch-linear AURA-123 "implement authentication"

# 3. Make changes and commit
git add .
git commit -m "feat(auth): add JWT authentication [AURA-123]"

# 4. Push branch
git push origin feature/AURA-123-implement-authentication

# 5. Create PR linked to issue
just pr-linear "Implement JWT Authentication" "Adds JWT-based authentication system" AURA-123
```

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

6. **Always link branches to Linear issues** - Use `branch-linear` instead of `branch-create`
7. **Include issue ID in commit messages** - Format: `feat(scope): description [AURA-123]`
8. **Use PR template** - The template includes a section for Linear issue linking
9. **Set priority when creating issues** - Don't leave everything as Normal
10. **Update priority as context changes** - Priorities can change over time
11. **Assign issues when starting work** - Helps track who's working on what
12. **Review priorities regularly** - Ensure they reflect current project needs
13. **Use High sparingly** - Reserve for truly important work

## Troubleshooting

### Issue Not Found

- Check issue ID format (AURA-123)
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

## Related Documentation

- [Development Guide](DEVELOPMENT.md) - Development workflow and pipeline
- [Architecture Guide](ARCHITECTURE.md) - System architecture overview
