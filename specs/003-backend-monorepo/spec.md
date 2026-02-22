# Feature Specification: Brain Ball Backend Monorepo

**Feature Branch**: `003-backend-monorepo`  
**Created**: 2025-02-21  
**Status**: Draft  
**Input**: User description: "Let's build out our backend for brain ball. I want this repository to become a Monorepo sharing multiple packages, starting with: client (on-device, python, existing code, not dockerized), API (backend, golang, new code to support a REST API that links client with backend services, dockerized), person recognition service (backend, python, new code to recognize a person based on their voice, dockerized), word2animal service (backend, python, new code to select an animal based on text input -- like 'beak' might show a bird, dockerized). Speech-to-text will still occur on the client device, but the current text-to-animal should be offloaded to the backend via API calls. Backend should follow kubernetes and ML ops practices, and the entire backend should be spun up locally on any developer's machine. Expect the client to be on the same local network as the backend."

## Clarifications

### Session 2025-02-21

- Q: Who enrolls voices for person recognition, and when? (Impacts: data model, API design, UX.) → A: First-use auto-enrollment — first time a voice is heard, backend creates an identity (e.g. anonymous "Person 1"); same voice later maps to that identity.
- Q: When the backend (or text-to-animal API) is unreachable, should the client fall back to on-device text-to-animal or only show an error? → A: Show an error and a random animal — user sees that the backend is unavailable and a random animal is displayed so the experience continues.
- Q: Is person recognition required for the first shippable release, or can it follow after text-to-animal and local backend? → A: Can follow in a later release — first release is text-to-animal + local backend; person recognition can be added afterward.
- Q: Should the spec pin a concrete round-trip latency target for text-to-animal (for testability and SLOs)? → A: 2 seconds.
- Q: For person recognition, should voice/voice-derived data be retained on the backend after the request, and if so for what purpose? → A: Retained up to a 1GB limit.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Runs Full Backend Locally (Priority: P1)

A developer clones the repository and runs a single command (or minimal steps) to start the entire backend stack on their machine. All backend services come up in a consistent way, and the developer can verify they are healthy without needing the on-device client.

**Why this priority**: Without a repeatable local backend, developers cannot build or debug the API and ML services. This is the foundation for all other backend work.

**Independent Test**: Can be fully tested by running the documented “start backend” flow on a clean machine and confirming all services report healthy. Delivers value by enabling any contributor to develop backend features.

**Acceptance Scenarios**:

1. **Given** a developer on a machine with the repo and required tooling, **When** they follow the documented steps to start the backend, **Then** all backend services start and report a healthy/ready state.
2. **Given** the backend is running locally, **When** the developer checks service availability (e.g., health endpoints or equivalent), **Then** each backend component is reachable and indicates it is ready to accept work.

---

### User Story 2 - Client Gets Animal from Text via API (Priority: P1)

A user speaks on the device; speech-to-text runs on the device and produces text. The client sends that text to the backend. The backend returns an animal (or equivalent representation) chosen from the text (e.g., “beak” suggests a bird). The client uses that result to show the correct animal or image.

**Why this priority**: This is the core product flow—moving text-to-animal from on-device to the backend so the system can scale and improve the mapping over time.

**Independent Test**: Can be tested by sending a text string to the backend API and verifying the response contains an appropriate animal (or identifier) for that text, without needing the physical device.

**Acceptance Scenarios**:

1. **Given** the backend is running and the client has network access to it, **When** the client sends the recognized text (e.g., “beak”) to the backend, **Then** the backend returns an animal (or identifier) that matches the intent (e.g., bird).
2. **Given** the backend is running, **When** a request is sent with valid text input, **Then** the response is returned within 2 seconds (under normal LAN conditions) and in a defined structure the client can use for display.

---

### User Story 3 - Backend Recognizes Person from Voice (Priority: P2)

A user speaks on the device; the client may send voice (or derived) data to the backend. The backend identifies which person is speaking and returns that identity so the experience can be personalized (e.g., per-user animals or preferences).

**Why this priority**: Enables personalized behavior and future features; depends on the API and local backend being in place.

**Independent Test**: Can be tested by sending voice (or voice-derived) data to the backend and verifying the returned identity is consistent for the same person and distinct for different people where applicable.

**Acceptance Scenarios**:

1. **Given** the backend is running and person recognition is configured, **When** the client sends voice (or voice-derived) data for a known person, **Then** the backend returns an identity consistent with that person.
2. **Given** the backend is running, **When** a recognition request is sent, **Then** the response indicates either a recognized person or an appropriate “unknown”/error state.

---

### User Story 4 - Client and Backend on Same Local Network (Priority: P2)

The on-device client and the backend run on the same local network (e.g., home or office LAN). The client discovers or is configured with the backend base URL and uses it for all API calls. No public internet is required for core flows.

**Why this priority**: Matches the stated deployment model and keeps latency low and setup simple for developers and users.

**Independent Test**: Can be tested by running the backend on one machine and the client (or a test client) on another machine on the same LAN and verifying successful API calls.

**Acceptance Scenarios**:

1. **Given** the backend is running on a host on the LAN and the client is on the same LAN, **When** the client is configured with that backend base URL, **Then** the client can reach the API and complete text-to-animal (and optionally person recognition) calls.
2. **Given** the client is configured with the backend URL, **When** the user triggers a flow that requires the backend, **Then** the request is sent to the backend and a response is received without requiring public internet.

---

### Edge Cases

- What happens when the backend (or a specific service) is unreachable? The client MUST show a clear error indicating the backend is unavailable and MUST display a random animal so the user still sees feedback; the client MUST NOT block the user indefinitely.
- What happens when text input is empty, very long, or invalid? The API should return a well-defined error or default so the client can show a consistent behavior.
- What happens when person recognition cannot identify the speaker? The backend should return an explicit “unknown” or equivalent so the client can apply a default experience.
- What happens when the backend is starting or restarting? Health checks and readiness should distinguish “not ready” so clients or load balancers can avoid sending traffic until ready.
- What happens when multiple clients use the backend at once? The backend should support concurrent requests without incorrect or cross-user results (e.g., correct animal and identity per request).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST be organized as a monorepo containing at least: a client package (on-device, existing behavior preserved), a backend API package, a person-recognition backend service, and a text-to-animal backend service.
- **FR-002**: The backend MUST expose a REST API that accepts text input and returns an animal (or stable identifier) suitable for display, so the client can offload text-to-animal to the backend.
- **FR-003**: Speech-to-text MUST remain on the client device; only the step that maps text to animal is performed by the backend.
- **FR-004**: The backend MUST provide a person-recognition capability that accepts voice (or voice-derived) input and returns an identity (or “unknown”) for the speaker. Person identities MUST be created on first use (first-use auto-enrollment): the first time a voice is heard, the backend creates an identity (e.g. anonymous “Person 1”); subsequent requests from the same voice MUST map to that identity.
- **FR-005**: The backend API MUST act as the single entry point the client uses to reach backend capabilities (text-to-animal and person recognition); the client MUST NOT call backend services directly by implementation-specific URLs.
- **FR-006**: The backend MUST be startable locally on a developer’s machine so that all backend services run together with a documented, repeatable process.
- **FR-007**: Backend services MUST follow practices suitable for containerized deployment and operational visibility (e.g., health/readiness, structured logging, configuration external to code) so they can be run in local clusters and later in production-like environments.
- **FR-008**: Backend ML-oriented services (person recognition, text-to-animal) MUST be deployable and configurable in a way that supports model updates and versioning without changing application code, consistent with common ML ops practices.
- **FR-009**: The system MUST support the client and backend running on the same local network; the client MUST be configurable with the backend base URL (or discovery mechanism) so it can reach the API without relying on public internet for core flows.
- **FR-010**: The backend MUST respond with clear success and error outcomes so the client can distinguish success, validation errors, and service unavailability.
- **FR-011**: When the backend (or text-to-animal API) is unreachable, the client MUST show a clear error that the backend is unavailable and MUST display a random animal so the experience continues without blocking the user.
- **FR-012**: Voice or voice-derived data retained by the backend for person recognition MUST NOT exceed 1GB total; the system MUST enforce this limit (e.g., by eviction or rejection of new enrollment when at capacity).

### Key Entities

- **Text-to-animal request**: Represents a single request from the client containing the recognized text (e.g., word or phrase). Used to select and return an animal (or identifier) for display.
- **Text-to-animal response**: Contains the chosen animal or identifier and any metadata needed for the client to display the correct asset or label.
- **Person recognition request**: Contains voice (or voice-derived) data for the current speaker. Used to identify the person.
- **Person recognition response**: Contains the identity of the speaker (or an explicit unknown/error state) for personalization.
- **Backend service**: A deployable unit that implements one or more capabilities (API gateway, text-to-animal, person recognition) and exposes health/readiness and configuration consistent with the rest of the stack.

## Assumptions

- The existing on-device client will be refactored to call the backend API for text-to-animal while keeping speech-to-text on-device; the in-repo client package remains the source of truth for device behavior.
- “Animal” in the spec means a stable identifier or label (e.g., bird, dog) that the client can map to images or assets; the exact format of the response is an API design detail.
- Local backend “spin up” is achieved via a single orchestration mechanism (e.g., scripts or local cluster) that starts all backend services with minimal manual steps.
- Person recognition may use voice embeddings or similar derived data rather than raw audio in the API contract, to reduce payload size and align with typical ML pipelines; the exact payload is a design detail. No separate enrollment flow is required; identities are created on first encounter (first-use auto-enrollment).
- Health and readiness endpoints (or equivalent) are the standard way for developers and orchestration to verify that services are running correctly.
- No authentication is required for the initial local/same-LAN scenario; security and auth for wider deployment are out of scope for this spec unless explicitly added later.
- Person recognition is not required for the first shippable release; the first release is text-to-animal via API plus local backend. Person recognition can be added in a later release.
- Voice or voice-derived data may be retained on the backend for person recognition up to a 1GB limit; the system must enforce this cap.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new developer can start the full backend on their machine using the documented process and see all services healthy within a defined, reasonable time (e.g., under five minutes from “start” to “all green”).
- **SC-002**: When the client sends recognized text to the backend, the user sees the correct animal (or fallback) on the device; the round-trip from text send to display update completes within 2 seconds under normal LAN conditions.
- **SC-003**: Person recognition returns a consistent identity for the same speaker across multiple requests in a session, when the system is configured for that speaker.
- **SC-004**: The client can be pointed at a backend on the same LAN and complete text-to-animal and (when used) person-recognition flows without internet access.
- **SC-005**: Backend services expose health/readiness in a consistent way so that “all services up” can be verified automatically (e.g., by a script or dashboard).
- **SC-006**: Model or configuration changes for text-to-animal or person recognition can be applied without redeploying or rewriting the main application code, in line with standard ML ops practices.
