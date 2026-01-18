# Production Deployment Guide

## Prerequisites

1. **Kubernetes Cluster**: Production-ready cluster (EKS, GKE, AKS, or self-hosted)
2. **kubectl**: Configured to access your cluster
3. **kustomize**: For building manifests
4. **Docker Images**: Pushed to container registry (GHCR)
5. **Domain Names**: Configured DNS for your domains
6. **TLS Certificates**: cert-manager installed (for automatic TLS)

## Pre-Deployment Checklist

- [ ] Kubernetes cluster is running and accessible
- [ ] Docker images are built and pushed to registry
- [ ] Secrets are created (database URI, etc.)
- [ ] DNS records point to your cluster
- [ ] Ingress controller is installed
- [ ] cert-manager is installed (for TLS)
- [ ] Resource quotas are appropriate for your cluster
- [ ] Backup strategy is configured

## Step 1: Install Prerequisites

### Install Nginx Ingress Controller

```bash
cd k8s/scripts
./setup-ingress.sh
```

### Install cert-manager

```bash
./setup-cert-manager.sh
```

### Configure cert-manager ClusterIssuer

1. Edit `k8s/overlays/production/cert-manager-issuer.yaml`
2. Update the email address
3. Apply:
   ```bash
   kubectl apply -f k8s/overlays/production/cert-manager-issuer.yaml
   ```

## Step 2: Create Secrets

**Never commit secrets to Git!**

```bash
# Create backend secrets
kubectl create secret generic backend-secrets \
  --from-literal=postgres-db-uri='postgresql://user:password@postgres:5432/aura' \
  -n aura-production

# Create postgres secrets
kubectl create secret generic postgres-secrets \
  --from-literal=postgres-user='aura' \
  --from-literal=postgres-password='your-secure-password' \
  --from-literal=postgres-db='aura' \
  -n aura-production
```

**For GitOps workflows**, use Sealed Secrets (see `docs/workflows/production-secrets.md`).

## Step 3: Update Configuration

### Update Domain Names

Edit `k8s/overlays/production/ingress.yaml`:

```yaml
spec:
  rules:
    - host: api.yourdomain.com # Change this
    - host: app.yourdomain.com # Change this
```

Edit `k8s/overlays/production/kustomization.yaml`:

```yaml
configMapGenerator:
  - name: web-dashboard-config
    literals:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com # Change this
```

### Update Image Tags

Edit `k8s/overlays/production/kustomization.yaml`:

```yaml
images:
  - name: aura-backend
    newName: ghcr.io/your-org/aura-backend
    newTag: v1.0.0 # Use specific version tags
```

## Step 4: Deploy

### Build and Push Images

```bash
# Build production images
just k8s-build-prod

# Push to registry
just k8s-push-images
```

### Deploy to Kubernetes

```bash
# Preview what will be deployed
kubectl kustomize k8s/overlays/production

# Deploy
kubectl apply -k k8s/overlays/production

# Or use the deploy script
./k8s/scripts/deploy.sh production
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n aura-production

# Check services
kubectl get svc -n aura-production

# Check ingress
kubectl get ingress -n aura-production

# Check HPA
kubectl get hpa -n aura-production

# View logs
kubectl logs -n aura-production deployment/backend
```

## Step 5: Configure DNS

1. Get the external IP of your ingress controller:

   ```bash
   kubectl get svc -n ingress-nginx ingress-nginx-controller
   ```

2. Create DNS A records:
   - `api.yourdomain.com` → Ingress IP
   - `app.yourdomain.com` → Ingress IP

3. Wait for DNS propagation (can take a few minutes)

4. Verify TLS certificates:
   ```bash
   kubectl get certificate -n aura-production
   kubectl describe certificate aura-tls -n aura-production
   ```

## Step 6: Post-Deployment Verification

### Health Checks

```bash
# Check backend health
curl https://api.yourdomain.com/health

# Check web dashboard
curl https://app.yourdomain.com
```

### Monitor Resources

```bash
# Watch pods
kubectl get pods -n aura-production -w

# Check resource usage
kubectl top pods -n aura-production

# Check HPA status
kubectl describe hpa backend-hpa -n aura-production
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment backend -n aura-production --replicas=5
```

### Auto-Scaling

HPA is already configured. It will automatically scale based on CPU/memory usage.

View HPA status:

```bash
kubectl get hpa -n aura-production
kubectl describe hpa backend-hpa -n aura-production
```

## Updates and Rollouts

### Rolling Update

```bash
# Update image tag in kustomization.yaml
kubectl apply -k k8s/overlays/production

# Monitor rollout
kubectl rollout status deployment/backend -n aura-production
```

### Rollback

```bash
# View rollout history
kubectl rollout history deployment/backend -n aura-production

# Rollback to previous version
kubectl rollout undo deployment/backend -n aura-production
```

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -n aura-production deployment/backend -f

# Web dashboard logs
kubectl logs -n aura-production deployment/web-dashboard -f

# All pods
kubectl logs -n aura-production --all-containers=true -f
```

### Resource Monitoring

```bash
# Pod resource usage
kubectl top pods -n aura-production

# Node resource usage
kubectl top nodes
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n aura-production

# Check events
kubectl get events -n aura-production --sort-by='.lastTimestamp'
```

### Ingress Not Working

```bash
# Check ingress
kubectl describe ingress aura-ingress -n aura-production

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### TLS Certificate Issues

```bash
# Check certificate status
kubectl describe certificate aura-tls -n aura-production

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

### Database Connection Issues

```bash
# Check postgres pod
kubectl logs -n aura-production statefulset/postgres

# Test connection
kubectl exec -it -n aura-production statefulset/postgres -- psql -U aura -d aura
```

## Backup and Recovery

### Database Backups

Backup CronJob is configured in `k8s/overlays/production/postgres-backup.yaml`.

To run a manual backup:

```bash
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%s) -n aura-production
```

### Restore from Backup

```bash
# Copy backup to postgres pod
kubectl cp backup.sql.gz aura-production/postgres-0:/tmp/

# Restore
kubectl exec -it -n aura-production postgres-0 -- \
  gunzip -c /tmp/backup.sql.gz | psql -U aura -d aura
```

## Security Best Practices

1. **Network Policies**: Already configured to isolate services
2. **RBAC**: Service accounts with minimal permissions
3. **Pod Security**: Restricted security standards enforced
4. **Secrets**: Never commit to Git, use sealed secrets or external secrets
5. **TLS**: All traffic encrypted via cert-manager
6. **Resource Limits**: Configured to prevent resource exhaustion

## Production Considerations

### High Availability

- Multiple replicas (3+) for backend and web dashboard
- PodDisruptionBudgets ensure availability during updates
- Anti-affinity rules spread pods across nodes

### Performance

- HPA automatically scales based on load
- Resource requests/limits prevent resource contention
- Health checks ensure only healthy pods receive traffic

### Reliability

- Liveness probes restart unhealthy pods
- Readiness probes prevent traffic to starting pods
- Startup probes give apps time to initialize

## Next Steps

1. Set up monitoring (Prometheus + Grafana)
2. Configure alerting
3. Set up log aggregation (Loki)
4. Configure backup storage (S3, etc.)
5. Set up CI/CD for automated deployments
6. Configure disaster recovery procedures
