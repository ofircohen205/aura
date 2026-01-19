# Required Repository Secrets

This document lists all secrets required for the CI/CD workflows to function properly.

## Core Secrets

### Docker Registry (GitHub Container Registry)

| Secret         | Description                              | Required For                      |
| -------------- | ---------------------------------------- | --------------------------------- |
| `GITHUB_TOKEN` | Automatically provided by GitHub Actions | Docker builds, package publishing |

### PyPI Publishing (CLI) - Future

> **Note:** CLI packages are currently published to GitHub Releases. PyPI publishing will be enabled in the future.

| Secret           | Description                           | Required For               |
| ---------------- | ------------------------------------- | -------------------------- |
| `PYPI_API_TOKEN` | PyPI API token for `aura-cli` package | `cli-release.yml` (future) |

We recommend using [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/) instead of API tokens for enhanced security when enabling PyPI.

### VS Code Marketplace

| Secret     | Description                                   | Required For                  |
| ---------- | --------------------------------------------- | ----------------------------- |
| `VSCE_PAT` | Personal Access Token for VS Code Marketplace | Extension publishing (future) |

### Vercel Deployment

| Secret              | Description                         | Required For               |
| ------------------- | ----------------------------------- | -------------------------- |
| `VERCEL_TOKEN`      | Vercel authentication token         | `web-dashboard-vercel.yml` |
| `VERCEL_ORG_ID`     | Vercel organization ID              | `web-dashboard-vercel.yml` |
| `VERCEL_PROJECT_ID` | Vercel project ID for web-dashboard | `web-dashboard-vercel.yml` |

### Kubernetes Deployments

| Secret                  | Description                                      | Required For             |
| ----------------------- | ------------------------------------------------ | ------------------------ |
| `KUBECONFIG_DEV`        | Base64-encoded kubeconfig for dev cluster        | `k8s-deploy-dev.yml`     |
| `KUBECONFIG_STAGING`    | Base64-encoded kubeconfig for staging cluster    | `k8s-deploy-staging.yml` |
| `KUBECONFIG_PRODUCTION` | Base64-encoded kubeconfig for production cluster | `k8s-deploy-prod.yml`    |

## Setting Up Secrets

### Via GitHub UI

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its name and value

### Via GitHub CLI

```bash
# Example: Set PyPI token
gh secret set PYPI_API_TOKEN --body "pypi-xxxxx"

# Example: Set Vercel token
gh secret set VERCEL_TOKEN --body "xxxxx"

# Example: Set kubeconfig (base64 encoded)
cat ~/.kube/config | base64 | gh secret set KUBECONFIG_DEV
```

## Environment Protection

For production deployments, we recommend creating [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) with required reviewers:

- **preview**: No protection required
- **pypi**: Requires manual approval
- **production**: Requires manual approval from at least 2 reviewers

## Security Best Practices

1. **Rotate secrets regularly** - Update tokens and credentials periodically
2. **Use least privilege** - Grant only necessary permissions to each token
3. **Audit access** - Regularly review who has access to secrets
4. **Use OIDC where possible** - Prefer workload identity over static tokens (e.g., PyPI Trusted Publishers, AWS OIDC)
