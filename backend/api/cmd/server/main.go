package main

import (
	"context"
	"log"
	"log/slog"
	"net/http"
	"os"
	"time"

	"brainball/api/internal/grpcclient"
	"brainball/api/internal/health"
	"brainball/api/internal/middleware"
	"brainball/api/internal/rest"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	addr := os.Getenv("HTTP_ADDR")
	if addr == "" {
		addr = ":8080"
	}
	word2animalAddr := os.Getenv("WORD2ANIMAL_GRPC_ADDR")
	if word2animalAddr == "" {
		word2animalAddr = "localhost:50051"
	}

	readyFunc := func() error {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
		conn, err := grpc.DialContext(ctx, word2animalAddr,
			grpc.WithTransportCredentials(insecure.NewCredentials()),
			grpc.WithBlock())
		if err != nil {
			return err
		}
		conn.Close()
		return nil
	}

	// Word2Animal gRPC client for /v1/text-to-animal (optional at startup; handler returns 503 if unreachable)
	ctx := context.Background()
	wc, err := grpcclient.NewWord2AnimalClient(ctx, word2animalAddr)
	if err != nil {
		log.Printf("word2animal client (will retry on request): %v", err)
		wc = nil
	} else {
		defer wc.Close()
	}
	handler := rest.NewTextToAnimalHandler(word2animalAddr, wc)

	mux := http.NewServeMux()
	mux.HandleFunc("/health", health.Health)
	mux.HandleFunc("/ready", health.Ready(readyFunc))
	mux.Handle("/v1/text-to-animal", handler)

	handlerWithLogging := middleware.Logging(slog.Default())(mux)
	log.Printf("API listening on %s", addr)
	if err := http.ListenAndServe(addr, handlerWithLogging); err != nil {
		log.Fatal(err)
	}
}
