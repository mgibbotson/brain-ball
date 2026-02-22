# Quickstart: Brain Ball Backend (Local)

**Date**: 2025-02-21  
**Goal**: Spin up the entire backend on a developer’s machine so all services report healthy (spec SC-001). Client runs on the same LAN and calls the backend REST API.

## Prerequisites

- **Docker** and **Docker Compose** (for the “one command” backend run).
- **Go 1.21+** and **Python 3.11+** (if building/running services locally without Docker).
- **Optional**: **Kubernetes** (kind or minikube) and **kubectl** for K8s-based run and Kubeflow ML ops.

## Option A: Docker Compose (fastest)

**Validation**: Run this flow end-to-end (start backend, curl `/health`, `/ready`, `POST /v1/text-to-animal`, then run client with `BRAIN_BALL_API_URL`) and fix any gaps before release.

1. From repo root, start the backend (one command):
   ```bash
   make backend-up
   ```
   Or manually:
   ```bash
   docker compose -f infra/docker-compose.yaml up -d
   ```
2. Wait until all services are healthy (API `/ready` returns 200 when word2animal is up). Docker Compose waits for word2animal health before starting the API.
3. Verify:
   ```bash
   curl -s http://localhost:8080/health
   curl -s http://localhost:8080/ready
   ```
   **Ready check**: `/ready` returns 503 until word2animal gRPC is reachable, then 200 when both are up. If you see 503, wait a few seconds and retry.
   ```bash
   curl -s -X POST http://localhost:8080/v1/text-to-animal -H "Content-Type: application/json" -d '{"text":"beak"}'
   ```
   Expected: `{"animal":"bird"}` (or equivalent). Round-trip should be ≤ 2s (SC-002); to verify, run `time curl -s -X POST http://localhost:8080/v1/text-to-animal -H "Content-Type: application/json" -d '{"text":"beak"}'` and confirm elapsed time &lt; 2s.

4. **Client**: Configure the on-device client with backend base URL `http://<host-ip>:8080` (replace `<host-ip>` with the machine’s LAN IP). Run the client on a device on the same LAN.

**Stop**:
```bash
make backend-down
```
Or: `docker compose -f infra/docker-compose.yaml down`

## Option B: Kubernetes (kind/minikube)

1. Create cluster (example with kind):
   ```bash
   kind create cluster --name brain-ball
   kubectl config use-context kind-brain-ball
   ```
2. Build and load images (if using local images):
   ```bash
   # Build API and word2animal images, then load into kind
   make build-images
   kind load docker-image brainball/api:latest brainball/word2animal:latest --name brain-ball
   ```
3. Apply manifests:
   ```bash
   kubectl apply -f infra/k8s/
   ```
4. Wait for deployments to be ready:
   ```bash
   kubectl wait --for=condition=ready pod -l app=api -n default --timeout=300s
   kubectl wait --for=condition=ready pod -l app=word2animal -n default --timeout=300s
   ```
5. Port-forward or use Ingress to reach API (e.g. `kubectl port-forward svc/api 8080:8080`).
6. Verify `/health`, `/ready`, and `POST /v1/text-to-animal` as in Option A.

**Kubeflow (ML ops)**: Install Kubeflow in the cluster for training pipelines and model versioning. Use Kubeflow Pipelines to produce model artifacts; configure word2animal service to load the artifact path/version via config (see plan.md and research.md).

## Same-LAN setup (client and backend on local network)

Core flows work on the same LAN without internet (SC-004):

1. **Backend**: Run the backend on one machine (e.g. `make backend-up` from repo root). Note the machine’s LAN IP (e.g. `192.168.1.100` on macOS: `ipconfig getifaddr en0`; on Linux: `hostname -I` or `ip addr`).
2. **Client**: On another device on the same LAN, set the backend base URL to the host IP and API port:
   ```bash
   export BRAIN_BALL_API_URL=http://<host-ip>:8080
   ```
   Example: `BRAIN_BALL_API_URL=http://192.168.1.100:8080`
3. Run the client on that device. All API calls use this configurable URL (no hardcoded localhost in production path).
4. Ensure firewall allows TCP port 8080 to the backend host.

## Client configuration

- Set backend base URL (e.g. environment variable `BRAIN_BALL_API_URL=http://192.168.1.100:8080` or config file).
- When backend is unreachable: client shows a clear error and a random animal (spec FR-011).

## First release scope

- **In scope**: API (Go) + word2animal (Python); REST `/v1/text-to-animal`; local run via Docker Compose or K8s.
- **Later release**: person-recognition service; REST `/v1/person-recognition`; Kubeflow pipelines for model training.

## Resource usage and timing (constitution)

- **Round-trip latency**: Text-to-animal (client → API → word2animal → API → client) target ≤ 2 s under normal LAN (SC-002). Verify with `time curl ...` or the quickstart verification step.
- **Backend start**: All services healthy within &lt; 5 minutes from start (SC-001). Docker Compose typically ready in under a minute.
- **Expected resource usage (guidance)**: API (Go): modest memory (~50–100 MB), low CPU when idle. word2animal (Python): depends on model; stub/small model ~100–200 MB RAM; scale for concurrent requests as needed.

## Troubleshooting

- **API `/ready` returns 503**: One or more downstream gRPC services (word2animal) are not ready. Check service logs and health.
- **Client cannot reach API**: Ensure client and backend are on the same LAN and firewall allows port 8080 (or chosen port).
- **Text-to-animal &gt; 2s**: Check LAN latency and word2animal model load/inference time; optimize or scale as needed.
