# Story: Manage Deployments for Knowledge Dashboard and GitHub App

**Role:** DevOps Engineer
**Related SRS Section:** 4.3

## Desired Feature

The Knowledge Dashboard (Next.js) and the GitHub Architect App (Probot) need to be deployed to a production-ready environment (Vercel and/or AWS).

## Planning & Technical Spec

### Architecture

- **Web**: Vercel (easiest for Next.js).
- **GitHub App**: Vercel (Serverless functions) or AWS Lambda (if long-running tasks needed, though SRS mentions Redis for rate limits, suggesting stateful/worker needs).
- **Environment Management**: Separation of `staging` and `production`.

### Standards & Workflows

- **Git Flow**: Create a new branch for this story and work only on that branch.

### Implementation Checklist

- [ ] Connect GitHub Repo to Vercel.
- [ ] Configure Environment Variables (`AURA_API_KEY`, `GITHUB_APP_PEM`).
- [ ] Setup Domain DNS (if applicable).
- [ ] monitor logs/usage via Vercel Dashboard.

## Testing Plan

- **Manual Verification**:
  - [ ] Deploy to Staging.
  - [ ] Verify Dashboard loads.
  - [ ] Verify GitHub App responds to a webhook event.
