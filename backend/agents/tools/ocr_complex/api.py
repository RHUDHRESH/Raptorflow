"""
FastAPI wrapper for OCR Complex.
Endpoints:
- GET /health
- POST /process (file upload)
- POST /batch (multiple files)
Explicit success/failure.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from .ocr_complex import OCRComplex

app = FastAPI(title="OCR Complex API", version="0.1.0")

# Instantiate with default config; override via env/config if desired
ocr = OCRComplex({})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    nlp: bool = Form(True),
    translate_to: str = Form(None),
):
    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        options: Dict[str, Any] = {"nlp": nlp}
        if translate_to:
            options["translate_to"] = translate_to

        result = ocr.process_document(tmp_path, options)
        Path(tmp_path).unlink(missing_ok=True)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.post("/batch")
async def process_batch(files: List[UploadFile] = File(...)):
    try:
        temp_paths = []
        for f in files:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(f.filename).suffix
            ) as tmp:
                tmp.write(await f.read())
                temp_paths.append(tmp.name)

        results = ocr.process_batch(temp_paths, options={"nlp": True})
        for p in temp_paths:
            Path(p).unlink(missing_ok=True)
        return JSONResponse(results)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
