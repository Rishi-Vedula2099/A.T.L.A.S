# A.T.L.A.S — Kubernetes Manifests

Plain Kubernetes manifests mirroring the Docker Compose stack. Apply with
`kubectl` directly, or use the [Helm chart](../helm/atlas/) for parameterized
deploys. The two are kept in sync — pick whichever fits your workflow.

## Layout

Files are numbered for apply order (numeric sort):

| File                              | Kind                | Notes                                          |
|-----------------------------------|---------------------|------------------------------------------------|
| `00-namespace.yaml`               | Namespace           | `atlas` with baseline pod-security labels      |
| `01-configmaps.yaml`              | ConfigMap           | Non-secret config + DB init placeholders       |
| `02-secrets.yaml`                 | Secret              | **Provision real values yourself**             |
| `03-persistentvolumes.yaml`       | PVC                 | 20–50 Gi per datastore                         |
| `10-postgres-statefulset.yaml`    | StatefulSet         | Postgres 16, pg_isready probes                 |
| `11-redis-statefulset.yaml`       | StatefulSet         | Redis 7, AOF on                                |
| `12-neo4j-statefulset.yaml`       | StatefulSet         | Neo4j 5 community + APOC                       |
| `13-qdrant-statefulset.yaml`      | StatefulSet         | Qdrant with readyz/livez probes                |
| `14-minio-statefulset.yaml`       | StatefulSet         | MinIO for backups                              |
| `20-backend-deployment.yaml`      | Deployment (×3)     | Atlas backend, readyz/liveness/startup probes  |
| `21-frontend-deployment.yaml`     | Deployment (×2)     | Next.js, read-only root FS                     |
| `30-services.yaml`                | Services            | ClusterIPs for everything                      |
| `40-ingress.yaml`                 | Ingress             | nginx + cert-manager TLS                       |
| `50-hpa.yaml`                     | HPA                 | CPU/memory autoscaling                         |
| `51-pdb.yaml`                     | PDB                 | Voluntary disruption guard                     |
| `60-networkpolicies.yaml`         | NetworkPolicy       | Default-deny + 5-network segmentation          |

`deployment.legacy.yaml` is the original Phase-1 stub, kept for reference.

## Quick start

```bash
# 1. Create namespace + non-secret config
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmaps.yaml
kubectl apply -f 03-persistentvolumes.yaml

# 2. Provision secrets (CHOOSE ONE METHOD):
#    a) Direct creation from .env values
kubectl create secret generic atlas-db-secret --namespace=atlas \
    --from-literal=postgres-password='...' \
    --from-literal=neo4j-password='...' \
    --from-literal=redis-password='...' \
    --from-literal=jwt-secret='...' \
    --from-literal=jwt-refresh-secret='...' \
    --from-literal=atlas-api-key='...' \
    --from-literal=minio-access-key='...' \
    --from-literal=minio-secret-key='...' \
    --from-literal=atlas-backup-key='...' \
    --from-literal=bootstrap-admin-password='...'
#    b) Sealed Secrets / External Secrets Operator (recommended — see docs/security.md)

# 3. PVCs + databases (stateful — bring up first and wait for readiness)
kubectl apply -f 10-postgres-statefulset.yaml \
              -f 11-redis-statefulset.yaml \
              -f 12-neo4j-statefulset.yaml \
              -f 13-qdrant-statefulset.yaml \
              -f 14-minio-statefulset.yaml
kubectl wait --namespace=atlas --for=condition=Ready pod -l app.kubernetes.io/component=database --timeout=300s

# 4. Services, app, ingress, autoscaling
kubectl apply -f 30-services.yaml \
              -f 20-backend-deployment.yaml \
              -f 21-frontend-deployment.yaml \
              -f 40-ingress.yaml \
              -f 50-hpa.yaml \
              -f 51-pdb.yaml \
              -f 60-networkpolicies.yaml
kubectl rollout status deployment/atlas-backend --namespace=atlas
```

## Notes

- **Storage classes**: PVCs use `storageClassName: standard`. Override per
  cloud (gp3 / premium-rwo / standard-rwo) via kustomize patches.
- **Database init**: real schema files live in
  [`infrastructure/init/`](../init/). For k8s, bake them into a custom image
  or mount as a projected volume on the StatefulSet `init` path.
- **Ingress**: the example assumes nginx-ingress + cert-manager. For Traefik,
  swap the `Ingress` annotations or use `IngressRoute`.
- **GPU**: see [docs/operations.md](../../docs/operations.md#4-gpu-enablement).
  Add `nvidia.com/gpu` resource requests and node selectors on the backend
  Deployment.
- **Images**: pinned to `ghcr.io/atlas/atlas-backend:latest` and
  `ghcr.io/atlas/atlas-frontend:latest`. Override per environment with
  `kubectl set image`.
