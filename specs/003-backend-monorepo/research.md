# Research: Brain Ball Backend Monorepo

**Date**: 2025-02-21  
**Phase**: Implementation plan (gRPC microservices, REST client–backend, Kubeflow ML ops)

## API Style: Client ↔ Backend vs Backend Internal

### Client ↔ Backend: REST
- **Decision**: REST over HTTP with JSON between the on-device client and the backend API.
- **Rationale**: Client is Python on device/Raspberry Pi; REST is easy to consume (requests/urllib), debuggable (curl, browser), and matches spec FR-002 (REST API). No need for bidirectional streaming or codegen on the client for first release.
- **Alternatives considered**:
  - gRPC from client: would require proto codegen and gRPC runtime on device; more complexity and larger footprint.
  - GraphQL: overkill for two primary operations (text-to-animal, later person recognition).

### Backend Internal: gRPC
- **Decision**: gRPC between the API gateway and microservices (word2animal, person-recognition).
- **Rationale**: Strong typing, codegen, efficient binary protocol, and good fit for service-to-service calls. Aligns with “microservices” and keeps REST only at the edge.
- **Alternatives considered**:
  - REST between API and services: possible but duplicate HTTP handling and less clear contracts.
  - Message queue (e.g. RabbitMQ): adds operational complexity; request/response pattern fits RPC for first release.

## ML Ops: Kubeflow

- **Decision**: Use Kubeflow for ML ops (training pipelines, model versioning/artifacts, experimentation).
- **Rationale**: Spec requires “kubernetes and ML ops practices” and “model updates and versioning without changing application code” (FR-008, SC-006). Kubeflow provides Pipelines, Training jobs, and artifact storage (e.g. MinIO or PVC) so models can be versioned and served by loading the chosen artifact in the Python services.
- **Alternatives considered**:
  - Custom scripts only: no standard pipeline or versioning story.
  - MLflow only: good for tracking/registry but less K8s-native than Kubeflow for this stack.
  - Kubeflow + in-process serving: chosen so Python services load the model artifact (path/version from config); no separate inference server required for first release.

## Local Backend Run

- **Decision**: Support both Docker Compose and Kubernetes (e.g. kind/minikube) for “spin up locally.” Docker Compose for fastest “one command” dev; K8s manifests for parity with production-like and Kubeflow.
- **Rationale**: Spec FR-006 and SC-001 require backend startable locally with documented, repeatable process. Docker Compose is the simplest single-command story; K8s + Kubeflow satisfy “kubernetes and ML ops practices.”
- **Alternatives considered**:
  - Kubernetes only: higher friction for some developers.
  - Docker Compose only: less alignment with “Kubernetes and ML ops” for pipelines/training.

## Language and Runtime Choices

### API: Go
- **Decision**: Implement the backend API gateway in Go.
- **Rationale**: User-specified; good fit for a thin gateway (HTTP + gRPC client), single binary, low footprint.
- **Alternatives considered**: Python (would match services but user asked for Go for API).

### Microservices: Python
- **Decision**: word2animal and person-recognition in Python.
- **Rationale**: User-specified; Python is standard for ML inference and model loading; aligns with existing client and Kubeflow/Python ecosystem.
- **Alternatives considered**: Go for inference (possible via ONNX or CGO but less common for ML workloads).

## Health and Readiness

- **Decision**: Every backend component (API, word2animal, person-recognition) exposes health and readiness (e.g. `/health`, `/ready` or gRPC health protocol). API’s readiness depends on downstream gRPC services being ready.
- **Rationale**: Spec FR-007, SC-005; required for “all services up” verification and K8s liveness/readiness probes.
- **Alternatives considered**: Health only (no readiness): insufficient for “traffic only when ready.”

## First Release Scope

- **Decision**: First shippable release = text-to-animal via REST + local backend (API + word2animal). Person recognition and its gRPC service are implemented in the monorepo but not required for “first release” (per spec clarification).
- **Rationale**: Spec clarification: “Can follow in a later release”; crawl = text-to-animal + backend, walk = person recognition.
- **Alternatives considered**: Shipping person recognition in first release: would expand scope and delay core flow.
