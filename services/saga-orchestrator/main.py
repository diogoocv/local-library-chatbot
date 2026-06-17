from fastapi import FastAPI, File, HTTPException, UploadFile
import requests

app = FastAPI(title="Saga Orchestrator")

METADATA_SERVICE_URL = "http://localhost:8001"
TEXT_EXTRACTOR_URL = "http://localhost:8002"
VECTOR_DB_URL = "http://localhost:8003"

@app.get("/health")
def health():
    return {"status": "ok", "service": "saga-orchestrator"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    document_id = None
    try:
        # Save Metadata (State = PROCESSING)
        meta_res = requests.post(f"{METADATA_SERVICE_URL}/metadata", json={"filename": file.filename})
        meta_res.raise_for_status()
        metadata = meta_res.json()
        document_id = metadata["document_id"]

        # Extract Text and Chunk it
        file_content = await file.read()
        extract_res = requests.post(
            f"{TEXT_EXTRACTOR_URL}/extract",
            files={"file": (file.filename, file_content, "application/pdf")}
        )
        extract_res.raise_for_status()
        extracted = extract_res.json()
        chunks = extracted.get("chunks", [])

        if not chunks:
            raise ValueError("No text could be extracted.")

        # Save Vectors (Loop through the chunks)
        for chunk in chunks:
            vec_res = requests.post(
                f"{VECTOR_DB_URL}/documents",
                json={"title": metadata["title"], "content": chunk}
            )
            vec_res.raise_for_status()

        # Complete Saga (State -> AVAILABLE)
        requests.put(f"{METADATA_SERVICE_URL}/metadata/{document_id}/complete")

        return {
            "message": "Document successfully ingested via Saga.",
            "document_id": document_id,
            "chunks_saved": len(chunks)
        }

    except Exception as e:
        # COMPENSATING TRANSACTION: If anything fails, rollback the distributed state
        if document_id:
            try:
                requests.delete(f"{METADATA_SERVICE_URL}/metadata/{document_id}")
            except:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Saga Transaction Failed. Rollback executed. Error: {str(e)}"
        )