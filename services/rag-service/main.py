from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="RAG Service")

VECTOR_DB_URL = "http://localhost:8003"


class QueryRequest(BaseModel):
    question: str
    limit: int = 5


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "rag-service"
    }


@app.post("/query")
def query_documents(request: QueryRequest):
    try:
        response = requests.post(
            f"{VECTOR_DB_URL}/search",
            json={
                "query": request.question,
                "limit": request.limit
            }
        )

        response.raise_for_status()

        results = response.json()

        context = []

        for item in results.get("results", []):
            context.append(
                {
                    "title": item["title"],
                    "content": item["content"]
                }
            )

        return {
            "question": request.question,
            "context": context
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )