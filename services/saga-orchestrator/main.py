from fastapi import FastAPI, File, HTTPException, UploadFile
import requests

app = FastAPI(title="Saga Orchestrator")

METADATA_SERVICE_URL = "http://localhost:8001"
TEXT_EXTRACTOR_URL = "http://localhost:8002"
VECTOR_DB_URL = "http://localhost:8003"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "saga-orchestrator"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        metadata_response = requests.post(
            f"{METADATA_SERVICE_URL}/metadata",
            json={
                "filename": file.filename
            }
        )

        metadata_response.raise_for_status()

        metadata = metadata_response.json()

        file_content = await file.read()

        extract_response = requests.post(
            f"{TEXT_EXTRACTOR_URL}/extract",
            files={
                "file": (
                    file.filename,
                    file_content,
                    "application/pdf"
                )
            }
        )

        extract_response.raise_for_status()

        extracted = extract_response.json()

        text = extracted.get("text", "").strip()

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document."
            )

        vector_response = requests.post(
            f"{VECTOR_DB_URL}/documents",
            json={
                "title": metadata["title"],
                "content": text
            }
        )

        vector_response.raise_for_status()

        vector_result = vector_response.json()

        return {
            "message": "Document successfully indexed.",
            "metadata": metadata,
            "vector_record": vector_result
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )