from io import BytesIO

from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader

app = FastAPI(title="Text Extractor Service")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "text-extractor-service"
    }


@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    content = await file.read()

    reader = PdfReader(BytesIO(content))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    full_text = "\n".join(pages)

    return {
        "filename": file.filename,
        "text": full_text
    }