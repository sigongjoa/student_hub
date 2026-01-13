#!/bin/bash

# Start all gRPC MCP servers

cd /mnt/d/progress/mathesis/node0_student_hub
export PYTHONPATH=/mnt/d/progress/mathesis/node0_student_hub

echo "Starting Node 2 (Q-DNA) on port 50052..."
python3 app/grpc_services/node2_qdna_server.py &
NODE2_PID=$!

sleep 2

echo "Starting Node 4 (Lab Node) on port 50053..."
python3 app/grpc_services/node4_labnode_server.py &
NODE4_PID=$!

sleep 2

echo "Starting Node 7 (Error Note) on port 50054..."
python3 app/grpc_services/node7_errornote_server.py &
NODE7_PID=$!

sleep 3

echo "✅ All servers started!"
echo "Node 2 PID: $NODE2_PID"
echo "Node 4 PID: $NODE4_PID"
echo "Node 7 PID: $NODE7_PID"

# Keep script running
wait
