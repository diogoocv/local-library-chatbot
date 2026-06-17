from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Document Metadata Service")

# In-memory database to store Saga states
database = {}

class MetadataRequest(BaseModel):
    filename: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "document-metadata-service"}

@app.post("/metadata")
def create_metadata(request: MetadataRequest):
    document_id = f"doc_{len(database) + 1}"
    title = request.filename.rsplit(".", 1)[0]

    metadata = {
        "document_id": document_id,
        "filename": request.filename,
        "title": title,
        "status": "PROCESSING", # Initial Saga State
        "uploaded_at": datetime.utcnow().isoformat()
    }
    database[document_id] = metadata
    return metadata

@app.put("/metadata/{document_id}/complete")
def complete_metadata(document_id: str):
    if document_id in database:
        database[document_id]["status"] = "AVAILABLE" # Success State
        return database[document_id]
    raise HTTPException(status_code=404, detail="Document not found")

@app.delete("/metadata/{document_id}")
def rollback_metadata(document_id: str):
    if document_id in database:
        database[document_id]["status"] = "FAILED" # Compensating Transaction State
        return {"message": "Rollback successful. State marked as FAILED."}
    raise HTTPException(status_code=404, detail="Document not found")