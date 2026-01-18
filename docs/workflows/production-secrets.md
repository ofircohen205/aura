# Production Secrets Management

## Overview

This document describes how to manage secrets in production Kubernetes environments for Aura.

## Options

### 1. Sealed Secrets (Recommended for GitOps)

**What**: Encrypt secrets so they can be safely stored in Git.

**Installation:**

```bash
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

**Usage:**

```bash
# Install kubeseal CLI
brew install kubeseal  # macOS
# or download from: https://github.com/bitnami-labs/sealed-secrets/releases

# Create a sealed secret
kubectl create secret generic backend-secrets \
  --from-literal=postgres-db-uri='postgresql://...' \
  --dry-run=client -o yaml | kubeseal -o yaml > sealed-secret.yaml

# Apply the sealed secret
kubectl apply -f sealed-secret.yaml
```

**Pros:**

- Secrets can be stored in Git (encrypted)
- Works well with GitOps workflows
- No external dependencies

**Cons:**

- Requires kubeseal CLI
- Secrets are encrypted but still visible in Git

### 2. External Secrets Operator

**What**: Sync secrets from external secret stores (AWS Secrets Manager, HashiCorp Vault, etc.)

**Installation:**

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace
```

**Usage:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: backend-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: backend-secrets
  data:
    - secretKey: postgres-db-uri
      remoteRef:
        key: aura/production/postgres
        property: db-uri
```

**Pros:**

- Centralized secret management
- Integrates with cloud providers
- Automatic rotation support

**Cons:**

- Requires external secret store
- More complex setup

### 3. Cloud-Native Solutions

**AWS:**

- AWS Secrets Manager
- AWS Parameter Store
- Use External Secrets Operator

**GCP:**

- Secret Manager
- Use External Secrets Operator

**Azure:**

- Key Vault
- Use External Secrets Operator

## Current Implementation

Currently, Aura uses Kubernetes Secrets directly. For production:

1. **Never commit secrets to Git**
2. **Use kubectl to create secrets:**
   ```bash
   kubectl create secret generic backend-secrets \
     --from-literal=postgres-db-uri='postgresql://user:pass@host/db' \
     -n aura-production
   ```
3. **Or use sealed secrets for GitOps workflows**

## Migration Path

1. **Development**: Continue using kubectl secrets (local only)
2. **Staging**: Use sealed secrets for GitOps
3. **Production**: Use External Secrets Operator with cloud secret store

## Best Practices

1. **Rotate secrets regularly**
2. **Use different secrets per environment**
3. **Limit access to secrets (RBAC)**
4. **Audit secret access**
5. **Never log secrets**
6. **Use secret scanning in CI/CD**

## Example: Setting Up Sealed Secrets

```bash
# 1. Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# 2. Get the public key (for encryption)
kubeseal --fetch-cert > sealed-secrets-public-key.pem

# 3. Create a sealed secret
kubectl create secret generic backend-secrets \
  --from-literal=postgres-db-uri='postgresql://...' \
  --dry-run=client -o yaml | \
  kubeseal --cert=sealed-secrets-public-key.pem -o yaml > k8s/overlays/production/sealed-secret-backend.yaml

# 4. Commit the sealed secret to Git
git add k8s/overlays/production/sealed-secret-backend.yaml
git commit -m "Add sealed secret for backend"
```

## Security Considerations

- Secrets are base64 encoded (not encrypted) in Kubernetes
- Use RBAC to limit who can read secrets
- Enable encryption at rest for etcd
- Use network policies to limit pod-to-pod communication
- Regularly rotate secrets
- Monitor secret access
