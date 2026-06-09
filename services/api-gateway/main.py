from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
import requests

app = FastAPI(title="API Gateway")

SAGA_URL = "http://localhost:8006"
RAG_URL = "http://localhost:8004"


class QueryRequest(BaseModel):
    question: str
    limit: int = 5


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "api-gateway"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_content = await file.read()

        response = requests.post(
            f"{SAGA_URL}/upload",
            files={
                "file": (
                    file.filename,
                    file_content,
                    "application/pdf"
                )
            }
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/query")
def query(request: QueryRequest):
    try:
        response = requests.post(
            f"{RAG_URL}/query",
            json={
                "question": request.question,
                "limit": request.limit
            }
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )