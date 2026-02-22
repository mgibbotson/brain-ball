# Data Model: Brain Ball Backend Monorepo

**Date**: 2025-02-21  
**Phase**: First release (text-to-animal + local backend); person recognition in later release.

## API Surface (REST: Client ↔ API)

### Text-to-Animal Request (client → API)
Represents a single request from the client containing the recognized text.

**Fields**:
- `text` (string): The word or phrase from speech-to-text (e.g. "beak", "fur").
- Optional: `person_id` (string): For future personalization; omit or null in first release.

**Validation Rules**:
- `text` must be non-empty and within a reasonable length (e.g. ≤ 500 characters).
- Empty or invalid input → API returns 400 with clear error; client shows consistent behavior (per spec edge cases).

### Text-to-Animal Response (API → client)
Contains the chosen animal or identifier for display.

**Fields**:
- `animal` (string): Stable identifier/label (e.g. "bird", "dog") for the client to map to images/assets.
- Optional: `confidence` (float 0–1) or `alternatives` (array) for future use.
- On error: HTTP 4xx/5xx with body indicating validation error or service unavailability (FR-010).

**State / Lifecycle**:
- Stateless; no server-side session. Each request is independent.

### Person Recognition Request (client → API) — later release
Contains voice or voice-derived data for the current speaker.

**Fields**:
- `audio` or `embedding` (payload): Raw audio bytes or precomputed embedding; exact format TBD (e.g. base64 PCM, or float array).
- Optional metadata (sample rate, duration).

**Validation Rules**:
- Payload size bounded (e.g. max 1MB per request) to avoid abuse.
- Backend enforces 1GB total retained voice-derived data (FR-012); eviction or reject when at cap.

### Person Recognition Response (API → client) — later release
Contains the identity of the speaker or unknown/error.

**Fields**:
- `person_id` (string): Stable anonymous identifier (e.g. "person_1") or empty/"unknown".
- `is_new` (boolean): True if this request created a new identity (first-use auto-enrollment).
- On error or unknown: `person_id` empty or "unknown", or HTTP 4xx/5xx.

**Identity Lifecycle**:
- First-use auto-enrollment: first time a voice is seen, backend creates a new identity (e.g. "person_1"); subsequent requests from same voice map to that identity.
- Storage for voice-derived data capped at 1GB; eviction policy when at limit (oldest or least-used; TBD in implementation).

## gRPC Surface (API ↔ Microservices)

### Word2Animal (API ↔ word2animal service)
- **Request**: `text` (string).
- **Response**: `animal` (string), optional `confidence` (float).
- **Errors**: gRPC status codes (e.g. InvalidArgument for empty text, Unavailable if service down).

### Person Recognition (API ↔ person-recognition service) — later release
- **Request**: `audio` or `embedding` (bytes or repeated float).
- **Response**: `person_id` (string), `is_new` (bool).
- **Errors**: gRPC status codes; ResourceExhausted when at 1GB cap.

## Internal Storage (Backend)

### Word2Animal Service
- **Model artifact**: Path or URI to model file (e.g. from Kubeflow artifact store or mounted volume). No DB; config-driven model version/path (FR-008, SC-006).
- **No persistent request/response storage** in first release.

### Person Recognition Service — later release
- **Voice-derived store**: Up to 1GB total (FR-012). Each identity has associated data (e.g. embedding vectors); eviction when at cap.
- **Identity registry**: Map person_id ↔ stored data; first-use creates new person_id and stores derived data.

## Relationships

- **Client** sends REST **Text-to-Animal Request** → **API** → gRPC to **word2animal** → **API** returns REST **Text-to-Animal Response**.
- **Client** (later) sends REST **Person Recognition Request** → **API** → gRPC to **person-recognition** → **API** returns REST **Person Recognition Response**.
- **Person recognition** store is self-contained within the service; API does not persist person data.

## Data Flow (First Release)

1. Client (speech-to-text on-device) produces `text`.
2. Client HTTP POST to API `/v1/text-to-animal` with `{ "text": "beak" }`.
3. API validates, calls word2animal service via gRPC with `text`.
4. Word2animal loads model (from config), runs inference, returns `animal` (e.g. "bird").
5. API returns 200 and `{ "animal": "bird" }` to client.
6. Client maps `animal` to display asset and shows it; if backend unreachable, client shows error + random animal (FR-011).
