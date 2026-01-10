#!/bin/bash

# Protocol Buffers 코드 생성

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$PROJECT_ROOT/protos"
OUTPUT_DIR="$PROJECT_ROOT/generated"

echo "🔧 Generating Python code from .proto files..."

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# protoc로 Python 코드 생성
python3 -m grpc_tools.protoc \
  --proto_path="$PROTO_DIR" \
  --python_out="$OUTPUT_DIR" \
  --grpc_python_out="$OUTPUT_DIR" \
  "$PROTO_DIR"/*.proto

# __init__.py 생성
touch "$OUTPUT_DIR/__init__.py"

echo "✅ Code generation complete!"
echo "📁 Generated files in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"
