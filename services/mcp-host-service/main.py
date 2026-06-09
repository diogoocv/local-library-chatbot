from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Host Service")


class CollectionRequest(BaseModel):
    collection_name: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "mcp-host-service"
    }


@app.get("/tools")
def list_tools():
    return {
        "tools": [
            "list_collections",
            "list_documents",
            "search_documents"
        ]
    }


@app.get("/collections")
def list_collections():
    return {
        "collections": [
            {
                "id": "1",
                "name": "Distributed Systems"
            },
            {
                "id": "2",
                "name": "Artificial Intelligence"
            }
        ]
    }


@app.post("/documents")
def list_documents(request: CollectionRequest):
    mock_data = {
        "Distributed Systems": [
            "Microservices.pdf",
            "REST_APIs.pdf",
            "Middleware.pdf"
        ],
        "Artificial Intelligence": [
            "RAG.pdf",
            "MCP.pdf",
            "Embeddings.pdf"
        ]
    }

    return {
        "collection": request.collection_name,
        "documents": mock_data.get(
            request.collection_name,
            []
        )
    }


@app.get("/search")
def search_documents(query: str):
    documents = [
        "Microservices.pdf",
        "REST_APIs.pdf",
        "Middleware.pdf",
        "RAG.pdf",
        "MCP.pdf",
        "Embeddings.pdf"
    ]

    results = []

    for document in documents:
        if query.lower() in document.lower():
            results.append(document)

    return {
        "query": query,
        "results": results
    }