from pathlib import Path
from uuid import uuid4

import chromadb
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Vector DB Service")

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_PATH = BASE_DIR / "data" / "chroma"

CHROMA_PATH.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_or_create_collection(
    name="documents"
)

model = SentenceTransformer("all-MiniLM-L6-v2")


class DocumentRequest(BaseModel):
    title: str
    content: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "vector-db-service"
    }


@app.post("/documents")
def add_document(request: DocumentRequest):
    embedding = model.encode(request.content).tolist()

    document_id = str(uuid4())

    collection.add(
        ids=[document_id],
        documents=[request.content],
        embeddings=[embedding],
        metadatas=[
            {
                "title": request.title
            }
        ]
    )

    return {
        "document_id": document_id,
        "title": request.title
    }


@app.post("/search")
def search(request: SearchRequest):
    query_embedding = model.encode(request.query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=request.limit
    )

    documents = []

    if results["documents"]:
        for index, document in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][index]

            documents.append(
                {
                    "title": metadata.get("title"),
                    "content": document
                }
            )

    return {
        "query": request.query,
        "results": documents
    }