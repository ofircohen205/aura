# GitHub Secrets Configuration Guide

This document lists all GitHub secrets required for CI/CD workflows in this repository.

## Required Secrets

### 1. Kubernetes Deployment Secrets

These secrets contain base64-encoded kubeconfig files for accessing your Kubernetes clusters.

#### `KUBECONFIG_DEV`

- **Purpose**: Kubernetes cluster access for development environment
- **Used by**: `k8s-deploy-dev.yml` workflow
- **Format**: Base64-encoded kubeconfig file
- **How to create**:

  ```bash
  # Get your kubeconfig and encode it
  cat ~/.kube/config | base64 | pbcopy  # macOS
  # Or for Linux:
  cat ~/.kube/config | base64

  # Then set it in GitHub:
  gh secret set KUBECONFIG_DEV
  # Paste the base64 string when prompted
  ```

#### `KUBECONFIG_STAGING`

- **Purpose**: Kubernetes cluster access for staging environment
- **Used by**: `k8s-deploy-staging.yml` workflow
- **Format**: Base64-encoded kubeconfig file
- **How to create**: Same as above, but for your staging cluster
  ```bash
  # Switch to staging cluster context first
  kubectl config use-context <staging-context>
  cat ~/.kube/config | base64 | pbcopy
  gh secret set KUBECONFIG_STAGING
  ```

#### `KUBECONFIG_PRODUCTION`

- **Purpose**: Kubernetes cluster access for production environment
- **Used by**: `k8s-deploy-prod.yml` workflow
- **Format**: Base64-encoded kubeconfig file
- **How to create**: Same as above, but for your production cluster
  ```bash
  # Switch to production cluster context first
  kubectl config use-context <production-context>
  cat ~/.kube/config | base64 | pbcopy
  gh secret set KUBECONFIG_PRODUCTION
  ```

**Important Notes:**

- Each kubeconfig should have at least one context defined
- The kubeconfig must be valid YAML/JSON format
- Ensure the service account/user in the kubeconfig has necessary permissions
- For production, use a dedicated service account with least privilege

### 2. Vercel Deployment Secrets

These secrets are required for deploying the web dashboard to Vercel.

#### `VERCEL_TOKEN`

- **Purpose**: Authentication token for Vercel API
- **Used by**: `web-dashboard-vercel.yml` workflow
- **How to get**:
  1. Go to [Vercel Settings → Tokens](https://vercel.com/account/tokens)
  2. Click "Create Token"
  3. Give it a name (e.g., "GitHub Actions")
  4. Set expiration (recommended: no expiration for CI/CD)
  5. Copy the token
- **How to set**:
  ```bash
  gh secret set VERCEL_TOKEN
  # Paste the token when prompted
  ```

#### `VERCEL_ORG_ID`

- **Purpose**: Your Vercel organization/team ID
- **Used by**: `web-dashboard-vercel.yml` workflow
- **How to get**:
  1. Go to your Vercel project settings
  2. The Org ID is in the URL or in project settings
  3. Or run: `vercel whoami` and check your account
  4. Or use Vercel API: `curl https://api.vercel.com/v2/teams -H "Authorization: Bearer $VERCEL_TOKEN"`
- **How to set**:
  ```bash
  gh secret set VERCEL_ORG_ID
  # Paste the organization ID when prompted
  ```

#### `VERCEL_PROJECT_ID`

- **Purpose**: Your Vercel project ID
- **Used by**: `web-dashboard-vercel.yml` workflow
- **How to get**:
  1. Go to your Vercel project settings
  2. The Project ID is visible in the project settings page
  3. Or run: `vercel link` in your project directory and check `.vercel/project.json`
- **How to set**:
  ```bash
  gh secret set VERCEL_PROJECT_ID
  # Paste the project ID when prompted
  ```

## Automatically Provided Secrets

These are automatically provided by GitHub Actions and don't need to be set manually:

- **`GITHUB_TOKEN`**: Automatically provided for each workflow run
  - Has permissions to push to GitHub Container Registry (GHCR)
  - Used for Docker image builds and pushes
  - No action required

## Optional/Future Secrets

These secrets are mentioned in the codebase but not currently required:

### `VSCE_PAT` (Future)

- **Purpose**: Personal Access Token for VS Code Marketplace publishing
- **Status**: Not currently used
- **When needed**: When publishing VS Code extension to marketplace

### `PYPI_API_TOKEN` (Future)

- **Purpose**: API token for PyPI package publishing
- **Status**: Not currently used
- **When needed**: When publishing Python packages to PyPI

## Setting Secrets via GitHub Web UI

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

## Setting Secrets via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# macOS: brew install gh
# Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Authenticate
gh auth login

# Set secrets (will prompt for value)
gh secret set KUBECONFIG_DEV
gh secret set KUBECONFIG_STAGING
gh secret set KUBECONFIG_PRODUCTION
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID

# Or set from file/command output
cat ~/.kube/config | base64 | gh secret set KUBECONFIG_DEV
echo "your-vercel-token" | gh secret set VERCEL_TOKEN
```

## Setting Secrets via GitHub API

```bash
# Using curl (requires a GitHub Personal Access Token with repo scope)
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/secrets/KUBECONFIG_DEV \
  -d '{"encrypted_value":"ENCRYPTED_VALUE","key_id":"KEY_ID"}'
```

Note: The API method requires encryption using GitHub's public key. The CLI method is simpler.

## Verifying Secrets

To verify your secrets are set correctly:

```bash
# List all secrets (names only, not values)
gh secret list

# Check if a specific secret exists
gh secret list | grep KUBECONFIG_DEV
```

## Security Best Practices

1. **Rotate secrets regularly**: Especially for production credentials
2. **Use least privilege**: Grant only necessary permissions to service accounts
3. **Audit access**: Regularly review who has access to secrets
4. **Use separate secrets per environment**: Don't reuse dev secrets for production
5. **Monitor usage**: Check GitHub Actions logs for secret access
6. **Use OIDC where possible**: Prefer workload identity over static tokens (future improvement)

## Troubleshooting

### "No context found in kubeconfig"

- Ensure your kubeconfig file has at least one context defined
- Verify the base64 encoding is correct
- Check that the secret value is not empty

### "Invalid kubeconfig format"

- Verify the kubeconfig is valid YAML/JSON
- Test locally: `kubectl config view`
- Ensure the file was properly base64 encoded

### "Secret is not set"

- Verify the secret name matches exactly (case-sensitive)
- Check that the secret was added to the correct repository
- Ensure you're checking the right environment (if using GitHub Environments)

## Summary Checklist

- [ ] `KUBECONFIG_DEV` - Base64-encoded kubeconfig for dev cluster
- [ ] `KUBECONFIG_STAGING` - Base64-encoded kubeconfig for staging cluster
- [ ] `KUBECONFIG_PRODUCTION` - Base64-encoded kubeconfig for production cluster
- [ ] `VERCEL_TOKEN` - Vercel API authentication token
- [ ] `VERCEL_ORG_ID` - Vercel organization/team ID
- [ ] `VERCEL_PROJECT_ID` - Vercel project ID

Total: **6 required secrets**
