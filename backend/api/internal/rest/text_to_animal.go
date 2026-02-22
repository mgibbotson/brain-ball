package rest

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"

	"brainball/api/internal/grpcclient"
)

const maxTextLength = 500

// TextToAnimalRequest is the JSON body for POST /v1/text-to-animal.
type TextToAnimalRequest struct {
	Text string `json:"text"`
}

// TextToAnimalResponse is the JSON response.
type TextToAnimalResponse struct {
	Animal     string  `json:"animal"`
	Confidence float32 `json:"confidence,omitempty"`
}

// ErrorResponse is the JSON error body.
type ErrorResponse struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

// TextToAnimalHandler holds word2animal address and optional client; reconnects on demand.
type TextToAnimalHandler struct {
	addr   string
	client *grpcclient.Word2AnimalClient
	mu     sync.Mutex
}

// NewTextToAnimalHandler returns a handler that calls word2animal (reconnects if client is nil).
func NewTextToAnimalHandler(addr string, client *grpcclient.Word2AnimalClient) *TextToAnimalHandler {
	return &TextToAnimalHandler{addr: addr, client: client}
}

// ServeHTTP handles POST /v1/text-to-animal.
func (h *TextToAnimalHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "method_not_allowed", "method not allowed")
		return
	}
	var req TextToAnimalRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "invalid_request", "invalid JSON")
		return
	}
	text := strings.TrimSpace(req.Text)
	if text == "" {
		writeError(w, http.StatusBadRequest, "invalid_request", "text is required")
		return
	}
	if len(text) > maxTextLength {
		writeError(w, http.StatusBadRequest, "invalid_request", "text too long")
		return
	}
	h.mu.Lock()
	client := h.client
	h.mu.Unlock()
	if client == nil {
		ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
		c, err := grpcclient.NewWord2AnimalClient(ctx, h.addr)
		cancel()
		if err != nil {
			log.Printf("word2animal dial failed: %v", err)
			writeError(w, http.StatusServiceUnavailable, "service_unavailable", "word2animal unavailable")
			return
		}
		h.mu.Lock()
		h.client = c
		h.mu.Unlock()
		client = c
	}
	animal, confidence, err := client.GetAnimal(r.Context(), text)
	if err != nil {
		log.Printf("word2animal GetAnimal failed: %v", err)
		h.mu.Lock()
		h.client = nil
		h.mu.Unlock()
		writeError(w, http.StatusServiceUnavailable, "service_unavailable", "word2animal unavailable")
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(TextToAnimalResponse{Animal: animal, Confidence: confidence})
}

func writeError(w http.ResponseWriter, status int, code, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(ErrorResponse{Code: code, Message: message})
}
