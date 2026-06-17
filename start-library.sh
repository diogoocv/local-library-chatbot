#!/bin/bash

echo "======================================"
echo "Booting Distributed Microservices..."
echo "======================================"

# Activate the virtual environment
source venv/bin/activate

# Set up a trap to kill all background processes when the user presses Ctrl+C
trap 'echo -e "\nShutting down all microservices..."; kill $(jobs -p); exit' SIGINT SIGTERM

# Start the Ollama container (Assuming docker-compose is in the root)
echo "Starting local Llama 3 container..."
docker compose up -d

# Boot all Python microservices in the background using subshells to handle directories
echo "Starting API Gateway (:8000)..."
(cd services/api-gateway && uvicorn main:app --port 8000) &

echo "Starting Document Metadata Service (:8001)..."
(cd services/document-metadata-service && uvicorn main:app --port 8001) &

echo "Starting Text Extractor Service (:8002)..."
(cd services/text-extractor-service && uvicorn main:app --port 8002) &

echo "Starting Vector DB Service (:8003)..."
(cd services/vector-database-service && uvicorn main:app --port 8003) &

echo "Starting MCP Host Service (:8004)..."
(cd services/mcp-host-service && uvicorn main:app --port 8004) &

echo "Starting Saga Orchestrator (:8005)..."
(cd services/saga-orchestrator && uvicorn main:app --port 8005) &

# Give the backend a few seconds to initialize
sleep 5

echo "======================================"
echo "Backend is live. Launching Zotero Extension..."
echo "======================================"

# Boot the frontend in the foreground so the user sees the Zotero logs
cd client/zotero-plugin
npm start