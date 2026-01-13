#!/bin/bash

# Protocol Buffers code generation for Node 0 MCP Server

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$PROJECT_ROOT/protos"
OUTPUT_DIR="$PROJECT_ROOT/generated"

echo "Generating Python code from .proto files..."

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate Python code from proto files
python3 -m grpc_tools.protoc \
  --proto_path="$PROTO_DIR" \
  --python_out="$OUTPUT_DIR" \
  --grpc_python_out="$OUTPUT_DIR" \
  --pyi_out="$OUTPUT_DIR" \
  "$PROTO_DIR"/*.proto

# Create __init__.py
touch "$OUTPUT_DIR/__init__.py"

echo "✅ Code generation complete!"
echo "Generated files in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"
