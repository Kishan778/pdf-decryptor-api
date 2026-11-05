from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import io
import re
import pypdf

app = FastAPI(title="PDF Decryptor & Parser API")

class PDFRequest(BaseModel):
    file_base64: str
    password: str = ""

@app.get("/")
def home():
    return {"status": "running", "service": "PDF Decryptor API"}

@app.post("/extract-text")
def extract_text(payload: PDFRequest):
    try:
        pdf_bytes = base64.b64decode(payload.file_base64)
        stream = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(stream)

        # Encrypted PDF check
        if reader.is_encrypted:
            pwd = payload.password or "000003"
            res = reader.decrypt(pwd)
            if not res:
                raise HTTPException(status_code=400, detail="Invalid PDF password")

        extracted_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                extracted_text.append(t)

        full_text = "\n".join(extracted_text)
        return {
            "success": True, 
            "text": full_text,
            "pages": len(reader.pages)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
