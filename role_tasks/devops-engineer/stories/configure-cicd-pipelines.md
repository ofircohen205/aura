# Story: Configure CI/CD Pipelines

**Role:** DevOps Engineer
**Related SRS Section:** 4.3

## Desired Feature

We have 4 distinct artifacts (Extension, CLI, Probot App, Dashboard) that need automated testing and deployment pipelines. The goal is to ensure that a push to `main` safely deploys all components.

## Planning & Technical Spec

### Architecture

- **Platform**: GitHub Actions.
- **Workflow Strategy**: Monorepo-style or multiple workflows based on path filters.
- **Artifacts**:
  - `vscode-extension`: Publish to VSCode Marketplace (or build .vsix).
  - `cli`: Publish to PyPI (internal/public).
  - `backend`: Docker build -> Registry (ECR/GHCR).
  - `web`: Vercel Deployment.

### Implementation Checklist

- [ ] Create `.github/workflows/ci-backend.yml`: Lint, Test (Pytest).
- [ ] Create `.github/workflows/ci-extension.yml`: Compile, Test (Headless).
- [ ] Create `.github/workflows/ci-web.yml`: Build Next.js.
- [ ] Set up Secrets in GitHub Repo settings.

## Testing Plan

- **Manual Verification**:
  - [ ] Trigger a build by pushing a dummy change to each directory.
  - [ ] Verify Green checkmarks on the PR.
