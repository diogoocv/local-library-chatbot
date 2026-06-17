import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for backend service routing
MCP_HOST_SERVICE_URL = os.getenv("MCP_HOST_SERVICE_URL", "http://localhost:8004")
SAGA_ORCHESTRATOR_URL = os.getenv("SAGA_ORCHESTRATOR_URL", "http://localhost:8005")

class ChatRequest(BaseModel):
    question: str
    google_api_key: str = ""

@app.post("/query")
async def handle_chat_query(payload: ChatRequest):
    """
    Intercepts the frontend request and routes it
    to the intelligent LangChain MCP host router.
    """
    try:
        # Forward the payload to the LangChain router
        response = requests.post(
            f"{MCP_HOST_SERVICE_URL}/route_query",
            json={
                "question": payload.question,
                "google_api_key": payload.google_api_key,
                "context_chunks": [] # The router's tool will pull chunks from ChromaDB
            },
            timeout=300 # Allow time for the local model to process
        )

        # Check if the microservice returned an error
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Router Error: {response.text}")
        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to the routing service: {str(e)}"
        )

@app.post("/upload")
async def handle_file_upload(file: UploadFile = File(...)):
    """
    Receives the PDF binary from the frontend and proxies it directly
    to the Saga Orchestrator to start the distributed ingestion transaction.
    """
    try:
        # Read binary file data into memory
        file_content = await file.read()

        # Format as multipart form data to pass to the next service
        files = {'file': (file.filename, file_content, file.content_type)}

        response = requests.post(
            f"{SAGA_ORCHESTRATOR_URL}/upload",
            files=files,
            timeout=60
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Saga Orchestrator Error: {response.text}"
            )

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to Saga Orchestrator: {str(e)}"
        )