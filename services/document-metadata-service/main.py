from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Document Metadata Service")


class MetadataRequest(BaseModel):
    filename: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "document-metadata-service"
    }


@app.post("/metadata")
def create_metadata(request: MetadataRequest):
    filename = request.filename

    title = filename.rsplit(".", 1)[0]

    metadata = {
        "filename": filename,
        "title": title,
        "uploaded_at": datetime.utcnow().isoformat()
    }

    return metadata