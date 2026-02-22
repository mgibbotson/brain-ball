package grpcclient

import (
	"context"
	"fmt"
	"strings"

	"brainball/api/pkg/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	_ "google.golang.org/grpc/resolver/dns"
)

// Word2AnimalClient dials word2animal gRPC and calls GetAnimal.
type Word2AnimalClient struct {
	conn   *grpc.ClientConn
	client proto.Word2AnimalClient
}

// dialTarget returns the gRPC dial target. Use dns:///host:port so Docker/K8s DNS resolves.
func dialTarget(addr string) string {
	addr = strings.TrimSpace(addr)
	if addr == "" || strings.Contains(addr, "://") {
		return addr
	}
	return "dns:///" + addr
}

// NewWord2AnimalClient connects to addr and returns a client.
func NewWord2AnimalClient(ctx context.Context, addr string) (*Word2AnimalClient, error) {
	target := dialTarget(addr)
	conn, err := grpc.DialContext(ctx, target,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock())
	if err != nil {
		return nil, fmt.Errorf("word2animal dial: %w", err)
	}
	return &Word2AnimalClient{
		conn:   conn,
		client: proto.NewWord2AnimalClient(conn),
	}, nil
}

// GetAnimal returns the animal for the given text.
func (c *Word2AnimalClient) GetAnimal(ctx context.Context, text string) (string, float32, error) {
	resp, err := c.client.GetAnimal(ctx, &proto.GetAnimalRequest{Text: text})
	if err != nil {
		return "", 0, err
	}
	return resp.Animal, resp.Confidence, nil
}

// Close closes the gRPC connection.
func (c *Word2AnimalClient) Close() error {
	return c.conn.Close()
}
