from io import BytesIO
from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader

app = FastAPI(title="Text Extractor Service")

def chunk_text(text, words_per_chunk=200):
    words = text.split()
    return [" ".join(words[i:i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]

@app.get("/health")
def health():
    return {"status": "ok", "service": "text-extractor-service"}

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
    chunks = chunk_text(full_text)

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "chunks": chunks
    }