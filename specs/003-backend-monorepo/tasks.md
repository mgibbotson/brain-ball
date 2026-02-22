# Tasks: Brain Ball Backend Monorepo

**Input**: Design documents from `/specs/003-backend-monorepo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Optional test tasks included for API contract and client fallback; implement tests if desired.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently. First release = User Story 1 + User Story 2 (local backend + text-to-animal). User Story 3 (person recognition) is later release.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Client**: `client/` (on-device Python; existing)
- **Backend**: `backend/api/` (Go), `backend/services/word2animal/` (Python), `backend/services/person-recognition/` (Python)
- **Infra**: `infra/` (docker-compose, k8s, kubeflow)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Monorepo structure and backend layout per plan.md

- [x] T001 Create backend directory layout: backend/api/, backend/services/word2animal/, backend/services/person-recognition/, infra/
- [x] T002 Initialize Go module in backend/api/ (go.mod, go.sum) with module path per plan
- [x] T003 [P] Copy gRPC protos from specs/003-backend-monorepo/contracts/grpc/ into backend/api/pkg/proto/ and backend/services/word2animal/proto/ and backend/services/person-recognition/proto/
- [x] T004 [P] Create backend/services/word2animal/requirements.txt with grpcio, grpcio-tools, and minimal ML runtime (e.g. scikit-learn or placeholder)
- [x] T005 [P] Create backend/services/person-recognition/requirements.txt with grpcio, grpcio-tools (later release)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Proto codegen, health/readiness pattern, and Docker images so US1 and US2 can be built

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Generate Go gRPC client code from word2animal.proto in backend/api/pkg/proto/ (protoc or buf)
- [x] T007 [P] Implement gRPC server skeleton in backend/services/word2animal/src/server.py (load proto, expose Word2Animal.GetAnimal stub returning default animal)
- [x] T008 [P] Add health/readiness handlers to API: backend/api/internal/health/health.go (or equivalent) with /health (liveness) and /ready (readiness; check word2animal gRPC reachable)
- [x] T009 Add gRPC health check to backend/services/word2animal (grpc health protocol or HTTP /health on optional sidecar; ensure API /ready can probe it)
- [x] T010 Create Dockerfile for backend/api/ (multi-stage build, expose port 8080)
- [x] T011 Create Dockerfile for backend/services/word2animal/ (Python image, expose gRPC port)
- [x] T012 Wire API REST router and start HTTP server in backend/api/cmd/server/ (chi or gin; mount /health, /ready; no /v1/text-to-animal yet)

**Checkpoint**: Foundation ready — API and word2animal service skeletons exist and can be containerized; health/ready pattern in place

---

## Phase 3: User Story 1 - Developer Runs Full Backend Locally (Priority: P1) 🎯 MVP

**Goal**: A developer can run one command (or minimal steps) to start the entire backend stack locally and see all services healthy (SC-001).

**Independent Test**: Run documented “start backend” flow; curl /health and /ready on API; all backend components report healthy within &lt; 5 minutes.

- [x] T013 [US1] Add docker-compose.yaml in infra/ that starts backend API and word2animal service with correct ports and health checks
- [x] T014 [US1] Document “start backend” steps in specs/003-backend-monorepo/quickstart.md (Option A: Docker Compose) and ensure steps match infra/docker-compose.yaml
- [x] T015 [US1] Add script or make target at repo root to run “docker compose -f infra/docker-compose.yaml up -d” (or equivalent) for one-command start
- [x] T016 [US1] Verify API /ready returns 503 until word2animal is ready, then 200 when both are up; document verification in quickstart.md

**Checkpoint**: User Story 1 complete — developer can start full backend locally and verify all services healthy

---

## Phase 4: User Story 2 - Client Gets Animal from Text via API (Priority: P1)

**Goal**: Client sends recognized text to backend REST API; backend returns animal identifier; round-trip ≤ 2s. When backend unreachable, client shows error + random animal (FR-011).

**Independent Test**: POST /v1/text-to-animal with {"text":"beak"} returns 200 and {"animal":"bird"} (or equivalent); client displays it; when API is down, client shows error and a random animal.

### Implementation for User Story 2

- [x] T017 [P] [US2] Implement word2animal inference in backend/services/word2animal/src/inference.py (text → animal; use stub mapping or simple model; config-driven model path per data-model.md)
- [x] T018 [US2] Implement word2animal gRPC handler in backend/services/word2animal/src/server.py calling inference and returning GetAnimalResponse (animal, optional confidence)
- [x] T019 [US2] Add model loader in backend/services/word2animal/src/model_loader.py (load artifact from config path/version; support no-op or static map for first release)
- [x] T020 [US2] Implement REST POST /v1/text-to-animal in backend/api/internal/rest/ (validate request body: text required, max length 500; call word2animal via gRPC; return 200 + JSON animal or 400/503 per contracts/rest-openapi.yaml)
- [x] T021 [US2] Implement gRPC client to word2animal in backend/api/internal/grpcclient/ (dial word2animal address from config; call GetAnimal; handle Unavailable → API returns 503)
- [x] T022 [US2] Add config in backend/api for word2animal gRPC address (env or config file) and HTTP listen address (e.g. :8080)
- [x] T023 [US2] Add HTTP client in client/app for backend API: module or helper in client/app/ (e.g. client/app/backend_client.py) that POSTs to configurable base URL /v1/text-to-animal with {"text": ...} and returns animal or error
- [x] T024 [US2] Add client configuration for backend base URL (env BRAIN_BALL_API_URL or config file) in client/app; document in README or quickstart
- [x] T025 [US2] Refactor client voice_interaction (or display path) in client/app/ to call backend client for text-to-animal when backend URL is set; when backend unreachable, show clear error and display random animal (FR-011)
- [x] T026 [US2] Ensure API returns 400 for empty or invalid text and 503 when word2animal is down; client handles both and shows consistent behavior per spec edge cases
- [x] T027 [US2] Verify round-trip ≤ 2s (SC-002): add integration test or script that POSTs /v1/text-to-animal and asserts response time ≤ 2s under normal conditions; or document manual verification in quickstart.md

**Checkpoint**: User Story 2 complete — client gets animal from text via API; backend unreachable → error + random animal

---

## Phase 5: User Story 3 - Backend Recognizes Person from Voice (Priority: P2, Later Release)

**Goal**: Backend accepts voice (or voice-derived) input and returns person identity; first-use auto-enrollment; voice-derived data capped at 1GB (FR-012).

**Independent Test**: POST /v1/person-recognition with embedding/audio returns person_id and is_new; same voice returns same person_id; total storage ≤ 1GB.

- [ ] T028 [P] [US3] Implement person-recognition gRPC server skeleton in backend/services/person-recognition/src/server.py (IdentifyOrEnroll stub)
- [ ] T029 [US3] Implement voice-derived store in backend/services/person-recognition/src/store.py with 1GB cap and eviction (e.g. oldest or least-used) per FR-012
- [ ] T030 [US3] Implement first-use auto-enrollment and identification in backend/services/person-recognition/src/inference.py (match or create identity from embedding)
- [ ] T031 [US3] Implement REST POST /v1/person-recognition in backend/api/internal/rest/ and gRPC client to person-recognition in backend/api/internal/grpcclient/
- [ ] T032 [US3] Add person-recognition service to infra/docker-compose.yaml and optional K8s manifests in infra/k8s/
- [ ] T033 [US3] Enforce 1GB limit in store: reject or evict when at cap; return gRPC ResourceExhausted when at limit

**Checkpoint**: User Story 3 complete — person recognition available; first-use auto-enrollment; 1GB cap enforced

---

## Phase 6: User Story 4 - Client and Backend on Same Local Network (Priority: P2)

**Goal**: Client configurable with backend base URL; core flows work on same LAN without internet (SC-004).

**Independent Test**: Run backend on one machine, client on another on same LAN; set client backend URL to host:port; complete text-to-animal without internet.

- [x] T034 [US4] Document same-LAN setup in specs/003-backend-monorepo/quickstart.md: how to set BRAIN_BALL_API_URL to http://&lt;host-ip&gt;:8080 and run client on another device
- [x] T035 [US4] Verify client uses configurable base URL for all API calls (no hardcoded localhost in production path) in client/app/

**Checkpoint**: User Story 4 complete — client and backend work on same LAN with configurable URL

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Observability, validation, and docs

- [x] T036 [P] Add structured logging in backend/api (request id, status, latency) and in backend/services/word2animal
- [x] T037 [P] Add request validation and consistent error response body (code, message) for API per contracts/rest-openapi.yaml
- [ ] T038 Run quickstart.md flow end-to-end and fix any gaps (Docker Compose start, health/ready, POST /v1/text-to-animal, client with backend URL)
- [x] T039 [P] Add optional K8s manifests in infra/k8s/ for API and word2animal (Deployment, Service) and document Option B in quickstart.md
- [x] T040 Add Makefile or script at repo root for build-images (backend/api, backend/services/word2animal) and load into kind if using K8s
- [x] T041 [P] Document model versioning (FR-008, SC-006): first release uses config-driven model path per T019; Kubeflow pipelines/artifact versioning for later release — add note in plan.md or quickstart.md
- [x] T042 [P] Document resource usage and timing characteristics (constitution) in quickstart.md or README: e.g. expected memory/CPU for backend services, round-trip latency target (2s), backend start time (&lt; 5 min)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational — can start after T012
- **User Story 2 (Phase 4)**: Depends on Foundational; benefits from US1 (running backend) but can be developed in parallel (API + word2animal + client tasks)
- **User Story 3 (Phase 5)**: Depends on Foundational; independent of US1/US2; later release
- **User Story 4 (Phase 6)**: Depends on US2 (client already has backend URL); small doc/config tasks
- **Polish (Phase 7)**: Depends on US1 + US2 (and optionally US3/US4) complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no dependency on US2/US3/US4
- **US2 (P1)**: After Phase 2 — no dependency on US3; US4 doc assumes US2 client exists
- **US3 (P2, later release)**: After Phase 2 — independent of US1/US2
- **US4 (P2)**: After US2 client has backend URL; doc and verification only

### Within Each User Story

- US1: docker-compose and quickstart before verification task
- US2: word2animal inference + gRPC handler before API REST handler; API gRPC client before REST handler; client backend client before refactoring voice_interaction
- US3: store + inference before REST/gRPC wiring

### Parallel Opportunities

- Phase 1: T003, T004, T005 can run in parallel
- Phase 2: T007, T008 (and T009) can run in parallel after T006; T010, T011 can run in parallel
- Phase 4: T017, T019 can run in parallel; T023, T024 can run in parallel
- Phase 7: T036, T037, T039, T041, T042 can run in parallel
- Different user stories (US1, US2, US3) can be worked in parallel by different developers after Phase 2

---

## Parallel Example: User Story 2

```text
# Word2animal service (can do together):
T017 Implement inference in backend/services/word2animal/src/inference.py
T019 Add model_loader in backend/services/word2animal/src/model_loader.py

# Client (can do together):
T023 Add HTTP client in client/app/backend_client.py
T024 Add client configuration for backend base URL
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (local backend run)
4. Complete Phase 4: User Story 2 (text-to-animal API + client)
5. **STOP and VALIDATE**: Run quickstart; POST /v1/text-to-animal; verify round-trip ≤ 2s (T027); run client with backend URL; test backend unreachable → error + random animal
6. Deploy/demo first release

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → test “start backend” independently
3. Add US2 → test text-to-animal + client independently (MVP)
4. Add US4 → doc and config (small)
5. Add US3 (later release) → person recognition
6. Polish → logging, K8s, quickstart validation

### Parallel Team Strategy

- After Phase 2: Developer A — US1 (infra, quickstart); Developer B — US2 (word2animal + API + client)
- US3 can be picked up later by any developer (person-recognition service + API + client optional)

---

## Notes

- [P] = different files, no dependencies
- [USn] maps task to user story for traceability
- First release = US1 + US2; US3 is later release; US4 is config/doc on top of US2
- Use paths from plan: client/, backend/api/, backend/services/word2animal/, backend/services/person-recognition/, infra/
- Commit after each task or logical group; stop at any checkpoint to validate story independently
