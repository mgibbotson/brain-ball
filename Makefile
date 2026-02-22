# Brain Ball monorepo
# Backend: API (Go) + word2animal (Python)

.PHONY: backend-up backend-down backend-build

backend-up:
	docker compose -f infra/docker-compose.yaml up -d

backend-down:
	docker compose -f infra/docker-compose.yaml down

backend-build:
	docker compose -f infra/docker-compose.yaml build

backend-restart:
	docker compose -f infra/docker-compose.yaml down
	docker compose -f infra/docker-compose.yaml up -d

backend-restart-rebuild:
	docker compose -f infra/docker-compose.yaml down
	docker compose -f infra/docker-compose.yaml build
	docker compose -f infra/docker-compose.yaml up -d

# Regenerate Go gRPC/protobuf code (requires Docker)
proto:
	docker run --rm -v "$$(pwd)/backend/api:/app" -w /app golang:1.21-bookworm bash /app/scripts/genproto.sh

# Build API and word2animal images (for kind load)
build-images:
	docker build -t brainball/api:latest backend/api
	docker build -t brainball/word2animal:latest backend/services/word2animal
