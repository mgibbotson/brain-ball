package middleware

import (
	"crypto/rand"
	"encoding/hex"
	"log/slog"
	"net/http"
	"time"
)

// responseWriter wraps http.ResponseWriter to capture status and size.
type responseWriter struct {
	http.ResponseWriter
	status int
	size   int
}

func (w *responseWriter) WriteHeader(code int) {
	w.status = code
	w.ResponseWriter.WriteHeader(code)
}

func (w *responseWriter) Write(b []byte) (int, error) {
	n, err := w.ResponseWriter.Write(b)
	w.size += n
	return n, err
}

// Logging returns a middleware that logs request_id, method, path, status, and duration_ms.
func Logging(logger *slog.Logger) func(http.Handler) http.Handler {
	if logger == nil {
		logger = slog.Default()
	}
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			reqID := genRequestID()
			start := time.Now()
			wrap := &responseWriter{ResponseWriter: w, status: http.StatusOK}
			next.ServeHTTP(wrap, r)
			dur := time.Since(start)
			logger.Info("request",
				"request_id", reqID,
				"method", r.Method,
				"path", r.URL.Path,
				"status", wrap.status,
				"duration_ms", dur.Milliseconds(),
			)
		})
	}
}

func genRequestID() string {
	b := make([]byte, 8)
	if _, err := rand.Read(b); err != nil {
		return "unknown"
	}
	return hex.EncodeToString(b)
}
