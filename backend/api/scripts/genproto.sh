#!/bin/bash
set -e
apt-get update -qq && apt-get install -y -qq protobuf-compiler > /dev/null
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.31.0
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3.0
export PATH="$PATH:$(go env GOPATH)/bin"
protoc -I pkg/proto --go_out=pkg/proto --go_opt=paths=source_relative \
  --go-grpc_out=pkg/proto --go-grpc_opt=paths=source_relative \
  pkg/proto/word2animal.proto
