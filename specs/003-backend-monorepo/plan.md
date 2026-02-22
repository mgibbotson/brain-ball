# Implementation Plan: Brain Ball Backend Monorepo

**Branch**: `003-backend-monorepo` | **Date**: 2025-02-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-backend-monorepo/spec.md`

## Summary

Transform the repository into a monorepo with a REST API (client–backend) and gRPC between backend microservices. The on-device client (Python, existing) keeps speech-to-text on-device and calls the backend REST API for text-to-animal; backend services (API in Go, word2animal and person-recognition in Python) communicate via gRPC. ML ops is implemented with Kubeflow for model training, versioning, and pipelines; model serving is done by the Python services. The entire backend is runnable locally (Kubernetes or Docker Compose) with the client on the same LAN.

## Technical Context

**API (backend gateway)**  
- **Language/Version**: Go 1.21+  
- **Primary Dependencies**: stdlib `net/http`, gRPC client libraries, OpenAPI/router (e.g. chi or gin), health/readiness endpoints  
- **Role**: Single entry point for the client; exposes REST; calls word2animal and person-recognition over gRPC  

**Microservices (ML)**  
- **Language/Version**: Python 3.11+  
- **Primary Dependencies**: grpcio, grpcio-tools (proto codegen), FastAPI or minimal ASGI (optional for health), ML runtime (e.g. ONNX, PyTorch, or scikit-learn depending on model)  
- **Role**: word2animal (text → animal); person-recognition (voice/embedding → identity); first release ships word2animal only  

**Client**  
- **Language/Version**: Python 3.11+ (existing)  
- **Role**: Speech-to-text on-device; HTTP client to backend REST API for text-to-animal; configurable backend base URL  

**Inter-service communication**  
- **Client ↔ Backend**: REST over HTTP (JSON).  
- **API ↔ Microservices**: gRPC (typed contracts, streaming optional later).  

**ML ops**  
- **Tool**: Kubeflow (Pipelines, Training, model versioning/artifacts).  
- **Serving**: Models loaded by Python services (no separate inference server in first release).  

**Storage**  
- **word2animal**: Model artifacts (e.g. object store or mounted volume); no DB for first release.  
- **person-recognition**: Voice-derived data up to 1GB (e.g. file store or SQLite); eviction when at cap.  

**Testing**  
- **API**: Go tests (stdlib testing or testify); contract tests against REST and gRPC.  
- **Services**: pytest; gRPC server tests; optional integration with real models.  
- **Client**: Existing pytest; add tests for REST client and “backend unreachable → error + random animal” behavior.  

**Target Platform**  
- **Backend**: Linux containers (Docker); local run via Kubernetes (kind/minikube) or Docker Compose.  
- **Client**: Raspberry Pi Zero W / desktop (existing).  

**Project Type**  
- Monorepo: client/ (Python app), backend/api (Go), backend/services/word2animal (Python), backend/services/person-recognition (Python), infra/ (K8s, Docker, Kubeflow manifests).  

**Performance Goals**  
- Text-to-animal round-trip (client → API → word2animal → API → client): ≤ 2 s under normal LAN (per spec SC-002).  
- Backend start to “all healthy”: &lt; 5 minutes (per spec SC-001).  

**Constraints**  
- Person recognition voice/voice-derived data ≤ 1GB (FR-012).  
- First release: text-to-animal + local backend only; person recognition in a later release.  
- No auth in spec for same-LAN; backend must still distinguish success vs validation vs unavailable (FR-010).  

**Scale/Scope**  
- Same-LAN; multiple clients concurrent; backend supports concurrent requests without cross-user mix-up.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Crawl-Walk-Run (NON-NEGOTIABLE)
✅ **PASS**: First release is crawl: text-to-animal via REST + local backend (API + word2animal). Person recognition is walk phase (later release). Each phase is independently testable.

### II. Simplicity First
✅ **PASS**: REST for client (simple HTTP/JSON); gRPC for backend internals (strong typing, one RPC per capability). Kubeflow used for ML ops only where it adds value (training/pipelines); serving is in-process in Python services.

### III. Modular Architecture
✅ **PASS**: Clear boundaries: client, API gateway, word2animal service, person-recognition service. Each service has a single responsibility; API is the only client-facing entry point.

### IV. Clear and Readable Code
✅ **PASS**: Go and Python with standard style; proto-defined contracts; small focused functions.

### V. Hardware Abstraction Layer
✅ **PASS**: Client already uses HAL for device; backend is pure software. No new hardware in this plan.

**Gate Status**: ✅ ALL GATES PASS

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-monorepo/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── rest-openapi.yaml    # Client ↔ API (REST)
│   └── grpc/                # API ↔ microservices (gRPC)
│       ├── word2animal.proto
│       └── person_recognition.proto
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Existing client (on-device Python; not dockerized)
client/
├── lib/                 # existing: lcd, microphone, etc.
├── app/                 # existing: main.py, voice_interaction, display_content, image_embeddings, etc.
├── ui/
└── playground/

# Backend: API gateway + microservices (grouped under backend/)
backend/
├── api/                 # Go; single entry point for client; calls microservices via gRPC
│   ├── cmd/
│   │   └── server/      # main, config, start REST + gRPC clients
│   ├── internal/
│   │   ├── rest/        # HTTP handlers, router, middleware
│   │   ├── grpcclient/  # gRPC clients to word2animal, person-recognition
│   │   └── health/      # health/readiness
│   ├── pkg/
│   │   └── proto/       # generated Go from .proto (or vendored)
│   ├── Dockerfile
│   ├── go.mod
│   └── go.sum
├── services/
│   ├── word2animal/     # Python; gRPC server; model loading per Kubeflow/ML ops
│   │   ├── src/
│   │   │   ├── server.py
│   │   │   ├── model_loader.py
│   │   │   └── inference.py
│   │   ├── proto/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── person-recognition/  # Python; gRPC server; first-use auto-enrollment; 1GB cap (later release)
│       ├── src/
│       │   ├── server.py
│       │   ├── store.py
│       │   └── inference.py
│       ├── proto/
│       ├── Dockerfile
│       └── requirements.txt

# Local run: choose one or both
infra/
├── docker-compose.yaml  # backend API + word2animal (and optionally person-recognition) for dev
├── k8s/                 # base manifests (deployments, services) for backend
└── kubeflow/            # pipelines/training jobs, model versioning (ML ops)
```

**Structure Decision**: Monorepo with `client/` (existing on-device Python app), `backend/api/` (Go REST+gRPC gateway), and `backend/services/word2animal` and `backend/services/person-recognition` (Python gRPC servers). REST between client and API; gRPC between API and microservices. Kubeflow used for ML ops (training, pipelines, model artifacts); serving in-process in Python services.

### Model versioning (FR-008, SC-006)

- **First release**: word2animal uses a config-driven model path (see T019 / `model_loader.py`); no artifact store required. Model path/version can be set via env or config file.
- **Later release**: Kubeflow Pipelines produce model artifacts; versioning and promotion (e.g. staging → prod) via Kubeflow artifact tracking. Services load artifact path/version from config or a small metadata service.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
